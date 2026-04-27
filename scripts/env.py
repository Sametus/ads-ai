from datetime import datetime

import connector
import numpy as np

STATE_KEYS = [
    "distance",
    "theta_rad",
    "alpha_rad",
    "beta_rad",
    "target_clock_12",
    "target_clock_6",
    "target_clock_3",
    "target_clock_9",
    "closing_speed",
    "rel_vel_clock_12",
    "rel_vel_clock_6",
    "rel_vel_clock_3",
    "rel_vel_clock_9",
    "rel_vel_forward",
    "turn_rate_clock_12",
    "turn_rate_clock_6",
    "turn_rate_clock_3",
    "turn_rate_clock_9",
    "turn_rate_roll",
    "clock_validity",
    "forward_up_dot",
    "agl",
    "alt_error",
]

SQRT_HALF = float(np.sqrt(0.5))

TURN_DIRECTION_NAMES = [
    "hold",
    "clock_12",
    "clock_12_3",
    "clock_3",
    "clock_3_6",
    "clock_6",
    "clock_6_9",
    "clock_9",
    "clock_9_12",
]

# V10 policy outputs a continuous thrust plus one categorical clock direction.
# Python expands the direction into the existing Unity clock torque channels.
TURN_DIRECTION_VECTORS = np.asarray(
    [
        [0.0, 0.0],
        [1.0, 0.0],
        [SQRT_HALF, SQRT_HALF],
        [0.0, 1.0],
        [-SQRT_HALF, SQRT_HALF],
        [-1.0, 0.0],
        [-SQRT_HALF, -SQRT_HALF],
        [0.0, -1.0],
        [SQRT_HALF, -SQRT_HALF],
    ],
    dtype=np.float32,
)
TURN_DIRECTION_COUNT = len(TURN_DIRECTION_NAMES)
DISCRETE_TURN_STRENGTH = 1.2

ACTION_KEYS = ["thrust", "turn_direction"]

PYTHON_STEP_LOG_KEYS = [
    "episode_return_so_far",
    "action_logp",
    "value_pred",
    "action_norm_0",
    "action_direction_id",
    "action_direction_clock12",
    "action_direction_clock3",
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
    "reward_close_angle_penalty",
    "reward_turn_toward",
    "reward_clock_action_alignment",
    "reward_clock_wrong_channel",
    "reward_clock_coactivation",
    "reward_near_success_bonus",
    "reward_reverse_penalty",
    "reward_roll_penalty",
    "reward_angular_penalty",
    "reward_altitude",
    "reward_soft_floor_penalty",
    "reward_late_floor_penalty",
    "reward_soft_ceiling_penalty",
    "reward_thrust_gate_penalty",
    "reward_bad_thrust_angle_penalty",
    "reward_low_altitude_escape",
    "reward_low_altitude_control",
    "reward_low_altitude_sink_penalty",
    "reward_low_altitude_guidance_discount",
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
    ("rocket_body_forward_world", ("x", "y", "z")),
    ("rocket_body_up_world", ("x", "y", "z")),
    ("rocket_body_right_world", ("x", "y", "z")),
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
    ("clock_12_world", ("x", "y", "z")),
    ("clock_3_world", ("x", "y", "z")),
    ("clock_forward_world", ("x", "y", "z")),
    ("clock_12_local", ("x", "y", "z")),
    ("clock_3_local", ("x", "y", "z")),
    ("clock_forward_local", ("x", "y", "z")),
    ("rel_vel_guidance", ("x", "y", "z")),
    ("rel_vel_clock_signed", ("x", "y", "z")),
    ("rocket_ang_vel_guidance", ("x", "y", "z")),
    ("rocket_turn_clock_signed", ("x", "y", "z")),
    ("thrust_world", ("x", "y", "z")),
    ("desired_clock_turn_world", ("x", "y", "z")),
    ("command_turn_world", ("x", "y", "z")),
    ("command_turn_local", ("x", "y", "z")),
    ("torque_command_local", ("x", "y", "z")),
    ("torque_command_world", ("x", "y", "z")),
    ("applied_turn_world", ("x", "y", "z")),
    ("applied_turn_local", ("x", "y", "z")),
]

