import numpy as np

import settings
from env import Env
from sac_agent import SACAgent

TEST_EPISODES = 5
STEP_PRINT_EVERY = 50
DETERMINISTIC_POLICY = True


if __name__ == "__main__":
    settings.setup_gpu()
    settings.ensure_model_dir()

    env = Env(settings.IP, settings.PORT)
    agent = SACAgent()
    loaded_step = agent.load_checkpoint()

    if loaded_step == 0 and not agent.loaded_checkpoint:
        raise FileNotFoundError(
            "Test icin SAC checkpoint bulunamadi. Once scripts\\train.py ile egitim baslat."
        )

    total_returns = []
    total_lengths = []
    success_count = 0

    try:
        for ep in range(1, TEST_EPISODES + 1):
            _, _, state, start_info = env.reset()
            episode_id = env.episode_id

            ep_return = 0.0
            ep_len = 0
            done = False
            final_info = None

            print("=" * 80)
            print(
                f"[TEST EP {ep}/{TEST_EPISODES}] "
                f"episode_id={episode_id} | "
                f"sac_step={loaded_step}"
            )
            print(
                f"[RESET] Target Pos=({start_info['reset_px']:.2f}, "
                f"{start_info['reset_py']:.2f}, {start_info['reset_pz']:.2f}) | "
                f"Rot=({start_info['reset_ry']:.2f}, {start_info['reset_rz']:.2f}) | "
                f"HeadingOffset={start_info['reset_heading_offset']:.2f}"
            )

            while not done:
                action, _ = agent.act(state, deterministic=DETERMINISTIC_POLICY)
                next_state, reward, done, info = env.step(action)

                ep_return += reward
                ep_len += 1
                final_info = info

                if info["step_id"] % STEP_PRINT_EVERY == 0:
                    print(
                        f"[EP {episode_id:<4} | ST {info['step_id']:<4}] "
                        f"Dst={info['distance']:.2f} | "
                        f"Theta={info['theta_deg']:.2f}deg | "
                        f"Cls={info['closing_speed']:.2f} | "
                        f"AGL={info['agl']:.2f} | "
                        f"R={reward:.3f} | "
                        f"Action=[{action[0]:.3f}, {action[1]:.3f}, {action[2]:.3f}] | "
                        f"Mode={info.get('turn_direction_name', 'n/a')} | "
                        f"Acc=[{info.get('direct_accel_world_x', 0.0):.1f}, "
                        f"{info.get('direct_accel_world_y', 0.0):.1f}, "
                        f"{info.get('direct_accel_world_z', 0.0):.1f}]"
                    )

                state = next_state

            done_reason = final_info["done_reason"] if final_info is not None else "unknown"
            target_hit = float(final_info.get("target_hit_trigger", 0.0) or 0.0) > 0.5
            ellipsoid_hit = float(final_info.get("target_hit_ellipsoid", 0.0) or 0.0) > 0.5
            ellipsoid_value = float(final_info.get("target_hit_ellipsoid_value", 0.0) or 0.0)
            if done_reason == "success":
                success_count += 1

            total_returns.append(ep_return)
            total_lengths.append(ep_len)

            print("-" * 80)
            print(
                f"[EPISODE END] "
                f"episode_id={episode_id} | "
                f"done_reason={done_reason} | "
                f"return={ep_return:.3f} | "
                f"len={ep_len} | "
                f"final_distance={final_info['distance']:.2f} | "
                f"final_agl={final_info['agl']:.2f} | "
                f"final_theta={final_info.get('theta_deg', 0.0):.2f} | "
                f"final_alignment={final_info.get('alignment', 0.0):.2f} | "
                f"hit={'VAR' if target_hit else 'YOK'} | "
                f"ellipsoid={int(ellipsoid_hit)}/{ellipsoid_value:.2f}"
            )

        print("=" * 80)
        print("[TEST SUMMARY]")
        print(f"SAC Step           : {loaded_step}")
        print(f"Episode Count      : {TEST_EPISODES}")
        print(f"Deterministic Mode : {DETERMINISTIC_POLICY}")
        print(f"Success Count      : {success_count}")
        print(f"Success Rate       : {100.0 * success_count / TEST_EPISODES:.2f}%")
        print(f"Mean Return        : {np.mean(total_returns):.3f}")
        print(f"Std Return         : {np.std(total_returns):.3f}")
        print(f"Mean Episode Len   : {np.mean(total_lengths):.2f}")

    finally:
        env.close()
