from datetime import datetime

import connector
import numpy as np

STATE_KEYS = [
    "distance",
    "theta_rad",
    "alpha_rad",
    "beta_rad",
    "closing_speed",
    "rel_vel_right",
    "rel_vel_up",
    "rel_vel_forward",
    "turn_rate_vertical",
    "turn_rate_horizontal",
    "turn_rate_roll",
    "forward_up_dot",
    "agl",
    "alt_error",
]

ACTION_KEYS = ["thrust", "vertical_cmd", "horizontal_cmd"]

PYTHON_STEP_LOG_KEYS = [
    "episode_return_so_far",
    "action_logp",
    "value_pred",
    "action_norm_0",
    "action_norm_1",
    "action_norm_2",
]

REWARD_BREAKDOWN_KEYS = [
    "reward_step_penalty",
    "reward_distance",
    "reward_alignment",
    "reward_closing",
    "reward_theta_progress",
    "reward_alpha_beta",
    "reward_axis_error_penalty",
    "reward_direction_bonus",
    "reward_angle_focus",
    "reward_turn_toward",
    "reward_action_alignment",
    "reward_near_success_bonus",
    "reward_reverse_penalty",
    "reward_roll_penalty",
    "reward_angular_penalty",
    "reward_altitude",
    "reward_soft_floor_penalty",
    "reward_soft_ceiling_penalty",
    "reward_thrust_gate_penalty",
    "reward_terminal",
]

TELEMETRY_VECTOR_SPECS = [
    ("rocket_pos_world", ("x", "y", "z")),
    ("rocket_euler_world", ("x", "y", "z")),
    ("rocket_rot_world", ("x", "y", "z", "w")),
    ("rocket_point_pos_world", ("x", "y", "z")),
    ("rocket_point_forward_world", ("x", "y", "z")),
    ("rocket_point_up_world", ("x", "y", "z")),
    ("rocket_point_right_world", ("x", "y", "z")),
    ("rocket_vel_world", ("x", "y", "z")),
    ("rocket_vel_local", ("x", "y", "z")),
    ("rocket_ang_vel_world", ("x", "y", "z")),
    ("rocket_ang_vel_local", ("x", "y", "z")),
    ("target_pos_world", ("x", "y", "z")),
    ("target_euler_world", ("x", "y", "z")),
    ("target_rot_world", ("x", "y", "z", "w")),
    ("target_point_pos_world", ("x", "y", "z")),
    ("target_point_forward_world", ("x", "y", "z")),
    ("target_point_up_world", ("x", "y", "z")),
    ("target_vel_world", ("x", "y", "z")),
    ("target_vel_in_rocket_local", ("x", "y", "z")),
    ("target_ang_vel_world", ("x", "y", "z")),
    ("target_ang_vel_in_rocket_local", ("x", "y", "z")),
    ("rel_pos_world", ("x", "y", "z")),
    ("rel_pos_local", ("x", "y", "z")),
    ("rel_dir_world", ("x", "y", "z")),
    ("rel_dir_local", ("x", "y", "z")),
    ("rel_vel_world", ("x", "y", "z")),
    ("rel_vel_local", ("x", "y", "z")),
    ("gravity_world", ("x", "y", "z")),
    ("gravity_local", ("x", "y", "z")),
    ("guidance_up_world", ("x", "y", "z")),
    ("guidance_right_world", ("x", "y", "z")),
    ("guidance_forward_world", ("x", "y", "z")),
    ("guidance_up_local", ("x", "y", "z")),
    ("guidance_right_local", ("x", "y", "z")),
    ("guidance_forward_local", ("x", "y", "z")),
    ("rel_vel_guidance", ("x", "y", "z")),
    ("rocket_ang_vel_guidance", ("x", "y", "z")),
    ("applied_turn_world", ("x", "y", "z")),
    ("applied_turn_local", ("x", "y", "z")),
]

TELEMETRY_SCALAR_KEYS = [
    "target_speed",
    "roll_error_deg",
    "beta_validity",
]

TELEMETRY_FLAT_KEYS = [
    f"{name}_{suffix}"
    for name, suffixes in TELEMETRY_VECTOR_SPECS
    for suffix in suffixes
] + TELEMETRY_SCALAR_KEYS

DISTANCE_TANH_SCALE = 100.0
CLOSING_TANH_SCALE = 50.0
REL_VEL_TANH_SCALE = 50.0
ROC_ANG_VEL_TANH_SCALE = 6.0
AGL_TANH_SCALE = 50.0
ALT_ERROR_TANH_SCALE = 50.0
GRAVITY_SCALE = 9.81

