import numpy as np

import settings
from env import Env
from sac_agent import SACAgent


FINAL_TEST_PREFIX = "sac_v16_0_7_forward_speed_y100"
FINAL_TEST_STEP = 845000
DETERMINISTIC_POLICY = True
STEP_PRINT_EVERY = 200


def hit_text(info):
    trigger_hit = float(info.get("target_hit_trigger", 0.0) or 0.0) > 0.5
    ellipsoid_hit = float(info.get("target_hit_ellipsoid", 0.0) or 0.0) > 0.5
    ellipsoid_value = float(info.get("target_hit_ellipsoid_value", 0.0) or 0.0)
    return f"hit={'VAR' if trigger_hit else 'YOK'} ell={int(ellipsoid_hit)}/{ellipsoid_value:.2f}"


def main():
    settings.setup_gpu()
    settings.ensure_model_dir()

    env = Env(settings.IP, settings.PORT)
    agent = SACAgent()
    agent.load_model_weights(FINAL_TEST_STEP, FINAL_TEST_PREFIX)

    total_episodes = 0
    success_count = 0
    returns = []
    lengths = []

    print("=" * 88)
    print(
        "[FINAL TEST] "
        f"prefix={FINAL_TEST_PREFIX} step={FINAL_TEST_STEP} "
        f"deterministic={DETERMINISTIC_POLICY}"
    )
    print("Ctrl+C ile durdurabilirsin.")

    try:
        while True:
            _, _, state, start_info = env.reset()
            episode_id = env.episode_id
            episode_return = 0.0
            episode_len = 0
            done = False
            final_info = None

            print("-" * 88)
            print(
                f"[RESET] ep={episode_id} "
                f"offset={start_info.get('reset_heading_offset', 0.0):+.1f} "
                f"miss={start_info.get('reset_target_miss_distance', 0.0):.1f}m "
                f"target=({start_info['reset_px']:.1f}, {start_info['reset_py']:.1f}, {start_info['reset_pz']:.1f})"
            )

            while not done:
                action, _ = agent.act(state, deterministic=DETERMINISTIC_POLICY)
                next_state, reward, done, info = env.step(action)

                episode_return += reward
                episode_len += 1
                final_info = info

                if info["step_id"] % STEP_PRINT_EVERY == 0:
                    print(
                        f"[RUN] ep={episode_id} st={info['step_id']} "
                        f"dist={info.get('target_distance', info['distance']):.1f}m "
                        f"agl={info['agl']:.1f}m theta={info.get('theta_deg', 0.0):.1f} "
                        f"closing={info.get('closing_speed', 0.0):.1f}"
                    )

                state = next_state

            total_episodes += 1
            done_reason = final_info.get("done_reason", "unknown") if final_info else "unknown"
            if done_reason == "success":
                success_count += 1

            returns.append(float(episode_return))
            lengths.append(int(episode_len))
            success_rate = 100.0 * success_count / max(total_episodes, 1)
            status = "SUCCESS" if done_reason == "success" else done_reason.upper()

            print(
                f"[END] {status:<16} ep={episode_id} "
                f"len={episode_len} return={episode_return:.1f} "
                f"target_dist={final_info.get('target_distance', final_info['distance']):.1f}m "
                f"agl={final_info['agl']:.1f}m theta={final_info.get('theta_deg', 0.0):.1f} "
                f"{hit_text(final_info)} | "
                f"success={success_count}/{total_episodes} ({success_rate:.1f}%)"
            )

    except KeyboardInterrupt:
        print("\n" + "=" * 88)
        print("[FINAL TEST STOPPED]")
        print(f"Episodes     : {total_episodes}")
        print(f"Success      : {success_count}")
        if total_episodes:
            print(f"Success Rate : {100.0 * success_count / total_episodes:.2f}%")
            print(f"Mean Return  : {float(np.mean(returns)):.2f}")
            print(f"Mean Length  : {float(np.mean(lengths)):.1f}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
