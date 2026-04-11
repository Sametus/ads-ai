import numpy as np
from pprint import pprint

from env import ACTION_KEYS, Env, STATE_KEYS, get_active_phase_id, get_phase_config


def build_raw_state(
    episode_id=1,
    step_id=1,
    distance=300.0,
    theta_deg=0.0,
    alpha_deg=0.0,
    beta_deg=0.0,
    closing_speed=0.0,
    agl=50.0,
    alt_error=0.0,
    rel_vel_ref=(0.0, 0.0, -10.0),
    turn_rate_ref=(0.0, 0.0, 0.0),
    forward_up_dot=0.0,
    grounded_flag=0.0,
):
    return {
        "episode_id": episode_id,
        "step_id": step_id,
        "states": {
            "distance": float(distance),
            "theta_rad": float(np.deg2rad(theta_deg)),
            "alpha_rad": float(np.deg2rad(alpha_deg)),
            "beta_rad": float(np.deg2rad(beta_deg)),
            "closing_speed": float(closing_speed),
            "rel_vel_ref": list(rel_vel_ref),
            "turn_rate_ref": list(turn_rate_ref),
            "forward_up_dot": float(forward_up_dot),
            "agl": float(agl),
            "alt_error": float(alt_error),
            "grounded_flag": float(grounded_flag),
        }
    }


class DummyEnv(Env):
    def __init__(self):
        self.connect = None
        self.done = False
        self.state_size = len(STATE_KEYS)
        self.action_size = len(ACTION_KEYS)
        self.phase_id = get_active_phase_id()
        self.phase = get_phase_config()
        self.max_step = int(self.phase["max_step"])
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None
        self.reset_distance = None
        self.prev_theta = None
        self.prev_alpha_abs = None
        self.prev_beta_abs = None

    def close(self):
        pass


def run_case(
    env,
    name,
    prev_distance,
    step_count,
    raw_state,
    prev_theta_deg=None,
    prev_alpha_abs=None,
    prev_beta_abs=None,
    denorm_action=None,
):
    env.prev_distance = prev_distance
    env.reset_distance = prev_distance
    env.step_count = step_count
    current_theta_deg = float(np.degrees(raw_state["states"]["theta_rad"]))
    current_alpha_abs = abs(float(np.degrees(raw_state["states"]["alpha_rad"])))
    current_beta_abs = abs(float(np.degrees(raw_state["states"]["beta_rad"])))
    env.prev_theta = max(0.0, current_theta_deg + 8.0) if prev_theta_deg is None else prev_theta_deg
    env.prev_alpha_abs = current_alpha_abs + 6.0 if prev_alpha_abs is None else prev_alpha_abs
    env.prev_beta_abs = current_beta_abs + 6.0 if prev_beta_abs is None else prev_beta_abs

    reward, done, info = env.calculate_reward(raw_state, denorm_action=denorm_action)

    print("=" * 80)
    print(f"CASE: {name}")
    print("-" * 80)
    print(f"phase_id       : {env.phase_id}")
    print(f"step_count     : {step_count}")
    print(f"prev_distance  : {prev_distance}")
    print(f"distance       : {raw_state['states']['distance']}")
    print(f"delta_distance : {prev_distance - raw_state['states']['distance']}")
    print(f"theta_deg      : {info['theta_deg']:.2f}")
    print(f"alpha_deg      : {info['alpha_deg']:.2f}")
    print(f"beta_deg       : {info['beta_deg']:.2f}")
    print(f"closing_speed  : {raw_state['states']['closing_speed']}")
    print(f"agl            : {raw_state['states']['agl']}")
    print(f"alt_error      : {raw_state['states']['alt_error']}")
    print(f"grounded_flag  : {raw_state['states']['grounded_flag']}")
    print("-" * 80)
    print(f"reward         : {reward:.4f}")
    print(f"done           : {done}")
    print(f"done_reason    : {info['done_reason']}")
    print(f"success        : {info['success']}")
    print(
        "reward_terms   : "
        f"dist={info['reward_distance']:.4f} | "
        f"align={info['reward_alignment']:.4f} | "
        f"close={info['reward_closing']:.4f} | "
        f"theta_prog={info['reward_theta_progress']:.4f} | "
        f"alpha_beta={info['reward_alpha_beta']:.4f} | "
        f"dir_bonus={info['reward_direction_bonus']:.4f} | "
        f"angle_focus={info['reward_angle_focus']:.4f} | "
        f"turn_toward={info['reward_turn_toward']:.4f} | "
        f"action_align={info['reward_action_alignment']:.4f} | "
        f"near_bonus={info['reward_near_success_bonus']:.4f} | "
        f"reverse_pen={info['reward_reverse_penalty']:.4f} | "
        f"roll_pen={info['reward_roll_penalty']:.4f} | "
        f"ang_pen={info['reward_angular_penalty']:.4f} | "
        f"alt={info['reward_altitude']:.4f} | "
        f"soft_floor={info['reward_soft_floor_penalty']:.4f} | "
        f"soft_ceiling={info['reward_soft_ceiling_penalty']:.4f} | "
        f"terminal={info['reward_terminal']:.4f}"
    )
    print("-" * 80)
    pprint(info)
    print()