MIN_THRUST = 690.0
MAX_THRUST = 850.0
MAX_VERTICAL_CMD = 2.5
MAX_HORIZONTAL_CMD = 2.5
TARGET_VELOCITY = 25.0

# Runtime uses a single manually edited configuration.
ACTIVE_PHASE_ID = 1

REWARD_CONFIG = {
    "step_penalty": -0.08,
    "distance_gain": 0.12,
    "distance_delta_clip": 6.0,
    "alignment_gain": 0.16,
    "closing_gain": 0.10,
    "closing_speed_clip": 30.0,
    "theta_progress_gain": 0.18,
    "alpha_beta_gain": 0.14,
    "axis_error_penalty_gain": 0.10,
    "axis_error_soft_deg": 35.0,
    "direction_bonus_gain": 0.10,
    "angle_focus_gain": 0.12,
    "angle_focus_theta_deg": 90.0,
    "angle_bad_start_deg": 90.0,
    "turn_toward_gain": 0.30,
    "turn_toward_theta_deg": 60.0,
    "turn_toward_rate_clip": 4.0,
    "turn_positive_scale": 1.0,
    "turn_negative_scale": 1.0,
    "action_alignment_gain": 0.08,
    "action_positive_scale": 1.0,
    "action_negative_scale": 1.0,
    "low_altitude_turn_ready_agl": 18.0,
    "near_success_gain": 0.20,
    "near_success_distance": 40.0,
    "near_success_theta_deg": 35.0,
    "reverse_penalty_gain": 0.18,
    "direction_bonus_theta_deg": 40.0,
    "theta_progress_clip_deg": 18.0,
    "alpha_beta_progress_clip_deg": 14.0,
    "ang_vel_penalty": 0.02,
    "ang_vel_clip": 10.0,
    "height_align_gain": 0.012,
    "soft_floor": 8.0,
    "soft_floor_gain": 0.12,
    "soft_ceiling_start": 1000.0,
    "soft_ceiling_gain": 0.0,
    "soft_ceiling_curve_scale": 45.0,
    "thrust_gate_gain": 0.0,
    "thrust_gate_target_norm": -0.20,
    "thrust_gate_theta_start_deg": 35.0,
    "thrust_gate_theta_span_deg": 45.0,
    "thrust_gate_distance_scale": 80.0,
    "thrust_gate_distance_floor": 0.35,
    "min_agl": 0.40,
    "low_agl_grace_steps": 15,
    "collision_grace_steps": 8,
    "max_altitude": 110.0,
    "wrong_way_theta_deg": 128.0,
    "wrong_way_closing_speed": -16.0,
    "wrong_way_distance_ratio": 1.08,
    "wrong_way_grace_steps": 48,
    "success_reward": 180.0,
    "collision_penalty": -130.0,
    "low_altitude_penalty": -110.0,
    "high_altitude_penalty": -85.0,
    "wrong_way_penalty": -95.0,
    "beta_fade_start_abs_forward_up": 0.80,
    "beta_fade_end_abs_forward_up": 0.95,
    "beta_validity_floor": 0.25,
}

ACTIVE_PHASE_CONFIG = {
    "name": "v8_7_phase_2_2_radius_105_120_reward_grid",
    "spawn_radius_min": 105.0,
    "spawn_radius_max": 120.0,
    "heading_offset_min": -2.5,
    "heading_offset_max": 2.5,
    "max_step": 520,
    "step_penalty": -0.04,
    "distance_gain": 0.14,
    "alignment_gain": 0.12,
    "closing_gain": 0.04,
    "theta_progress_gain": 1.665,
    "theta_progress_clip_deg": 12.0,
    "alpha_beta_gain": 0.465,
    "alpha_beta_progress_clip_deg": 18.0,
    "axis_error_penalty_gain": 0.28,
    "axis_error_soft_deg": 30.0,
    "direction_bonus_gain": 0.0,
    "angle_focus_gain": 1.87,
    "angle_focus_theta_deg": 90.0,
    "angle_bad_start_deg": 70.0,
    "near_angle_distance": 70.0,
    "near_angle_span": 55.0,
    "turn_toward_gain": 0.384,
    "turn_toward_theta_deg": 75.0,
    "turn_toward_rate_clip": 4.0,
    "action_alignment_gain": 0.060,
    "near_success_gain": 0.25,
    "near_success_distance": 45.0,
    "near_success_theta_deg": 35.0,
    "reverse_penalty_gain": 0.405,
    "ang_vel_penalty": 0.035,
    "height_align_gain": 0.022,
    "soft_floor_gain": 0.05,
    "soft_floor_grace_steps": 60,
    "soft_ceiling_start": 105.0,
    "soft_ceiling_gain": 0.018,
    "thrust_gate_gain": 1.65,
    "thrust_gate_target_norm": -0.45,
    "thrust_gate_theta_start_deg": 55.0,
    "thrust_gate_theta_span_deg": 15.0,
    "thrust_gate_distance_scale": 30.0,
    "thrust_gate_distance_floor": 0.65,
    "low_altitude_penalty": -110.0,
    "high_altitude_penalty": -105.0,
    "max_altitude": 145.0,
    "wrong_way_theta_deg": 128.0,
    "wrong_way_closing_speed": -12.0,
    "wrong_way_distance_ratio": 1.05,
    "wrong_way_grace_steps": 36,
    "wrong_way_penalty": -115.0,
    "near_miss_distance": 18.0,
    "near_miss_theta_deg": 75.0,
    "near_miss_grace_steps": 80,
    "near_miss_penalty": -90.0,
    "success_distance": 15.0,
    "success_alignment": 0.76,
    "success_min_closing": 0.0,
    "success_reward": 180.0,
    "timeout_penalty": -80.0,
}