TELEMETRY_SCALAR_KEYS = [
    "target_speed",
    "roll_error_deg",
    "beta_validity",
    "clock_validity",
    "target_clock_angle_deg",
    "action_clock_angle_deg",
    "action_clock_mag",
    "action_clock12_raw",
    "action_clock3_raw",
    "action_clock12_net",
    "action_clock3_net",
    "low_altitude_turn_scale",
    "clock12_scale",
    "clock3_scale",
    "beta_validity_applied",
    "roll_control_scale",
    "roll_correction_cmd",
    "roll_correction_limit",
    "roll_torque_limit",
    "suppressed_roll_rate",
    "rocket_point_body_forward_dot",
    "rocket_point_body_up_dot",
    "rocket_point_body_right_dot",
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

MIN_THRUST = 620.0
MAX_THRUST = 700.0
MAX_CLOCK_CMD = 2.0
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
    "close_angle_penalty_gain": 0.0,
    "close_angle_distance": 55.0,
    "close_angle_theta_start_deg": 35.0,
    "close_angle_theta_span_deg": 80.0,
    "turn_toward_gain": 0.30,
    "turn_toward_theta_deg": 60.0,
    "turn_toward_rate_clip": 4.0,
    "turn_positive_scale": 1.0,
    "turn_negative_scale": 1.0,
    "clock_action_alignment_gain": 0.0,
    "clock_wrong_channel_penalty_gain": 0.0,
    "clock_coactivation_penalty_gain": 0.0,
    "clock_reward_validity_floor": 0.70,
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
    "late_floor_agl": 28.0,
    "late_floor_step": 160,
    "late_floor_penalty_gain": 0.0,
    "soft_ceiling_start": 1000.0,
    "soft_ceiling_gain": 0.0,
    "soft_ceiling_curve_scale": 45.0,
    "thrust_gate_gain": 0.0,
    "thrust_gate_target_norm": -0.20,
    "thrust_gate_theta_start_deg": 35.0,
    "thrust_gate_theta_span_deg": 45.0,
    "thrust_gate_distance_scale": 80.0,
    "thrust_gate_distance_floor": 0.35,
    "bad_thrust_angle_penalty_gain": 0.0,
    "bad_thrust_angle_min_thrust": 700.0,
    "bad_thrust_angle_theta_start_deg": 45.0,
    "bad_thrust_angle_theta_span_deg": 90.0,
    "bad_thrust_angle_step": 120,
    "low_alt_safe_agl": 8.0,
    "low_alt_escape_steps": 140,
    "low_alt_climb_speed": 4.0,
    "low_alt_agl_progress_clip": 0.12,
    "low_alt_escape_gain": 0.0,
    "low_alt_control_penalty_gain": 0.0,
    "low_alt_sink_penalty_gain": 0.0,
    "low_alt_guidance_discount_gain": 0.0,
    "low_alt_thrust_gate_relief": 0.0,
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
    "name": "v10_0_1_phase_1_clock_reward_recovery_140_160",
    "spawn_radius_min": 140.0,
    "spawn_radius_max": 160.0,
    "heading_offset_min": -5.0,
    "heading_offset_max": 5.0,
    "heading_offset_abs_min": 1.0,
    "max_step": 700,
    "step_penalty": -0.015,
    "distance_gain": 0.14,
    "alignment_gain": 0.12,
    "closing_gain": 0.04,
    "theta_progress_gain": 3.00,
    "theta_progress_clip_deg": 10.0,
    "alpha_beta_gain": 0.90,
    "alpha_beta_progress_clip_deg": 16.0,
    "axis_error_penalty_gain": 0.28,
    "axis_error_soft_deg": 30.0,
    "direction_bonus_gain": 0.06,
    "direction_bonus_theta_deg": 70.0,
    "angle_focus_gain": 0.55,
    "angle_focus_theta_deg": 100.0,
    "angle_bad_start_deg": 58.0,
    "close_angle_penalty_gain": 0.95,
    "close_angle_distance": 55.0,
    "close_angle_theta_start_deg": 35.0,
    "close_angle_theta_span_deg": 80.0,
    "near_angle_distance": 125.0,
    "near_angle_span": 110.0,
    "turn_toward_gain": 0.95,
    "turn_toward_theta_deg": 75.0,
    "turn_toward_rate_clip": 4.0,
    "clock_action_alignment_gain": 1.20,
    "clock_wrong_channel_penalty_gain": 1.20,
    "clock_coactivation_penalty_gain": 0.10,
    "clock_reward_validity_floor": 0.70,
    "near_success_gain": 0.45,
    "near_success_distance": 42.0,
    "near_success_theta_deg": 34.0,
    "reverse_penalty_gain": 0.45,
    "ang_vel_penalty": 0.035,
    "height_align_gain": 0.022,
    "soft_floor_gain": 0.025,
    "soft_floor_grace_steps": 110,
    "soft_ceiling_start": 80.0,
    "soft_ceiling_gain": 0.035,
    "thrust_gate_gain": 0.65,
    "thrust_gate_target_norm": -0.10,
    "thrust_gate_theta_start_deg": 55.0,
    "thrust_gate_theta_span_deg": 28.0,
    "thrust_gate_distance_scale": 90.0,
    "thrust_gate_distance_floor": 0.45,
    "bad_thrust_angle_penalty_gain": 0.45,
    "bad_thrust_angle_min_thrust": 670.0,
    "bad_thrust_angle_theta_start_deg": 45.0,
    "bad_thrust_angle_theta_span_deg": 90.0,
    "bad_thrust_angle_step": 120,
    "low_alt_safe_agl": 10.0,
    "low_alt_escape_steps": 150,
    "low_alt_climb_speed": 4.0,
    "low_alt_agl_progress_clip": 0.12,
    "low_alt_escape_gain": 0.35,
    "low_alt_control_penalty_gain": 0.10,
    "low_alt_sink_penalty_gain": 2.40,
    "low_alt_guidance_discount_gain": 1.00,
    "low_alt_thrust_gate_relief": 0.80,
    "late_floor_agl": 28.0,
    "late_floor_step": 160,
    "late_floor_penalty_gain": 0.80,
    "min_agl": 0.18,
    "low_agl_grace_steps": 100,
    "collision_penalty": -150.0,
    "low_altitude_penalty": -180.0,
    "high_altitude_penalty": -150.0,
    "max_altitude": 125.0,
    "wrong_way_theta_deg": 128.0,
    "wrong_way_closing_speed": -12.0,
    "wrong_way_distance_ratio": 1.05,
    "wrong_way_grace_steps": 36,
    "wrong_way_penalty": -115.0,
    "near_miss_distance": 16.0,
    "near_miss_theta_deg": 75.0,
    "near_miss_grace_steps": 140,
    "near_miss_penalty": -55.0,
    "success_distance": 10.0,
    "success_alignment": 0.90,
    "success_min_closing": 0.0,
    "success_reward": 260.0,
    "timeout_penalty": -75.0,
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


def calculate_new_loc(
    radius_min,
    radius_max,
    heading_offset_min=0.0,
    heading_offset_max=0.0,
    heading_offset_abs_min=0.0,
):
    theta = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(radius_min, radius_max)
    px = radius * np.cos(theta)
    pz = radius * np.sin(theta)
    ry = 180.0
    base_rz = 90.0 - np.degrees(np.arctan2(pz, px))

    heading_min = int(np.ceil(heading_offset_min))
    heading_max = int(np.floor(heading_offset_max))
    abs_min = float(max(0.0, heading_offset_abs_min))
    if abs_min > 0.0 and heading_min <= heading_max:
        candidates = [v for v in range(heading_min, heading_max + 1) if abs(v) >= abs_min]
        if candidates:
            heading_offset = float(np.random.choice(candidates))
        else:
            heading_offset = np.random.uniform(heading_offset_min, heading_offset_max)
    else:
        heading_offset = np.random.uniform(heading_offset_min, heading_offset_max)

    miss_distance = radius * abs(np.sin(np.radians(heading_offset)))
    rz = base_rz + heading_offset
    return px, pz, ry, rz, heading_offset, miss_distance


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
        self.prev_agl = None
        self.last_action_info = {}

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
            s["target_clock"][0],
            s["target_clock"][1],
            s["target_clock"][2],
            s["target_clock"][3],
            s["closing_speed"],
            s["rel_vel_clock"][0],
            s["rel_vel_clock"][1],
            s["rel_vel_clock"][2],
            s["rel_vel_clock"][3],
            s["rel_vel_forward"],
            s["turn_rate_clock"][0],
            s["turn_rate_clock"][1],
            s["turn_rate_clock"][2],
            s["turn_rate_clock"][3],
            s["turn_rate_roll"],
            s["clock_validity"],
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
        s[4:8] = np.clip(s[4:8], 0.0, 1.0)
        s[8] = np.tanh(s[8] / CLOSING_TANH_SCALE)
        s[9:13] = np.tanh(s[9:13] / REL_VEL_TANH_SCALE)
        s[13] = np.tanh(s[13] / REL_VEL_TANH_SCALE)
        s[14:18] = np.tanh(s[14:18] / ROC_ANG_VEL_TANH_SCALE)
        s[18] = np.tanh(s[18] / ROC_ANG_VEL_TANH_SCALE)
        s[19] = np.clip(s[19], 0.0, 1.0)
        s[20] = np.clip(s[20], -1.0, 1.0)
        s[21] = np.tanh(s[21] / AGL_TANH_SCALE)
        s[22] = np.tanh(s[22] / ALT_ERROR_TANH_SCALE)
        return s.astype(np.float32)

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def reset(self):
        px, pz, ry, rz, heading_offset, target_miss_distance = calculate_new_loc(
            self.phase["spawn_radius_min"],
            self.phase["spawn_radius_max"],
            self.phase["heading_offset_min"],
            self.phase["heading_offset_max"],
            self.phase.get("heading_offset_abs_min", 0.0),
        )
        py = 50.0

        return self._send_reset_values(px, py, pz, ry, rz, heading_offset, target_miss_distance)

    def reset_with_config(
        self,
        radius_min,
        radius_max,
        heading_offset_min,
        heading_offset_max,
        heading_offset_abs_min=0.0,
        target_y=50.0,
    ):
        """
        PN saglik testleri icin reset araligini komut satirindan degistirir.

        Training tarafinda aktif faz ne ise o kalir. Bu metot sadece klasik gudum
        testinde 300m gibi ozel senaryolari hizli denemek icin kullanilir.
        """
        px, pz, ry, rz, heading_offset, target_miss_distance = calculate_new_loc(
            radius_min,
            radius_max,
            heading_offset_min,
            heading_offset_max,
            heading_offset_abs_min,
        )
        return self._send_reset_values(px, target_y, pz, ry, rz, heading_offset, target_miss_distance)

    def _send_reset_values(self, px, py, pz, ry, rz, heading_offset, target_miss_distance):
        """Reset paketini Unity'ye yollar ve ilk state bilgisini standart sekilde hazirlar."""
        self.episode_id += 1
        self.done = False
        self.step_count = 0
        self.last_action_info = {}

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
        self.prev_agl = float(raw_state["states"]["agl"])
        start_info = self.build_info(raw_state)

        start_info.update({
            "phase_id": self.phase_id,
            "phase_name": self.phase["name"],
            "reset_px": px,
            "reset_py": py,
            "reset_pz": pz,
            "reset_ry": ry,
            "reset_rz": rz,
            "reset_heading_offset": heading_offset,
            "reset_target_miss_distance": target_miss_distance,
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

        target_clock = np.asarray(states.get("target_clock", [0.0, 0.0, 0.0, 0.0]), dtype=np.float32)
        rel_vel_clock = np.asarray(states.get("rel_vel_clock", [0.0, 0.0, 0.0, 0.0]), dtype=np.float32)
        turn_rate_clock = np.asarray(states.get("turn_rate_clock", [0.0, 0.0, 0.0, 0.0]), dtype=np.float32)
        target_clock = np.clip(target_clock, 0.0, 1.0)
        clock_validity = float(np.clip(states.get("clock_validity", 1.0), 0.0, 1.0))
        rel_vel_forward = float(states.get("rel_vel_forward", states.get("rel_vel_ref", [0.0, 0.0, 0.0])[2]))
        turn_rate_roll = float(states.get("turn_rate_roll", states.get("turn_rate_ref", [0.0, 0.0, 0.0])[2]))
        ang_vel_mag = float(np.sqrt(np.sum(np.square(turn_rate_clock)) + turn_rate_roll ** 2))
        roll_rate_mag = abs(turn_rate_roll)
        roll_error_deg = abs(float(raw_state.get("telemetry", {}).get("roll_error_deg", 0.0)))
        rocket_vel_world = telemetry.get("rocket_vel_world", [0.0, 0.0, 0.0])
        rocket_vy = 0.0
        if isinstance(rocket_vel_world, (list, tuple)) and len(rocket_vel_world) >= 2:
            rocket_vy = float(rocket_vel_world[1])
        thrust_cmd_value = 0.5 * (MIN_THRUST + MAX_THRUST)
        thrust_cmd_norm = 0.0
        clock_cmd = np.zeros(4, dtype=np.float32)
        if denorm_action is not None and len(denorm_action) >= 5:
            thrust_cmd_value = float(denorm_action[0])
            thrust_cmd_norm = float(np.clip(
                ((denorm_action[0] - MIN_THRUST) / max(MAX_THRUST - MIN_THRUST, 1e-6)) * 2.0 - 1.0,
                -1.0,
                1.0,
            ))
            clock_cmd = np.clip(
                np.asarray(denorm_action[1:5], dtype=np.float32) / max(DISCRETE_TURN_STRENGTH, 1e-6),
                0.0,
                1.0,
            )

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
        prev_agl = agl if self.prev_agl is None else self.prev_agl
        delta_agl = float(np.clip(
            agl - prev_agl,
            -phase["low_alt_agl_progress_clip"],
            phase["low_alt_agl_progress_clip"],
        ))
        low_alt_window = float(np.clip(
            (phase["low_alt_safe_agl"] - agl) / max(phase["low_alt_safe_agl"], 1e-6),
            0.0,
            1.0,
        ))
        low_alt_launch_window = float(np.clip(
            1.0 - (self.step_count / max(phase["low_alt_escape_steps"], 1)),
            0.0,
            1.0,
        ))
        low_alt_time_scale = 0.50 + 0.50 * low_alt_launch_window
        climb_norm = float(np.clip(
            rocket_vy / max(phase["low_alt_climb_speed"], 1e-6),
            -1.0,
            1.0,
        ))
        sink_norm = max(-climb_norm, 0.0)
        agl_progress_norm = float(np.clip(
            delta_agl / max(phase["low_alt_agl_progress_clip"], 1e-6),
            -1.0,
            1.0,
        ))
        agl_loss_norm = max(-agl_progress_norm, 0.0)
        low_alt_descent_score = low_alt_window * low_alt_time_scale * (
            0.65 * sink_norm + 0.35 * agl_loss_norm
        )

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
        positive_guidance_reward = max(theta_progress_reward, 0.0) + max(alpha_beta_reward, 0.0)
        low_altitude_guidance_discount = min(
            positive_guidance_reward,
            phase["low_alt_guidance_discount_gain"] * low_alt_descent_score * positive_guidance_reward,
        )
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
        close_angle_distance_window = float(np.clip(
            1.0 - (distance / max(phase["close_angle_distance"], 1e-6)),
            0.0,
            1.0,
        ))
        close_angle_theta_window = float(np.clip(
            (theta_deg - phase["close_angle_theta_start_deg"])
            / max(phase["close_angle_theta_span_deg"], 1e-6),
            0.0,
            1.0,
        ))
        close_angle_penalty = (
            phase["close_angle_penalty_gain"]
            * close_angle_distance_window
            * (close_angle_theta_window ** 2)
            * (0.80 + 0.20 * max(-signed_closing, 0.0))
        )
        turn_need_window = float(np.clip(
            theta_deg / max(phase["turn_toward_theta_deg"], 1e-6),
            0.0,
            1.0,
        ))
        turn_rate_clock_norm = np.clip(
            turn_rate_clock / max(phase["turn_toward_rate_clip"], 1e-6),
            0.0,
            1.0,
        )
        target_clock_mass = max(float(np.sum(target_clock)), 1e-6)
        opposite_target_clock = np.asarray(
            [target_clock[1], target_clock[0], target_clock[3], target_clock[2]],
            dtype=np.float32,
        )
        opposite_clock_cmd = np.asarray(
            [clock_cmd[1], clock_cmd[0], clock_cmd[3], clock_cmd[2]],
            dtype=np.float32,
        )
        turn_toward_score = float(np.clip(
            (float(np.dot(target_clock, turn_rate_clock_norm)) / target_clock_mass) * turn_need_window,
            0.0,
            1.0,
        ))
        clock_reward_validity = max(clock_validity, phase["clock_reward_validity_floor"])
        clock_action_alignment_score = float(np.clip(
            (float(np.dot(target_clock, clock_cmd)) / target_clock_mass) * turn_need_window,
            0.0,
            1.0,
        ))
        clock_wrong_channel_score = float(np.clip(
            (float(np.dot(target_clock, opposite_clock_cmd)) / target_clock_mass) * turn_need_window,
            0.0,
            1.0,
        ))
        clock_coactivation_score = float(np.clip(
            min(clock_cmd[0], clock_cmd[1]) + min(clock_cmd[2], clock_cmd[3]),
            0.0,
            1.0,
        ))
        turn_toward_reward = phase["turn_toward_gain"] * turn_toward_score
        clock_action_alignment_reward = (
            phase["clock_action_alignment_gain"]
            * clock_action_alignment_score
            * clock_reward_validity
        )
        clock_wrong_channel_penalty = (
            phase["clock_wrong_channel_penalty_gain"]
            * clock_wrong_channel_score
            * clock_reward_validity
        )
        clock_coactivation_penalty = phase["clock_coactivation_penalty_gain"] * clock_coactivation_score

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
        late_floor_penalty = 0.0
        soft_ceiling_penalty = 0.0
        thrust_gate_penalty = 0.0
        bad_thrust_angle_penalty = 0.0
        low_altitude_escape_reward = 0.0
        low_altitude_control_penalty = 0.0
        low_altitude_sink_penalty = 0.0
        turn_cmd_mag = min(float(np.sum(clock_cmd)), 2.0) / 2.0

        if agl < phase["soft_floor"] and self.step_count > phase["soft_floor_grace_steps"]:
            soft_floor_penalty = phase["soft_floor_gain"] * (phase["soft_floor"] - agl)
        if self.step_count > phase["late_floor_step"]:
            late_floor_deficit = float(np.clip(
                (phase["late_floor_agl"] - agl) / max(phase["late_floor_agl"], 1e-6),
                0.0,
                1.0,
            ))
            late_floor_penalty = phase["late_floor_penalty_gain"] * (late_floor_deficit ** 2)
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
            thrust_gate_penalty *= 1.0 - (
                phase["low_alt_thrust_gate_relief"]
                * low_alt_window
                * low_alt_launch_window
            )
        if self.step_count > phase["bad_thrust_angle_step"]:
            bad_thrust_excess = float(np.clip(
                (thrust_cmd_value - phase["bad_thrust_angle_min_thrust"])
                / max(MAX_THRUST - phase["bad_thrust_angle_min_thrust"], 1e-6),
                0.0,
                1.0,
            ))
            bad_thrust_theta_window = float(np.clip(
                (theta_deg - phase["bad_thrust_angle_theta_start_deg"])
                / max(phase["bad_thrust_angle_theta_span_deg"], 1e-6),
                0.0,
                1.0,
            ))
            bad_thrust_angle_penalty = (
                phase["bad_thrust_angle_penalty_gain"]
                * bad_thrust_excess
                * (bad_thrust_theta_window ** 2)
            )

        if phase["low_alt_escape_gain"] > 0.0 and low_alt_window > 0.0:
            low_altitude_escape_reward = (
                phase["low_alt_escape_gain"]
                * low_alt_window
                * (0.60 * climb_norm + 0.40 * agl_progress_norm)
                * low_alt_time_scale
            )
        if phase["low_alt_control_penalty_gain"] > 0.0 and low_alt_window > 0.0:
            low_altitude_control_penalty = (
                phase["low_alt_control_penalty_gain"]
                * low_alt_window
                * turn_cmd_mag
                * low_alt_time_scale
            )
        if phase["low_alt_sink_penalty_gain"] > 0.0 and low_alt_descent_score > 0.0:
            low_altitude_sink_penalty = (
                phase["low_alt_sink_penalty_gain"]
                * low_alt_descent_score
                * (0.75 + 0.25 * turn_cmd_mag)
            )

        reward += distance_reward
        reward += alignment_reward
        reward += closing_reward
        reward += theta_progress_reward
        reward += alpha_beta_reward
        reward -= low_altitude_guidance_discount
        reward -= axis_error_penalty
        reward += direction_bonus
        reward += angle_focus_reward
        reward -= close_angle_penalty
        reward += turn_toward_reward
        reward += clock_action_alignment_reward
        reward -= clock_wrong_channel_penalty
        reward -= clock_coactivation_penalty
        reward += near_success_bonus
        reward -= reverse_penalty
        reward -= angular_penalty
        reward += altitude_reward
        reward -= soft_floor_penalty
        reward -= late_floor_penalty
        reward -= soft_ceiling_penalty
        reward -= thrust_gate_penalty
        reward -= bad_thrust_angle_penalty
        reward += low_altitude_escape_reward
        reward -= low_altitude_control_penalty
        reward -= low_altitude_sink_penalty

        near_miss_candidate = (
            self.step_count > phase["near_miss_grace_steps"]
            and distance <= phase["near_miss_distance"]
            and theta_deg >= phase["near_miss_theta_deg"]
        )

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
        self.prev_agl = agl

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
            "reward_close_angle_penalty": float(close_angle_penalty),
            "reward_turn_toward": float(turn_toward_reward),
            "reward_clock_action_alignment": float(clock_action_alignment_reward),
            "reward_clock_wrong_channel": float(clock_wrong_channel_penalty),
            "reward_clock_coactivation": float(clock_coactivation_penalty),
            "reward_near_success_bonus": float(near_success_bonus),
            "reward_reverse_penalty": float(reverse_penalty),
            "reward_roll_penalty": float(roll_penalty),
            "reward_angular_penalty": float(angular_penalty),
            "reward_altitude": float(altitude_reward),
            "reward_soft_floor_penalty": float(soft_floor_penalty),
            "reward_late_floor_penalty": float(late_floor_penalty),
            "reward_soft_ceiling_penalty": float(soft_ceiling_penalty),
            "reward_thrust_gate_penalty": float(thrust_gate_penalty),
            "reward_bad_thrust_angle_penalty": float(bad_thrust_angle_penalty),
            "reward_low_altitude_escape": float(low_altitude_escape_reward),
            "reward_low_altitude_control": float(low_altitude_control_penalty),
            "reward_low_altitude_sink_penalty": float(low_altitude_sink_penalty),
            "reward_low_altitude_guidance_discount": float(low_altitude_guidance_discount),
            "reward_terminal": float(terminal_reward),
            "near_miss_candidate": 1.0 if near_miss_candidate else 0.0,
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
        info["near_miss_candidate"] = reward_info["near_miss_candidate"]

        for key in REWARD_BREAKDOWN_KEYS:
            info[key] = reward_info[key]

        self.done = done
        return normalized_state, reward, done, info

    def step_direct_action(self, denorm_action, action_label="scripted_direct"):
        """
        Klasik gudum / scripted controller testleri icin dogrudan Unity action'i gonderir.

        Bu metot PPO action normalizasyonunu kullanmaz. Boylece PN gibi algoritmalar,
        Unity'nin bekledigi fiziksel komutlari dogrudan test edebilir:
        [thrust, clock_12, clock_6, clock_3, clock_9].
        """
        values = np.asarray(denorm_action, dtype=np.float32).reshape(-1)
        if len(values) < 5:
            raise ValueError("Direct action icin 5 deger gerekir: thrust, clock_12, clock_6, clock_3, clock_9")

        values = values[:5].astype(np.float32)
        self.step_count += 1

        clock_12_net = float(values[1] - values[2])
        clock_3_net = float(values[3] - values[4])
        self.last_action_info = {
            "action_direction_id": -1,
            "turn_direction_id": -1,
            "turn_direction_name": action_label,
            "action_direction_clock12": clock_12_net,
            "action_direction_clock3": clock_3_net,
            "turn_strength": float(np.sqrt(clock_12_net ** 2 + clock_3_net ** 2)),
        }

        action_dict = {
            "episode_id": self.episode_id,
            "step_id": self.step_count,
            "type": "action",
            "values": [float(v) for v in values],
        }

        self.connect.send_packet(action_dict)

        raw_state = self.read_state()
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)

        reward, done, reward_info = self.calculate_reward(raw_state, denorm_action=values)
        info = self.build_info(
            raw_state=raw_state,
            denorm_action=values,
            reward=reward,
            done=done,
            done_reason=reward_info["done_reason"],
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
        info["near_miss_candidate"] = reward_info["near_miss_candidate"]

        for key in REWARD_BREAKDOWN_KEYS:
            info[key] = reward_info[key]

        self.done = done
        return raw_state, normalized_state, reward, done, info

    # ------------------------------------------------------------------
    # YARDIMCI METODLAR
    # ------------------------------------------------------------------

    def denormalize_action(self, action):
        a = np.asarray(action, dtype=np.float32)
        thrust_norm = float(np.clip(a[0], -1.0, 1.0)) if len(a) > 0 else 0.0
        direction_id = int(np.clip(np.rint(a[1] if len(a) > 1 else 0.0), 0, TURN_DIRECTION_COUNT - 1))
        direction_vector = TURN_DIRECTION_VECTORS[direction_id]

        thrust = MIN_THRUST + ((thrust_norm + 1.0) / 2.0) * (MAX_THRUST - MIN_THRUST)
        clock_12_net = float(direction_vector[0]) * DISCRETE_TURN_STRENGTH
        clock_3_net = float(direction_vector[1]) * DISCRETE_TURN_STRENGTH

        clock_12_cmd = max(0.0, clock_12_net)
        clock_6_cmd = max(0.0, -clock_12_net)
        clock_3_cmd = max(0.0, clock_3_net)
        clock_9_cmd = max(0.0, -clock_3_net)

        self.last_action_info = {
            "action_direction_id": direction_id,
            "turn_direction_id": direction_id,
            "turn_direction_name": TURN_DIRECTION_NAMES[direction_id],
            "action_direction_clock12": clock_12_net,
            "action_direction_clock3": clock_3_net,
            "turn_strength": DISCRETE_TURN_STRENGTH,
        }

        return [
            float(thrust),
            float(clock_12_cmd),
            float(clock_6_cmd),
            float(clock_3_cmd),
            float(clock_9_cmd),
        ]

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
            "target_clock_12": float(s["target_clock"][0]),
            "target_clock_6": float(s["target_clock"][1]),
            "target_clock_3": float(s["target_clock"][2]),
            "target_clock_9": float(s["target_clock"][3]),
            "rel_vel_clock_12": float(s["rel_vel_clock"][0]),
            "rel_vel_clock_6": float(s["rel_vel_clock"][1]),
            "rel_vel_clock_3": float(s["rel_vel_clock"][2]),
            "rel_vel_clock_9": float(s["rel_vel_clock"][3]),
            "rel_vel_forward": float(s["rel_vel_forward"]),
            "turn_rate_clock_12": float(s["turn_rate_clock"][0]),
            "turn_rate_clock_6": float(s["turn_rate_clock"][1]),
            "turn_rate_clock_3": float(s["turn_rate_clock"][2]),
            "turn_rate_clock_9": float(s["turn_rate_clock"][3]),
            "turn_rate_roll": float(s["turn_rate_roll"]),
            "clock_validity": float(s["clock_validity"]),
            "forward_up_dot": float(s["forward_up_dot"]),
            "agl": float(s["agl"]),
            "alt_error": float(s["alt_error"]),
            "grounded_flag": float(s["grounded_flag"]),
        }

        info.update(flatten_telemetry(telemetry))

        if denorm_action is not None:
            info["thrust"] = denorm_action[0]
            info["clock_12_cmd"] = denorm_action[1]
            info["clock_6_cmd"] = denorm_action[2]
            info["clock_3_cmd"] = denorm_action[3]
            info["clock_9_cmd"] = denorm_action[4]
        else:
            info["thrust"] = None
            info["clock_12_cmd"] = None
            info["clock_6_cmd"] = None
            info["clock_3_cmd"] = None
            info["clock_9_cmd"] = None

        info.update(self.last_action_info)

        return info

    def close(self):
        self.connect.close()
