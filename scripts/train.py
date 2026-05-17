import log
import settings
from env import Env
from sac_agent import ReplayBuffer, SACAgent


def sac_update_id(global_step):
    """CSV loglar update_id bekledigi icin SAC global step'i okunur hale getirir."""
    return max(1, int(global_step))


if __name__ == "__main__":
    settings.setup_gpu()
    settings.ensure_model_dir()
    log.ensure_log_files()

    agent = SACAgent()
    start_step = agent.load_checkpoint()
    if start_step == 0:
        print("[SAC] Checkpoint yok; egitim sifirdan basliyor.")

    env = Env(settings.IP, settings.PORT)
    replay = ReplayBuffer(agent.state_size, agent.action_size, settings.SAC_REPLAY_SIZE)
    load_replay_buffer = bool(getattr(
        settings,
        "SAC_LOAD_REPLAY_BUFFER",
        getattr(settings, "SAC_SAVE_REPLAY_BUFFER", False),
    ))
    if load_replay_buffer:
        try:
            replay_step = replay.load(agent.replay_buffer_path())
            if replay_step is not None:
                print(
                    f"[SAC REPLAY] Replay buffer yuklendi: step {replay_step}, "
                    f"size={replay.size}, ptr={replay.ptr}."
                )
            else:
                print("[SAC REPLAY] Kayitli replay buffer yok; buffer yeniden dolacak.")
        except Exception as exc:
            print(f"[SAC REPLAY] Replay buffer yuklenemedi: {exc}. Buffer yeniden dolacak.")

    episode_return = 0.0
    episode_len = 0
    total_episode_count, total_success_count = log.load_success_counters()
    _, _, state, start_info = env.reset()
    episode_id = env.episode_id
    log.print_reset_console(episode_id, start_info)

    last_train_logs = {
        "loss": 0.0,
        "policy_loss": 0.0,
        "value_loss": 0.0,
        "entropy": 0.0,
        "kl": 0.0,
        "clip_frac": float(agent.alpha.numpy()),
        "alpha": float(agent.alpha.numpy()),
    }
    has_trained = start_step >= int(settings.SAC_START_TRAINING_STEPS)
    last_global_step = int(start_step)

    def save_progress(reason, step_id):
        step_id = max(0, int(step_id))
        if has_trained:
            print(f"[SAC SAVE] {reason}: step {step_id}: checkpoint kaydediliyor.")
            agent.save_checkpoint(step_id)
        else:
            print(
                f"[SAC SAVE SKIP] {reason}: step {step_id}: "
                "checkpoint icin replay warmup henuz bitmedi."
            )

        if bool(getattr(settings, "SAC_SAVE_REPLAY_BUFFER", False)) and replay.size > 0:
            replay.save(agent.replay_buffer_path(), step_id)
            print(
                f"[SAC REPLAY SAVE] {reason}: step {step_id}: "
                f"size={replay.size}, ptr={replay.ptr}."
            )
        elif bool(getattr(settings, "SAC_SAVE_REPLAY_BUFFER", False)):
            print(f"[SAC REPLAY SAVE SKIP] {reason}: kaydedilecek transition yok.")

    completed = False
    try:
        for global_step in range(start_step, int(settings.SAC_TOTAL_STEPS)):
            last_global_step = global_step + 1
            # Hazir baslangic yok: action ilk step'ten itibaren sifirdan baslayan SAC actor'unden gelir.
            action, action_logp = agent.act(state, deterministic=False)
            next_state, reward, done, info = env.step(action)

            replay.add(state, action, reward, next_state, done)
            if bool(getattr(settings, "SAC_RIGHT_MIRROR_AUGMENTATION", False)):
                replay.add_right_mirror(state, action, reward, next_state, done)

            episode_return += reward
            episode_len += 1

            info["episode_return_so_far"] = float(episode_return)
            info["action_logp"] = float(action_logp)
            info["value_pred"] = 0.0
            info["action_source"] = "sac_policy"
            for action_index, action_value in enumerate(action):
                info[f"action_norm_{action_index}"] = float(action_value)
            info["action_direction_id"] = -1
            info["action_direction_clock12"] = float(info.get("action_direction_clock12", 0.0))
            info["action_direction_clock3"] = float(info.get("action_direction_clock3", 0.0))

            log.append_step_csv(sac_update_id(global_step + 1), info)

            if info["step_id"] % log.STEP_PRINT_EVERY == 0:
                log.print_step_console(sac_update_id(global_step + 1), info)

            should_train = (
                replay.size >= int(settings.SAC_START_TRAINING_STEPS)
                and (global_step + 1) % int(settings.SAC_TRAIN_EVERY_STEPS) == 0
            )
            if should_train:
                for _ in range(int(settings.SAC_UPDATES_PER_STEP)):
                    last_train_logs = agent.train_step(replay, settings.SAC_BATCH_SIZE)
                has_trained = True

            if (global_step + 1) % int(settings.SAC_LOG_EVERY_STEPS) == 0:
                log.append_update_csv(
                    sac_update_id(global_step + 1),
                    last_train_logs,
                    agent.gamma,
                    0.0,
                    settings.SAC_ACTOR_LR,
                )
                print(
                    "[SAC STEP {step}] loss={loss:.4f} actor={actor:.4f} "
                    "q={q:.4f} ent={ent:.4f} alpha={alpha:.4f} buffer={buffer}".format(
                        step=global_step + 1,
                        loss=last_train_logs.get("loss", 0.0),
                        actor=last_train_logs.get("policy_loss", 0.0),
                        q=last_train_logs.get("value_loss", 0.0),
                        ent=last_train_logs.get("entropy", 0.0),
                        alpha=last_train_logs.get("alpha", agent.alpha.numpy()),
                        buffer=replay.size,
                    ),
                    flush=True,
                )

            if (global_step + 1) % int(settings.SAC_SAVE_EVERY_STEPS) == 0:
                save_progress("periodic", global_step + 1)

            if done:
                total_episode_count += 1
                if info["done_reason"] == "success":
                    total_success_count += 1

                log.append_episode_csv(
                    sac_update_id(global_step + 1),
                    episode_id,
                    episode_return,
                    episode_len,
                    info["done_reason"],
                    start_info,
                    info,
                )
                log.print_episode_console(
                    episode_id,
                    episode_return,
                    episode_len,
                    info["done_reason"],
                    start_info,
                    info,
                    total_success_count,
                    total_episode_count,
                )

                episode_return = 0.0
                episode_len = 0
                _, _, state, start_info = env.reset()
                episode_id = env.episode_id
                log.print_reset_console(episode_id, start_info)
            else:
                state = next_state

        completed = True
    except KeyboardInterrupt:
        print("\n[SAC INTERRUPT] Egitim kesildi; replay buffer ve mumkunse checkpoint kaydediliyor.")
        save_progress("interrupt", last_global_step)
    finally:
        if completed:
            print("[SAC FINAL SAVE] Egitim tamamlandi; son durum kaydediliyor.")
            save_progress("final", settings.SAC_TOTAL_STEPS)
        env.close()