def get_active_phase_id():
    return ACTIVE_PHASE_ID


def get_phase_config(_phase_id=None):
    config = dict(REWARD_CONFIG)
    config.update(ACTIVE_PHASE_CONFIG)
    return config


def compute_beta_validity(forward_up_dot, phase):
    abs_forward_up_dot = abs(float(forward_up_dot))
    fade_start = float(phase["beta_fade_start_abs_forward_up"])
    fade_end = float(phase["beta_fade_end_abs_forward_up"])
    validity_floor = float(phase.get("beta_validity_floor", 0.0))

    if abs_forward_up_dot <= fade_start:
        return 1.0
    if abs_forward_up_dot >= fade_end:
        return validity_floor

    t = (abs_forward_up_dot - fade_start) / max(fade_end - fade_start, 1e-6)
    t = float(np.clip(t, 0.0, 1.0))
    smooth = t * t * (3.0 - 2.0 * t)
    return float(validity_floor + (1.0 - validity_floor) * (1.0 - smooth))


def calculate_new_loc(radius_min, radius_max):
    theta = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(radius_min, radius_max)
    px = radius * np.cos(theta)
    pz = radius * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz, px))
    return px, pz, ry, rz


def flatten_telemetry(telemetry):
    flat = {}

    if not isinstance(telemetry, dict):
        return flat

    for name, suffixes in TELEMETRY_VECTOR_SPECS:
        values = telemetry.get(name)
        if not isinstance(values, (list, tuple)):
            continue

        for index, suffix in enumerate(suffixes):
            if index < len(values):
                flat[f"{name}_{suffix}"] = float(values[index])

    for key in TELEMETRY_SCALAR_KEYS:
        if key in telemetry:
            flat[key] = float(telemetry[key])

    return flat


