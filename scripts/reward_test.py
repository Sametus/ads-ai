import copy
import numpy as np
from pprint import pprint

# KENDİ env.py DOSYANDAN IMPORT ET
from env import Env


def build_raw_state(
    episode_id=1,
    step_id=1,
    distance=300.0,
    closing_rate=10.0,
    roc_h=50.0,
    height_error=0.0,
    target_dir=(0.0, 0.0, 1.0),
    rel_vel=(0.0, 0.0, -10.0),
    roc_vel=(0.0, 0.0, 20.0),
    roc_ang_vel=(0.0, 0.0, 0.0),
    g=(0.0, -9.81, 0.0),
    blend_w=0.0,
):
    return {
        "episode_id": episode_id,
        "step_id": step_id,
        "states": {
            "target_dir": list(target_dir),
            "rel_vel": list(rel_vel),
            "roc_vel": list(roc_vel),
            "roc_ang_vel": list(roc_ang_vel),
            "roc_h": float(roc_h),
            "height_error": float(height_error),
            "g": list(g),
            "distance": float(distance),
            "closing_rate": float(closing_rate),
            "blend_w": float(blend_w),
        }
    }


class DummyEnv(Env):
    """
    Gerçek TCP bağlantısı açmamak için Env'i override ediyoruz.
    Sadece reward test edeceğiz.
    """
    def __init__(self):
        self.connect = None
        self.done = False
        self.state_size = 20
        self.action_size = 3
        self.max_step = 1300
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None
        self.reset_distance = None

    def close(self):
        pass


def run_case(env, name, prev_distance, step_count, reset_distance, raw_state):
    env.prev_distance = prev_distance
    env.step_count = step_count
    env.reset_distance = reset_distance

    reward, done, info = env.calculate_reward(raw_state)

    print("=" * 80)
    print(f"CASE: {name}")
    print("-" * 80)
    print(f"step_count     : {step_count}")
    print(f"prev_distance  : {prev_distance}")
    print(f"distance       : {raw_state['states']['distance']}")
    print(f"delta_distance : {prev_distance - raw_state['states']['distance']}")
    print(f"closing_rate   : {raw_state['states']['closing_rate']}")
    print(f"roc_h          : {raw_state['states']['roc_h']}")
    print(f"height_error   : {raw_state['states']['height_error']}")
    print(f"target_dir_z   : {raw_state['states']['target_dir'][2]}")
    print(f"blend_w        : {raw_state['states']['blend_w']}")
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

    # 1) Normal yaklaşma
    raw = build_raw_state(
        distance=280.0,
        closing_rate=18.0,
        roc_h=45.0,
        height_error=5.0,
        target_dir=(0.0, 0.0, 0.95),
        roc_ang_vel=(0.1, 0.2, 0.1),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="normal_approach",
        prev_distance=290.0,
        step_count=120,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 2) High altitude ama yaklaşma da var
    raw = build_raw_state(
        distance=200.0,
        closing_rate=20.0,
        roc_h=110.0,
        height_error=60.0,
        target_dir=(0.0, 0.0, 0.9),
        roc_ang_vel=(0.1, 0.1, 0.1),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="high_altitude_with_good_progress",
        prev_distance=210.0,
        step_count=220,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 3) Low altitude
    raw = build_raw_state(
        distance=160.0,
        closing_rate=8.0,
        roc_h=0.2,
        height_error=40.0,
        target_dir=(0.0, 0.0, 0.8),
        roc_ang_vel=(0.2, 0.2, 0.2),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="low_altitude_terminal",
        prev_distance=165.0,
        step_count=80,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 4) Collision
    raw = build_raw_state(
        distance=50.0,
        closing_rate=-5.0,
        roc_h=1.0,
        height_error=20.0,
        target_dir=(0.0, 0.0, 0.4),
        roc_ang_vel=(0.3, 0.2, 0.1),
        blend_w=1.0,
    )
    run_case(
        env=env,
        name="collision_terminal",
        prev_distance=55.0,
        step_count=40,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 5) Success
    raw = build_raw_state(
        distance=8.0,
        closing_rate=12.0,
        roc_h=48.0,
        height_error=2.0,
        target_dir=(0.0, 0.0, 0.99),
        roc_ang_vel=(0.05, 0.05, 0.05),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="success_terminal",
        prev_distance=15.0,
        step_count=150,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 6) Escaped
    raw = build_raw_state(
        distance=430.0,
        closing_rate=-20.0,
        roc_h=40.0,
        height_error=15.0,
        target_dir=(0.0, 0.0, -0.3),
        roc_ang_vel=(0.2, 0.2, 0.2),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="escaped_terminal",
        prev_distance=420.0,
        step_count=300,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 7) Takla / yüksek açısal hız
    raw = build_raw_state(
        distance=250.0,
        closing_rate=10.0,
        roc_h=45.0,
        height_error=10.0,
        target_dir=(0.0, 0.0, 0.7),
        roc_ang_vel=(5.0, 6.0, 4.0),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="high_angular_velocity",
        prev_distance=255.0,
        step_count=100,
        reset_distance=300.0,
        raw_state=raw,
    )

    # 8) Hizasız ama yaklaşan
    raw = build_raw_state(
        distance=230.0,
        closing_rate=16.0,
        roc_h=50.0,
        height_error=5.0,
        target_dir=(0.0, 0.0, -0.4),
        roc_ang_vel=(0.1, 0.1, 0.1),
        blend_w=0.0,
    )
    run_case(
        env=env,
        name="approaching_but_misaligned",
        prev_distance=240.0,
        step_count=100,
        reset_distance=300.0,
        raw_state=raw,
    )


if __name__ == "__main__":
    main()