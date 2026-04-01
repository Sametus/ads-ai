import numpy as np
from pprint import pprint

from env import Env


def build_raw_state(
    episode_id=1,
    step_id=1,
    distance=300.0,
    closing_speed=0.0,
    los_yaw_deg=0.0,
    los_pitch_deg=0.0,
    agl=50.0,
    alt_error=0.0,
    rel_vel=(0.0, 0.0, -10.0),
    roc_ang_vel=(0.0, 0.0, 0.0),
    g=(0.0, -9.81, 0.0),
    grounded_flag=0.0,
):
    los_yaw_rad = np.deg2rad(los_yaw_deg)
    los_pitch_rad = np.deg2rad(los_pitch_deg)

    return {
        "episode_id": episode_id,
        "step_id": step_id,
        "states": {
            "los_yaw_sin": float(np.sin(los_yaw_rad)),
            "los_yaw_cos": float(np.cos(los_yaw_rad)),
            "los_pitch_sin": float(np.sin(los_pitch_rad)),
            "los_pitch_cos": float(np.cos(los_pitch_rad)),
            "distance": float(distance),
            "closing_speed": float(closing_speed),
            "rel_vel": list(rel_vel),
            "roc_ang_vel": list(roc_ang_vel),
            "g": list(g),
            "agl": float(agl),
            "alt_error": float(alt_error),
            "grounded_flag": float(grounded_flag),
        }
    }


class DummyEnv(Env):
    def __init__(self):
        self.connect = None
        self.done = False
        self.state_size = 18
        self.action_size = 3
        self.max_step = 255
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None
        self.reset_distance = None

    def close(self):
        pass


def run_case(env, name, prev_distance, step_count, raw_state):
    env.prev_distance = prev_distance
    env.step_count = step_count

    reward, done, info = env.calculate_reward(raw_state)

    print("=" * 80)
    print(f"CASE: {name}")
    print("-" * 80)
    print(f"step_count     : {step_count}")
    print(f"prev_distance  : {prev_distance}")
    print(f"distance       : {raw_state['states']['distance']}")
    print(f"delta_distance : {prev_distance - raw_state['states']['distance']}")
    print(f"closing_speed  : {raw_state['states']['closing_speed']}")
    print(f"los_yaw_deg    : {info['los_yaw_deg']:.2f}")
    print(f"los_pitch_deg  : {info['los_pitch_deg']:.2f}")
    print(f"agl            : {raw_state['states']['agl']}")
    print(f"alt_error      : {raw_state['states']['alt_error']}")
    print(f"grounded_flag  : {raw_state['states']['grounded_flag']}")
    print("-" * 80)
    print(f"reward         : {reward:.4f}")
    print(f"done           : {done}")
    print(f"done_reason    : {info['done_reason']}")
    print(f"success        : {info['success']}")
    print("-" * 80)
    pprint(info)
    print()


def main():
    env = DummyEnv()

    cases = [
        ("normal_approach", 290.0, 120, build_raw_state(
            distance=280.0,
            closing_speed=18.0,
            los_yaw_deg=4.0,
            los_pitch_deg=-2.0,
            agl=45.0,
            alt_error=5.0,
            roc_ang_vel=(0.1, 0.2, 0.1),
        )),
        ("high_altitude_with_good_progress", 210.0, 220, build_raw_state(
            distance=200.0,
            closing_speed=20.0,
            los_yaw_deg=6.0,
            los_pitch_deg=-3.0,
            agl=110.0,
            alt_error=8.0,
            roc_ang_vel=(0.1, 0.1, 0.1),
        )),
        ("low_altitude_terminal", 165.0, 80, build_raw_state(
            distance=160.0,
            closing_speed=8.0,
            los_yaw_deg=12.0,
            los_pitch_deg=-6.0,
            agl=0.2,
            alt_error=40.0,
            roc_ang_vel=(0.2, 0.2, 0.2),
        )),
        ("collision_terminal", 55.0, 40, build_raw_state(
            distance=50.0,
            closing_speed=-5.0,
            los_yaw_deg=25.0,
            los_pitch_deg=10.0,
            agl=1.0,
            alt_error=20.0,
            roc_ang_vel=(0.3, 0.2, 0.1),
            grounded_flag=1.0,
        )),
        ("success_terminal", 15.0, 150, build_raw_state(
            distance=8.0,
            closing_speed=12.0,
            los_yaw_deg=1.0,
            los_pitch_deg=0.5,
            agl=48.0,
            alt_error=2.0,
            roc_ang_vel=(0.05, 0.05, 0.05),
        )),
        ("high_angular_velocity", 255.0, 100, build_raw_state(
            distance=250.0,
            closing_speed=10.0,
            los_yaw_deg=15.0,
            los_pitch_deg=-8.0,
            agl=45.0,
            alt_error=10.0,
            roc_ang_vel=(5.0, 6.0, 4.0),
        )),
        ("approaching_but_misaligned", 240.0, 100, build_raw_state(
            distance=230.0,
            closing_speed=16.0,
            los_yaw_deg=120.0,
            los_pitch_deg=15.0,
            agl=50.0,
            alt_error=5.0,
            roc_ang_vel=(0.1, 0.1, 0.1),
        )),
    ]

    for name, prev_distance, step_count, raw_state in cases:
        run_case(env, name, prev_distance, step_count, raw_state)


if __name__ == "__main__":
    main()