class Env:
    def __init__(self, ip, port):
        self.connect = connector.Connector(ip, port)
        self.done = False
        self.state_size = len(STATE_KEYS)
        self.action_size = len(ACTION_KEYS)
        self.phase_id = get_active_phase_id()
        self.phase = get_phase_config(self.phase_id)
        self.max_step = int(self.phase["max_step"])
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None
        self.reset_distance = None
        self.prev_theta = None
        self.prev_alpha_abs = None
        self.prev_beta_abs = None

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def read_state(self):
        return self.connect.read_packet()

    def parse_state(self, raw_state):
        s = raw_state["states"]

        return np.array([
            s["distance"],
            s["theta_rad"],
            s["alpha_rad"],
            s["beta_rad"],
            s["closing_speed"],
            s["rel_vel_ref"][0],
            s["rel_vel_ref"][1],
            s["rel_vel_ref"][2],
            s["turn_rate_ref"][0],
            s["turn_rate_ref"][1],
            s["turn_rate_ref"][2],
            s["forward_up_dot"],
            s["agl"],
            s["alt_error"],
        ], dtype=np.float32)

    def normalize_state(self, vector_state):
        s = vector_state.copy()
        s[0] = np.tanh(s[0] / DISTANCE_TANH_SCALE)
        s[1] = np.clip(s[1] / np.pi, 0.0, 1.0)
        s[2] = np.clip(s[2] / np.pi, -1.0, 1.0)
        s[3] = np.clip(s[3] / np.pi, -1.0, 1.0)
        s[4] = np.tanh(s[4] / CLOSING_TANH_SCALE)
        s[5:8] = np.tanh(s[5:8] / REL_VEL_TANH_SCALE)
        s[8:11] = np.tanh(s[8:11] / ROC_ANG_VEL_TANH_SCALE)
        s[11] = np.clip(s[11], -1.0, 1.0)
        s[12] = np.tanh(s[12] / AGL_TANH_SCALE)
        s[13] = np.tanh(s[13] / ALT_ERROR_TANH_SCALE)
        return s.astype(np.float32)

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def reset(self):
        self.episode_id += 1
        px, pz, ry, rz = calculate_new_loc(
            self.phase["spawn_radius_min"],
            self.phase["spawn_radius_max"],
        )
        random_rot_degree = np.random.randint(
            self.phase["heading_offset_min"],
            self.phase["heading_offset_max"] + 1,
        )
        rz += random_rot_degree
        py = 50.0

        self.done = False
        self.step_count = 0

        init_loc = {
            "episode_id": self.episode_id,
            "step_id": 0,
            "type": "reset",
            "values": [px, py, pz, ry, rz]
        }
        self.connect.send_packet(data=init_loc)

        raw_state = self.read_state()
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)
        self.prev_distance = float(raw_state["states"]["distance"])
        self.reset_distance = self.prev_distance
        self.prev_theta = abs(float(np.degrees(raw_state["states"]["theta_rad"])))
        self.prev_alpha_abs = abs(float(np.degrees(raw_state["states"]["alpha_rad"])))
        self.prev_beta_abs = abs(float(np.degrees(raw_state["states"]["beta_rad"])))
        start_info = self.build_info(raw_state)

        start_info.update({
            "phase_id": self.phase_id,
            "phase_name": self.phase["name"],
            "reset_px": px,
            "reset_py": py,
            "reset_pz": pz,
            "reset_ry": ry,
            "reset_rz": rz,
            "reset_heading_offset": random_rot_degree
        })

        return raw_state, vector_state, normalized_state, start_info

    # ------------------------------------------------------------------
    # REWARD
    # ------------------------------------------------------------------

    def calculate_reward(self, raw_state, denorm_action=None):
        phase = self.phase
        states = raw_state["states"]
        telemetry = raw_state.get("telemetry", {})

        distance = float(states["distance"])
        agl = float(states["agl"])
        alt_error = float(states["alt_error"])
        grounded = float(states["grounded_flag"]) > 0.5
        closing_speed = float(states["closing_speed"])
        theta_rad = float(states["theta_rad"])
        theta_deg = float(np.degrees(theta_rad))
        alpha_rad = float(states["alpha_rad"])
        alpha_deg = float(np.degrees(alpha_rad))
        beta_rad = float(states["beta_rad"])
        beta_deg = float(np.degrees(beta_rad))
        alpha_abs = abs(alpha_deg)
        beta_abs = abs(beta_deg)
        beta_validity = float(telemetry.get("beta_validity", compute_beta_validity(states["forward_up_dot"], phase)))
        combined_axis_error = alpha_abs + beta_abs
        alignment = float(np.cos(theta_rad))
        alignment_positive = max(alignment, 0.0)
        signed_closing = float(np.clip(closing_speed / phase["closing_speed_clip"], -1.0, 1.0))
        positive_closing = max(signed_closing, 0.0)
        ceiling_excess = max(agl - phase["soft_ceiling_start"], 0.0)
        altitude_progress_gate = float(np.clip(1.0 - (ceiling_excess / 55.0), 0.25, 1.0))

        av = states["turn_rate_ref"]
        turn_rate_vertical = float(av[0])
        turn_rate_horizontal = float(av[1])
        ang_vel_mag = float(np.sqrt(av[0] ** 2 + av[1] ** 2 + av[2] ** 2))
        roll_rate_mag = abs(float(av[2]))
        roll_error_deg = abs(float(raw_state.get("telemetry", {}).get("roll_error_deg", 0.0)))
        thrust_cmd_norm = 0.0
        vertical_cmd_norm = 0.0
        horizontal_cmd_norm = 0.0
        if denorm_action is not None and len(denorm_action) >= 3:
            thrust_cmd_norm = float(np.clip(
                ((denorm_action[0] - MIN_THRUST) / max(MAX_THRUST - MIN_THRUST, 1e-6)) * 2.0 - 1.0,
                -1.0,
                1.0,
            ))
            vertical_cmd_norm = float(np.clip(denorm_action[1] / max(MAX_VERTICAL_CMD, 1e-6), -1.0, 1.0))
            horizontal_cmd_norm = float(np.clip(denorm_action[2] / max(MAX_HORIZONTAL_CMD, 1e-6), -1.0, 1.0))

        reward = phase["step_penalty"]
        done = False
        done_reason = None
        success = False
        terminal_reward = 0.0

        delta_distance = self.prev_distance - distance
        delta_distance = np.clip(
            delta_distance,
            -phase["distance_delta_clip"],
            phase["distance_delta_clip"],
        )

        prev_theta = theta_deg if self.prev_theta is None else self.prev_theta
        prev_alpha_abs = alpha_abs if self.prev_alpha_abs is None else self.prev_alpha_abs
        prev_beta_abs = beta_abs if self.prev_beta_abs is None else self.prev_beta_abs

        delta_theta_deg = float(np.clip(
            prev_theta - theta_deg,
            -phase["theta_progress_clip_deg"],
            phase["theta_progress_clip_deg"],
        ))
        delta_alpha_beta_deg = float(np.clip(
            (prev_alpha_abs + prev_beta_abs) - (alpha_abs + beta_abs),
            -phase["alpha_beta_progress_clip_deg"],
            phase["alpha_beta_progress_clip_deg"],
        ))

        angle_focus_window = float(np.clip(
            1.0 - (theta_deg / phase["angle_focus_theta_deg"]),
            0.0,
            1.0,
        ))
        angle_bad_window = float(np.clip(
            (theta_deg - phase["angle_bad_start_deg"])
            / max(1.0, 180.0 - phase["angle_bad_start_deg"]),
            0.0,
            1.0,
        ))
        good_angle_gate = float(np.clip((90.0 - theta_deg) / 75.0, 0.0, 1.0))
        near_angle_proximity = float(np.clip(
            (phase["near_angle_distance"] - distance) / max(phase["near_angle_span"], 1e-6),
            0.0,
            1.0,
        ))
        progress_urgency = float(np.clip(
            ((self.reset_distance or distance) - distance) / max((self.reset_distance or distance) - 35.0, 1e-6),
            0.0,
            1.0,
        ))
        theta_norm = float(np.clip(theta_deg / 120.0, 0.0, 1.5))
        axis_norm = float(np.clip(combined_axis_error / 180.0, 0.0, 1.5))

        # Distance and closing are allowed to help only when the rocket is target-facing.
        distance_reward = (
            phase["distance_gain"]
            * delta_distance
            * alignment_positive
            * (0.20 + 0.80 * good_angle_gate)
        )
        alignment_reward = phase["alignment_gain"] * alignment * (0.20 + 0.80 * positive_closing)
        closing_reward = 0.0
        if signed_closing > 0.0:
            closing_reward = phase["closing_gain"] * signed_closing * alignment_positive * good_angle_gate
        else:
            closing_reward = phase["closing_gain"] * signed_closing * (0.25 + 0.75 * angle_bad_window)

        theta_progress_reward = phase["theta_progress_gain"] * (delta_theta_deg / phase["theta_progress_clip_deg"])
        alpha_beta_reward = phase["alpha_beta_gain"] * (delta_alpha_beta_deg / phase["alpha_beta_progress_clip_deg"])
        axis_error_penalty = phase["axis_error_penalty_gain"] * near_angle_proximity * (axis_norm ** 2)

        direction_theta_window = float(np.clip(
            1.0 - (theta_deg / phase["direction_bonus_theta_deg"]),
            0.0,
            1.0,
        ))
        direction_axis_window = float(np.clip(
            1.0 - (combined_axis_error / 140.0),
            0.0,
            1.0,
        ))
        direction_bonus = (
            phase["direction_bonus_gain"]
            * max(delta_distance, 0.0)
            / max(phase["distance_delta_clip"], 1e-6)
            * direction_theta_window
            * direction_axis_window
            * (0.25 + 0.75 * positive_closing)
        )
        direction_bonus *= angle_focus_window
        angle_focus_reward = 0.0
        angle_focus_reward -= (
            phase["angle_focus_gain"]
            * near_angle_proximity
            * (theta_norm ** 2)
            * (0.35 + 0.65 * (1.0 + max(-signed_closing, 0.0)))
        )
        if delta_theta_deg < 0.0:
            angle_focus_reward -= (
                phase["theta_progress_gain"]
                * 0.55
                * progress_urgency
                * min(abs(delta_theta_deg) / max(phase["theta_progress_clip_deg"], 1e-6), 1.0)
                * (0.50 + 0.50 * theta_norm)
            )
        turn_need_window = float(np.clip(
            theta_deg / max(phase["turn_toward_theta_deg"], 1e-6),
            0.0,
            1.0,
        ))
        alpha_cmd_norm = float(np.clip(alpha_deg / 90.0, -1.0, 1.0))
        beta_cmd_norm = float(np.clip(beta_deg / 90.0, -1.0, 1.0))
        turn_rate_vertical_norm = float(np.clip(
            turn_rate_vertical / max(phase["turn_toward_rate_clip"], 1e-6),
            -1.0,
            1.0,
        ))
        turn_rate_horizontal_norm = float(np.clip(
            turn_rate_horizontal / max(phase["turn_toward_rate_clip"], 1e-6),
            -1.0,
            1.0,
        ))
        turn_toward_score = float(np.clip(
            (
                alpha_cmd_norm * turn_rate_vertical_norm
                + beta_cmd_norm * turn_rate_horizontal_norm
            ) * turn_need_window,
            -1.0,
            1.0,
        ))
        action_alignment_score = float(np.clip(
            (
                alpha_cmd_norm * vertical_cmd_norm
                + beta_cmd_norm * horizontal_cmd_norm
            ) * turn_need_window,
            -1.0,
            1.0,
        ))
        turn_toward_reward = phase["turn_toward_gain"] * turn_toward_score
        action_alignment_reward = phase["action_alignment_gain"] * action_alignment_score

        near_success_distance_window = float(np.clip(
            1.0 - (distance / phase["near_success_distance"]),
            0.0,
            1.0,
        ))
        near_success_theta_window = float(np.clip(
            1.0 - (theta_deg / phase["near_success_theta_deg"]),
            0.0,
            1.0,
        ))
        near_success_bonus = (
            phase["near_success_gain"]
            * near_success_distance_window
            * near_success_theta_window
            * (0.30 + 0.70 * positive_closing)
        )

        wrong_way_theta_factor = float(np.clip(
            (theta_deg - phase["wrong_way_theta_deg"]) / max(1.0, 180.0 - phase["wrong_way_theta_deg"]),
            0.0,
            1.0,
        ))
        wrong_way_distance_ratio = distance / max(self.reset_distance or distance, 1e-6)
        wrong_way_distance_factor = float(np.clip(
            (wrong_way_distance_ratio - 1.0) / max(0.01, phase["wrong_way_distance_ratio"] - 1.0),
            0.0,
            1.0,
        ))
        reverse_penalty = 0.0
        if delta_distance < 0.0 or signed_closing < 0.0:
            reverse_penalty = (
                phase["reverse_penalty_gain"]
                * max(0.0, (theta_deg - 70.0) / 80.0)
                * (
                    0.50 * min(abs(delta_distance) / max(phase["distance_delta_clip"], 1e-6), 1.0)
                    + 0.50 * max(-signed_closing, 0.0)
                )
            )

        roll_penalty_term = 0.08 * min(roll_rate_mag / max(phase["ang_vel_clip"], 1e-6), 1.0)
        roll_error_term = 0.04 * min(roll_error_deg / 45.0, 1.0)
        roll_penalty = roll_penalty_term + roll_error_term
        angular_penalty = phase["ang_vel_penalty"] * min(ang_vel_mag, phase["ang_vel_clip"])
        angular_penalty += roll_penalty
        altitude_reward = phase["height_align_gain"] * np.clip(1.0 - np.abs(alt_error) / 50.0, 0.0, 1.0)
        soft_floor_penalty = 0.0
        soft_ceiling_penalty = 0.0
        thrust_gate_penalty = 0.0

        if agl < phase["soft_floor"] and self.step_count > phase["soft_floor_grace_steps"]:
            soft_floor_penalty = phase["soft_floor_gain"] * (phase["soft_floor"] - agl)
        if agl > phase["soft_ceiling_start"]:
            soft_ceiling_penalty = (
                phase["soft_ceiling_gain"]
                * ceiling_excess
                * (1.0 + max(0.0, theta_deg - 60.0) / 100.0)
            )
        if phase["thrust_gate_gain"] > 0.0:
            thrust_excess = max(0.0, thrust_cmd_norm - phase["thrust_gate_target_norm"])
            thrust_angle_gate = float(np.clip(
                (theta_deg - phase["thrust_gate_theta_start_deg"])
                / max(phase["thrust_gate_theta_span_deg"], 1e-6),
                0.0,
                1.0,
            ))
            thrust_distance_floor = phase["thrust_gate_distance_floor"]
            thrust_distance_gate = thrust_distance_floor + (1.0 - thrust_distance_floor) * float(np.clip(
                distance / max(phase["thrust_gate_distance_scale"], 1e-6),
                0.0,
                1.0,
            ))
            thrust_gate_penalty = (
                phase["thrust_gate_gain"]
                * thrust_excess
                * thrust_angle_gate
                * thrust_distance_gate
            )

        reward += distance_reward
        reward += alignment_reward
        reward += closing_reward
        reward += theta_progress_reward
        reward += alpha_beta_reward
        reward -= axis_error_penalty
        reward += direction_bonus
        reward += angle_focus_reward
        reward += turn_toward_reward
        reward += action_alignment_reward
        reward += near_success_bonus
        reward -= reverse_penalty
        reward -= angular_penalty
        reward += altitude_reward
        reward -= soft_floor_penalty
        reward -= soft_ceiling_penalty
        reward -= thrust_gate_penalty

        if (
            distance <= phase["success_distance"]
            and alignment >= phase["success_alignment"]
            and closing_speed >= phase["success_min_closing"]
        ):
            terminal_reward = phase["success_reward"]
            reward += terminal_reward
            done = True
            done_reason = "success"
            success = True
        elif grounded and self.step_count > phase["collision_grace_steps"]:
            terminal_reward = phase["collision_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "collision"
        elif agl <= phase["min_agl"] and self.step_count > phase["low_agl_grace_steps"]:
            terminal_reward = phase["low_altitude_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "low_agl"
        elif (
            self.step_count > phase["near_miss_grace_steps"]
            and distance <= phase["near_miss_distance"]
            and theta_deg >= phase["near_miss_theta_deg"]
        ):
            terminal_reward = phase["near_miss_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "near_miss"
        elif agl >= phase["max_altitude"]:
            terminal_reward = phase["high_altitude_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "high_altitude"
        elif (
            self.step_count >= phase["wrong_way_grace_steps"]
            and theta_deg >= phase["wrong_way_theta_deg"]
            and closing_speed <= phase["wrong_way_closing_speed"]
            and wrong_way_distance_ratio >= phase["wrong_way_distance_ratio"]
        ):
            terminal_reward = phase["wrong_way_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "wrong_way"
        elif self.step_count >= self.max_step:
            terminal_reward = phase["timeout_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "timeout"

        self.prev_distance = distance
        self.prev_theta = theta_deg
        self.prev_alpha_abs = alpha_abs
        self.prev_beta_abs = beta_abs

        reward_info = {
            "reward_total": float(reward),
            "distance": float(distance),
            "delta_distance": float(delta_distance),
            "distance_ratio_from_reset": float(wrong_way_distance_ratio),
            "agl": float(agl),
            "alt_error": float(alt_error),
            "closing_speed": float(closing_speed),
            "alignment": float(alignment),
            "theta_rad": float(theta_rad),
            "theta_deg": float(theta_deg),
            "alpha_rad": float(alpha_rad),
            "alpha_deg": float(alpha_deg),
            "beta_rad": float(beta_rad),
            "beta_deg": float(beta_deg),
            "beta_validity": float(beta_validity),
            "ang_vel_mag": float(ang_vel_mag),
            "reward_step_penalty": float(phase["step_penalty"]),
            "reward_distance": float(distance_reward),
            "reward_alignment": float(alignment_reward),
            "reward_closing": float(closing_reward),
            "reward_theta_progress": float(theta_progress_reward),
            "reward_alpha_beta": float(alpha_beta_reward),
            "reward_axis_error_penalty": float(axis_error_penalty),
            "reward_direction_bonus": float(direction_bonus),
            "reward_angle_focus": float(angle_focus_reward),
            "reward_turn_toward": float(turn_toward_reward),
            "reward_action_alignment": float(action_alignment_reward),
            "reward_near_success_bonus": float(near_success_bonus),
            "reward_reverse_penalty": float(reverse_penalty),
            "reward_roll_penalty": float(roll_penalty),
            "reward_angular_penalty": float(angular_penalty),
            "reward_altitude": float(altitude_reward),
            "reward_soft_floor_penalty": float(soft_floor_penalty),
            "reward_soft_ceiling_penalty": float(soft_ceiling_penalty),
            "reward_thrust_gate_penalty": float(thrust_gate_penalty),
            "reward_terminal": float(terminal_reward),
            "grounded_flag": 1.0 if grounded else 0.0,
            "done_reason": done_reason,
            "success": success,
        }
        return float(reward), done, reward_info

    # ------------------------------------------------------------------
    # STEP
    # ------------------------------------------------------------------

    def step(self, action):
        self.step_count += 1
        denorm_action = self.denormalize_action(action)

        action_dict = {
            "episode_id": self.episode_id,
            "step_id": self.step_count,
            "type": "action",
            "values": denorm_action
        }

        self.connect.send_packet(action_dict)

        raw_state = self.read_state()
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)

        reward, done, reward_info = self.calculate_reward(raw_state, denorm_action=denorm_action)

        info = self.build_info(
            raw_state=raw_state,
            denorm_action=denorm_action,
            reward=reward,
            done=done,
            done_reason=reward_info["done_reason"]
        )
        info["grounded_flag"] = reward_info["grounded_flag"]
        info["alignment"] = reward_info["alignment"]
        info["ang_vel_mag"] = reward_info["ang_vel_mag"]
        info["closing_speed"] = reward_info["closing_speed"]
        info["delta_distance"] = reward_info["delta_distance"]
        info["theta_rad"] = reward_info["theta_rad"]
        info["theta_deg"] = reward_info["theta_deg"]
        info["alpha_rad"] = reward_info["alpha_rad"]
        info["alpha_deg"] = reward_info["alpha_deg"]
        info["beta_rad"] = reward_info["beta_rad"]
        info["beta_deg"] = reward_info["beta_deg"]
        info["reward_total"] = reward_info["reward_total"]
        info["success"] = reward_info["success"]

        for key in REWARD_BREAKDOWN_KEYS:
            info[key] = reward_info[key]

        self.done = done
        return normalized_state, reward, done, info

    # ------------------------------------------------------------------
    # YARDIMCI METODLAR
    # ------------------------------------------------------------------

    def denormalize_action(self, action):
        a = np.asarray(action, dtype=np.float32)
        a = np.clip(a, -1.0, 1.0)

        thrust = MIN_THRUST + ((a[0] + 1.0) / 2.0) * (MAX_THRUST - MIN_THRUST)
        vertical_cmd = a[1] * MAX_VERTICAL_CMD
        horizontal_cmd = a[2] * MAX_HORIZONTAL_CMD

        return [float(thrust), float(vertical_cmd), float(horizontal_cmd)]

    def build_info(self, raw_state, denorm_action=None, reward=None, done=None, done_reason=None):
        s = raw_state["states"]
        telemetry = raw_state.get("telemetry", {})

        theta_rad = float(s["theta_rad"])
        alpha_rad = float(s["alpha_rad"])
        beta_rad = float(s["beta_rad"])
        alignment = float(np.cos(theta_rad))

        info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "episode_id": raw_state["episode_id"],
            "step_id": raw_state["step_id"],
            "phase_id": self.phase_id,
            "phase_name": self.phase["name"],
            "max_step": self.max_step,
            "reward": reward,
            "done": done,
            "done_reason": done_reason,
            "distance": float(s["distance"]),
            "closing_speed": float(s["closing_speed"]),
            "theta_rad": theta_rad,
            "theta_deg": float(np.degrees(theta_rad)),
            "alpha_rad": alpha_rad,
            "alpha_deg": float(np.degrees(alpha_rad)),
            "beta_rad": beta_rad,
            "beta_deg": float(np.degrees(beta_rad)),
            "alignment": alignment,
            "rel_vel_right": float(s["rel_vel_ref"][0]),
            "rel_vel_up": float(s["rel_vel_ref"][1]),
            "rel_vel_forward": float(s["rel_vel_ref"][2]),
            "turn_rate_vertical": float(s["turn_rate_ref"][0]),
            "turn_rate_horizontal": float(s["turn_rate_ref"][1]),
            "turn_rate_roll": float(s["turn_rate_ref"][2]),
            "forward_up_dot": float(s["forward_up_dot"]),
            "agl": float(s["agl"]),
            "alt_error": float(s["alt_error"]),
            "grounded_flag": float(s["grounded_flag"]),
        }

        info.update(flatten_telemetry(telemetry))

        if denorm_action is not None:
            info["thrust"] = denorm_action[0]
            info["vertical_cmd"] = denorm_action[1]
            info["horizontal_cmd"] = denorm_action[2]
        else:
            info["thrust"] = None
            info["vertical_cmd"] = None
            info["horizontal_cmd"] = None

        return info

    def close(self):
        self.connect.close()