def main():
    cases = [
        (DummyEnv(), "normal_approach", 290.0, 120, build_raw_state(
            distance=280.0,
            theta_deg=4.5,
            alpha_deg=3.0,
            beta_deg=1.0,
            closing_speed=18.0,
            agl=45.0,
            alt_error=5.0,
            turn_rate_ref=(0.1, 0.2, 0.1),
        )),
        (DummyEnv(), "high_altitude_with_good_progress", 210.0, 220, build_raw_state(
            distance=200.0,
            theta_deg=6.7,
            alpha_deg=5.5,
            beta_deg=1.5,
            closing_speed=20.0,
            agl=124.0,
            alt_error=8.0,
            turn_rate_ref=(0.1, 0.1, 0.1),
            forward_up_dot=0.4,
        )),
        (DummyEnv(), "low_altitude_terminal", 165.0, 80, build_raw_state(
            distance=160.0,
            theta_deg=13.4,
            alpha_deg=-10.0,
            beta_deg=4.0,
            closing_speed=8.0,
            agl=0.2,
            alt_error=40.0,
            turn_rate_ref=(0.2, 0.2, 0.2),
        )),
        (DummyEnv(), "collision_terminal", 55.0, 40, build_raw_state(
            distance=50.0,
            theta_deg=26.8,
            alpha_deg=-4.0,
            beta_deg=18.0,
            closing_speed=-5.0,
            agl=1.0,
            alt_error=20.0,
            turn_rate_ref=(0.3, 0.2, 0.1),
            grounded_flag=1.0,
        )),
        (DummyEnv(), "success_terminal", 15.0, 150, build_raw_state(
            distance=8.0,
            theta_deg=1.1,
            alpha_deg=0.3,
            beta_deg=-0.2,
            closing_speed=12.0,
            agl=48.0,
            alt_error=2.0,
            turn_rate_ref=(0.05, 0.05, 0.05),
        )),
        (DummyEnv(), "high_angular_velocity", 255.0, 100, build_raw_state(
            distance=250.0,
            theta_deg=16.9,
            alpha_deg=12.0,
            beta_deg=-6.0,
            closing_speed=10.0,
            agl=45.0,
            alt_error=10.0,
            turn_rate_ref=(5.0, 6.0, 4.0),
        )),
        (DummyEnv(), "approaching_but_misaligned", 240.0, 100, build_raw_state(
            distance=230.0,
            theta_deg=118.9,
            alpha_deg=30.0,
            beta_deg=-75.0,
            closing_speed=16.0,
            agl=50.0,
            alt_error=5.0,
            turn_rate_ref=(0.1, 0.1, 0.1),
        ), {
            "prev_theta_deg": 118.9,
            "prev_alpha_abs": 30.0,
            "prev_beta_abs": 75.0,
        }),
        (DummyEnv(), "turning_toward_axis_error", 210.0, 80, build_raw_state(
            distance=205.0,
            theta_deg=70.0,
            alpha_deg=45.0,
            beta_deg=-35.0,
            closing_speed=4.0,
            agl=55.0,
            alt_error=5.0,
            turn_rate_ref=(1.2, -1.0, 0.1),
        ), {
            "prev_theta_deg": 72.0,
            "prev_alpha_abs": 48.0,
            "prev_beta_abs": 38.0,
            "denorm_action": [850.0, 1.5, -1.2],
        }),
        (DummyEnv(), "turning_away_from_axis_error", 210.0, 80, build_raw_state(
            distance=205.0,
            theta_deg=70.0,
            alpha_deg=45.0,
            beta_deg=-35.0,
            closing_speed=4.0,
            agl=55.0,
            alt_error=5.0,
            turn_rate_ref=(-1.2, 1.0, 0.1),
        ), {
            "prev_theta_deg": 72.0,
            "prev_alpha_abs": 48.0,
            "prev_beta_abs": 38.0,
            "denorm_action": [850.0, -1.5, 1.2],
        }),
        (DummyEnv(), "perfect_but_no_progress", 300.0, 100, build_raw_state(
            distance=300.0,
            theta_deg=0.0,
            closing_speed=0.0,
            agl=45.0,
            alt_error=0.0,
        ), {
            "prev_theta_deg": 0.0,
            "prev_alpha_abs": 0.0,
            "prev_beta_abs": 0.0,
        }),
        (DummyEnv(), "wrong_way_terminal", 130.0, 90, build_raw_state(
            distance=150.0,
            theta_deg=146.0,
            alpha_deg=18.0,
            beta_deg=-72.0,
            closing_speed=-20.0,
            agl=60.0,
            alt_error=15.0,
            rel_vel_ref=(12.0, 4.0, 15.0),
            turn_rate_ref=(0.2, 0.3, 0.4),
        )),
        (DummyEnv(), "success_blocked_by_bad_alignment", 13.0, 120, build_raw_state(
            distance=11.5,
            theta_deg=82.4,
            alpha_deg=30.0,
            beta_deg=50.0,
            closing_speed=1.0,
            agl=45.0,
            alt_error=0.0,
        )),
        (DummyEnv(), "timeout_terminal", 50.0, 700, build_raw_state(
            distance=40.0,
            theta_deg=3.2,
            alpha_deg=1.4,
            beta_deg=-0.7,
            closing_speed=15.0,
            agl=45.0,
            alt_error=0.0,
        )),
    ]

    for case in cases:
        env, name, prev_distance, step_count, raw_state, *rest = case
        overrides = rest[0] if rest else {}
        run_case(env, name, prev_distance, step_count, raw_state, **overrides)


if __name__ == "__main__":
    main()
