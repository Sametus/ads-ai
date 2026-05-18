import argparse

import settings
from env import Env
from sac_agent import ReplayBuffer, SACAgent


def collect_episode(env, agent, offset, radius, target_y, max_steps, deterministic):
    """Run one real Unity episode and keep transitions in memory until result is known."""
    _, _, state, start_info = env.reset_with_config(
        radius,
        radius,
        float(offset),
        float(offset),
        heading_offset_abs_min=0.0,
        target_y=target_y,
    )

    transitions = []
    episode_return = 0.0
    final_info = start_info

    for _ in range(int(max_steps)):
        action, _ = agent.act(state, deterministic=deterministic)
        next_state, reward, done, info = env.step(action)

        transitions.append((state.copy(), action.copy(), float(reward), next_state.copy(), bool(done)))
        episode_return += float(reward)
        final_info = info
        state = next_state

        if done:
            break

    return {
        "offset": int(offset),
        "done_reason": final_info.get("done_reason", "not_done"),
        "hit": 1 if float(final_info.get("target_hit_trigger", 0.0) or 0.0) > 0.5 else 0,
        "ellipsoid": 1 if float(final_info.get("target_hit_ellipsoid", 0.0) or 0.0) > 0.5 else 0,
        "ellipsoid_value": float(final_info.get("target_hit_ellipsoid_value", 0.0) or 0.0),
        "steps": int(final_info.get("step_id", len(transitions))),
        "return": float(episode_return),
        "distance": float(final_info.get("distance", 0.0)),
        "theta": float(final_info.get("theta_deg", 0.0)),
        "closing": float(final_info.get("closing_speed", 0.0)),
        "transitions": transitions,
    }


def add_transitions(replay, transitions):
    for state, action, reward, next_state, done in transitions:
        replay.add(state, action, reward, next_state, done)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Collect real Unity rollouts from the current SAC policy and append successful "
            "transitions to the replay buffer."
        )
    )
    parser.add_argument("--offsets", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    parser.add_argument("--successes-per-offset", type=int, default=5)
    parser.add_argument("--max-attempts-per-offset", type=int, default=12)
    parser.add_argument("--radius", type=float, default=700.0)
    parser.add_argument("--target-y", type=float, default=100.0)
    parser.add_argument("--max-steps", type=int, default=1200)
    parser.add_argument("--stochastic", action="store_true")
    parser.add_argument(
        "--checkpoint-step",
        type=int,
        default=None,
        help="Belirli bir SAC checkpoint step'i ile rollout toplar; verilmezse en son checkpoint yuklenir.",
    )
    parser.add_argument(
        "--checkpoint-prefix",
        default=None,
        help="Checkpoint prefix'i; verilmezse settings.SAC_MODEL_PREFIX kullanilir.",
    )
    parser.add_argument(
        "--keep-failures",
        action="store_true",
        help="Also append failed episodes. Default is to append successes only.",
    )
    args = parser.parse_args()

    settings.setup_gpu()
    settings.ensure_model_dir()

    agent = SACAgent()
    if args.checkpoint_step is not None:
        checkpoint_prefix = args.checkpoint_prefix or settings.SAC_MODEL_PREFIX
        agent.load_model_weights(int(args.checkpoint_step), checkpoint_prefix)
        agent.loaded_checkpoint = True
        loaded_step = int(args.checkpoint_step)
        print(
            f"[SAC ROLLOUT] Secilen checkpoint yuklendi: "
            f"prefix={checkpoint_prefix} step={loaded_step}",
            flush=True,
        )
    else:
        loaded_step = agent.load_checkpoint()
        if loaded_step == 0 and not agent.loaded_checkpoint:
            raise FileNotFoundError("SAC checkpoint bulunamadi; rollout toplanamiyor.")

    replay = ReplayBuffer(agent.state_size, agent.action_size, settings.SAC_REPLAY_SIZE)
    replay_path = agent.replay_buffer_path()
    replay_step = replay.load(replay_path)
    if replay_step is None:
        print("[ROLLOUT] Kayitli replay buffer yok; yeni buffer olusturulacak.", flush=True)
    else:
        print(
            f"[ROLLOUT] Replay buffer yuklendi: file_step={replay_step} "
            f"size={replay.size} ptr={replay.ptr}",
            flush=True,
        )

    deterministic = not bool(args.stochastic)
    env = Env(settings.IP, settings.PORT)
    total_added = 0
    total_success = 0
    total_attempts = 0

    try:
        print(
            f"[ROLLOUT] sac_step={loaded_step} deterministic={deterministic} "
            f"offsets={args.offsets} target_successes={args.successes_per_offset}",
            flush=True,
        )
        for offset in args.offsets:
            offset_success = 0
            offset_attempts = 0
            while (
                offset_success < int(args.successes_per_offset)
                and offset_attempts < int(args.max_attempts_per_offset)
            ):
                offset_attempts += 1
                total_attempts += 1
                result = collect_episode(
                    env,
                    agent,
                    offset,
                    args.radius,
                    args.target_y,
                    args.max_steps,
                    deterministic,
                )

                is_success = result["done_reason"] == "success"
                should_add = is_success or bool(args.keep_failures)
                if should_add:
                    add_transitions(replay, result["transitions"])
                    total_added += len(result["transitions"])

                if is_success:
                    offset_success += 1
                    total_success += 1

                print(
                    "[ROLLOUT] offset={offset:+d} attempt={attempt}/{max_attempts} "
                    "successes={successes}/{target} done={done} steps={steps} "
                    "hit={hit} ell={ellipsoid}/{ellipsoid_value:.2f} "
                    "return={ret:.2f} dist={dist:.2f} theta={theta:.1f} "
                    "closing={closing:.1f} added={added}".format(
                        offset=int(offset),
                        attempt=offset_attempts,
                        max_attempts=int(args.max_attempts_per_offset),
                        successes=offset_success,
                        target=int(args.successes_per_offset),
                        done=result["done_reason"],
                        steps=result["steps"],
                        ret=result["return"],
                        dist=result["distance"],
                        theta=result["theta"],
                        closing=result["closing"],
                        added=len(result["transitions"]) if should_add else 0,
                    ),
                    flush=True,
                )

            if offset_success < int(args.successes_per_offset):
                print(
                    f"[ROLLOUT WARN] offset={offset:+d}: hedeflenen success sayisina ulasilamadi "
                    f"({offset_success}/{args.successes_per_offset}).",
                    flush=True,
                )
    finally:
        env.close()

    replay.save(replay_path, loaded_step)
    print(
        f"[ROLLOUT SAVE] replay_path={replay_path} checkpoint_step={loaded_step} "
        f"attempts={total_attempts} successes={total_success} "
        f"added_transitions={total_added} final_size={replay.size} ptr={replay.ptr}",
        flush=True,
    )


if __name__ == "__main__":
    main()
