from datetime import datetime

import connector
import numpy as np

CONTROL_MODE = "direct_accel"

CLOCK_STATE_KEYS = [
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

DIRECT_STATE_KEYS = [
    "distance",
    "rel_dir_right",
    "rel_dir_up",
    "rel_dir_forward",
    "rel_vel_right",
    "rel_vel_up",
    "rel_vel_forward",
    "rocket_vel_right",
    "rocket_vel_up",
    "rocket_vel_forward",
    "closing_speed",
    "theta_rad",
    "agl",
    "alt_error",
    "target_speed",
    "rocket_speed",
]

GUIDANCE_ACCEL_STATE_KEYS = DIRECT_STATE_KEYS

BODY_ACCEL_STATE_KEYS = [
    "distance",
    "rel_dir_body_right",
    "rel_dir_body_up",
    "rel_dir_body_forward",
    "rel_vel_body_right",
    "rel_vel_body_up",
    "rel_vel_body_forward",
    "rocket_vel_body_right",
    "rocket_vel_body_up",
    "rocket_vel_body_forward",
    "closing_speed",
    "theta_rad",
    "agl",
    "alt_error",
    "target_speed",
    "rocket_speed",
]

STATE_KEYS = (
    GUIDANCE_ACCEL_STATE_KEYS
    if CONTROL_MODE == "guidance_accel"
    else BODY_ACCEL_STATE_KEYS
    if CONTROL_MODE == "body_accel"
    else DIRECT_STATE_KEYS if CONTROL_MODE == "direct_accel"
    else CLOCK_STATE_KEYS
)

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

# Direct RL action artik serbest dunya ivmesi degil.
# Ajan hedef hattina gore kucuk aim offset (sag/yukari sapma) ve pozitif ileri ivme secer.
# Boylece roket fiziksel olarak burnunun tersine veya 90 derece yanina itilmez.
DIRECT_ACTION_MAX_ACCEL = 55.0
DIRECT_ACTION_MIN_ACCEL = 20.0
DIRECT_ACTION_RIGHT_AIM_OFFSET = 0.75
DIRECT_ACTION_UP_AIM_OFFSET = 2.15
DIRECT_ACTION_AIM_OFFSET = DIRECT_ACTION_RIGHT_AIM_OFFSET
DIRECT_ACTION_MARKER = -7777.0
GUIDANCE_ACCEL_ACTION_MARKER = -5555.0
GUIDANCE_ACCEL_LATERAL_MAX_ACCEL = 24.0
GUIDANCE_ACCEL_UP_MAX_ACCEL = 22.0
GUIDANCE_ACCEL_FORWARD_MIN_ACCEL = 6.0
GUIDANCE_ACCEL_FORWARD_MAX_ACCEL = 28.0
GUIDANCE_ACCEL_MAX_ACCEL = 42.0
GUIDANCE_ACCEL_LAUNCH_SAFE_AGL = 18.0
GUIDANCE_ACCEL_LAUNCH_SAFE_STEPS = 120
GUIDANCE_ACCEL_LAUNCH_MIN_LATERAL_SCALE = 0.10
GUIDANCE_ACCEL_LAUNCH_MIN_FORWARD_SCALE = 0.18
GUIDANCE_ACCEL_LAUNCH_UP_BIAS = 10.0
GUIDANCE_ACCEL_LAUNCH_MIN_UP_ACCEL = 24.0
BODY_ACCEL_ACTION_MARKER = -6666.0
BODY_ACCEL_LATERAL_MAX_ACCEL = 32.0
BODY_ACCEL_FORWARD_MIN_ACCEL = 24.0
BODY_ACCEL_FORWARD_MAX_ACCEL = 58.0
BODY_ACCEL_LAUNCH_SAFE_AGL = 8.0
BODY_ACCEL_LAUNCH_SAFE_STEPS = 80
BODY_ACCEL_LAUNCH_MIN_LATERAL_SCALE = 0.20
DIRECT_LAUNCH_SAFE_AGL = 8.0
DIRECT_LAUNCH_SAFE_STEPS = 80
DIRECT_LAUNCH_UP_BIAS = 0.75

ACTION_KEYS = (
    ["accel_right", "accel_up", "accel_forward"]
    if CONTROL_MODE == "guidance_accel"
    else ["body_right_accel", "body_up_accel", "body_forward_accel"]
    if CONTROL_MODE == "body_accel"
    else ["aim_right", "aim_up", "forward_accel"]
    if CONTROL_MODE == "direct_accel"
    else ["thrust", "turn_direction"]
)

PYTHON_STEP_LOG_KEYS = [
    "episode_return_so_far",
    "action_logp",
    "value_pred",
    "action_source",
    "lead_time",
    "lead_distance",
    "lead_alignment",
    "final_approach_aim_alignment",
    "action_norm_0",
    "action_norm_1",
    "action_norm_2",
    "action_direction_id",
    "action_direction_clock12",
    "action_direction_clock3",
    "direct_accel_world_x",
    "direct_accel_world_y",
    "direct_accel_world_z",
    "direct_accel_cmd_right",
    "direct_accel_cmd_up",
    "direct_accel_cmd_forward",
    "direct_launch_guard",
    "altitude_schedule_progress",
    "altitude_schedule_desired_agl",
    "altitude_schedule_deficit",
    "altitude_schedule_horizontal_distance",
]

REWARD_BREAKDOWN_KEYS = [
    "reward_step_penalty",
    "reward_distance",
    "reward_alignment",
    "reward_theta_progress",
    "reward_closing",
    "reward_lead_alignment",
    "reward_final_approach",
    "reward_altitude_schedule",
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
    ("aim_point_pos_world", ("x", "y", "z")),
    ("aim_rel_pos_world", ("x", "y", "z")),
    ("aim_rel_dir_world", ("x", "y", "z")),
    ("target_rel_pos_world", ("x", "y", "z")),
    ("target_rel_dir_world", ("x", "y", "z")),
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
    "aim_lead_time",
    "aim_distance",
    "target_distance",
    "target_closing_speed",
    "target_theta_deg",
    "target_alignment",
    "target_hit_trigger",
    "target_hit_ellipsoid",
    "target_hit_ellipsoid_value",
    "roll_error_deg",
    "beta_validity",
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
    "step_penalty": -0.0085,
    "distance_gain": 0.30,
    "distance_progress_scale": 5.0,
    "alignment_gain": 0.06,
    "alignment_reward_floor": 0.20,
    "theta_progress_gain": 0.075,
    "theta_regress_penalty_scale": 1.15,
    "theta_progress_scale_deg": 20.0,
    "closing_gain": 0.12,
    "closing_speed_scale": 80.0,
    "lead_time_min": 0.0,
    "lead_time_max": 0.0,
    "lead_time_distance_scale": 1.0,
    "lead_reward_distance": 0.0,
    "lead_alignment_gain": 0.0,
    "lead_alignment_reward_floor": 0.20,
    "final_approach_gain": 0.27,
    "final_approach_distance": 80.0,
    "final_approach_alignment_floor": 0.70,
    "final_approach_lead_blend": 0.0,
    "final_approach_bad_angle_gain": 0.045,
    "final_approach_bad_closing_gain": 0.045,
    "final_approach_bad_progress_gain": 0.045,
    "altitude_schedule_gain": 0.03,
    "altitude_schedule_power": 0.70,
    "altitude_schedule_target_agl": 100.0,
    "altitude_schedule_tolerance": 5.0,
    "altitude_schedule_grace_steps": 80,
    "min_agl": 0.60,
    "low_agl_grace_steps": 80,
    "collision_grace_steps": 8,
    "max_altitude": 180.0,
    "max_theta_deg": 110.0,
    "bad_angle_grace_steps": 25,
    "wrong_way_alignment": -0.35,
    "wrong_way_closing_speed": -8.0,
    "wrong_way_grace_steps": 80,
    "missed_intercept_distance": 16.0,
    "missed_intercept_recede_distance": 8.0,
    "missed_intercept_closing_speed": -4.0,
    "near_miss_distance": 16.0,
    "hit_success_distance": 5.0,
    "success_distance": 10.0,
    "success_alignment": 0.866,
    "success_min_closing": -1.0,
    "guided_success_enabled": False,
    "distance_success_fallback": False,
    "success_reward": 120.0,
    "collision_penalty": -80.0,
    "low_altitude_penalty": -60.0,
    "high_altitude_penalty": -60.0,
    "bad_angle_penalty": -50.0,
    "wrong_way_penalty": -50.0,
    "missed_intercept_penalty": -70.0,
    "timeout_penalty": -55.0,
}

ACTIVE_PHASE_CONFIG = {
    "name": "v16_0_4_phase_1_altitude_schedule_y100",
    "spawn_radius_min": 700.0,
    "spawn_radius_max": 700.0,
    "target_y": 100.0,
    "heading_offset_min": -5.0,
    "heading_offset_max": 5.0,
    "heading_offset_abs_min": 1.0,
    "balanced_heading_offsets": True,
    "balanced_heading_offset_order": [1, 2, 3, 4, 5],
    "balanced_heading_sign_order": [-1, 1],
    "max_step": 1200,
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


def valid_heading_offsets(
    heading_offset_min=0.0,
    heading_offset_max=0.0,
    heading_offset_abs_min=0.0,
):
    heading_min = int(np.ceil(heading_offset_min))
    heading_max = int(np.floor(heading_offset_max))
    abs_min = float(max(0.0, heading_offset_abs_min))

    if abs_min > 0.0 and heading_min <= heading_max:
        candidates = [v for v in range(heading_min, heading_max + 1) if abs(v) >= abs_min]
        if candidates:
            return [float(v) for v in candidates]

    return None


def loc_from_theta_radius_heading(theta, radius, heading_offset):
    px = radius * np.cos(theta)
    pz = radius * np.sin(theta)
    ry = 180.0
    base_rz = 90.0 - np.degrees(np.arctan2(pz, px))
    miss_distance = radius * abs(np.sin(np.radians(heading_offset)))
    rz = base_rz + heading_offset
    return px, pz, ry, rz, heading_offset, miss_distance


def calculate_new_loc(
    radius_min,
    radius_max,
    heading_offset_min=0.0,
    heading_offset_max=0.0,
    heading_offset_abs_min=0.0,
):
    theta = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(radius_min, radius_max)

    candidates = valid_heading_offsets(
        heading_offset_min,
        heading_offset_max,
        heading_offset_abs_min,
    )
    if candidates:
        heading_offset = float(np.random.choice(candidates))
    else:
        heading_offset = np.random.uniform(heading_offset_min, heading_offset_max)

    return loc_from_theta_radius_heading(theta, radius, heading_offset)


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
        self.reset_horizontal_distance = None
        self.min_distance_seen = None
        self.prev_theta = None
        self.prev_alpha_abs = None
        self.prev_beta_abs = None
        self.prev_agl = None
        self.last_raw_state = None
        self.last_action_info = {}
        self._balanced_heading_index = 0
        self._balanced_heading_pair = None

    # STATE

    def read_state(self):
        return self.connect.read_packet()

    def parse_state(self, raw_state):
        if CONTROL_MODE == "guidance_accel":
            return self.parse_direct_state(raw_state)
        if CONTROL_MODE == "body_accel":
            return self.parse_body_accel_state(raw_state)
        if CONTROL_MODE == "direct_accel":
            return self.parse_direct_state(raw_state)

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

    def parse_direct_state(self, raw_state):
        """Direct-accel mimarisi icin sade state vektoru kurar."""
        s = raw_state["states"]
        telemetry = raw_state.get("telemetry", {})

        rel_pos = self._telemetry_vec(telemetry, "rel_pos_world")
        rel_vel = self._telemetry_vec(telemetry, "rel_vel_world")
        rocket_vel = self._telemetry_vec(telemetry, "rocket_vel_world")
        right_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_right_world"), np.array([1.0, 0.0, 0.0]))
        up_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_up_world"), np.array([0.0, 1.0, 0.0]))
        forward_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_forward_world"), np.array([0.0, 0.0, 1.0]))

        distance = float(s["distance"])
        rel_dir = self._safe_unit(rel_pos, forward_ref)
        rocket_speed = float(np.linalg.norm(rocket_vel))

        return np.array([
            distance,
            float(np.dot(rel_dir, right_ref)),
            float(np.dot(rel_dir, up_ref)),
            float(np.dot(rel_dir, forward_ref)),
            float(np.dot(rel_vel, right_ref)),
            float(np.dot(rel_vel, up_ref)),
            float(np.dot(rel_vel, forward_ref)),
            float(np.dot(rocket_vel, right_ref)),
            float(np.dot(rocket_vel, up_ref)),
            float(np.dot(rocket_vel, forward_ref)),
            float(s["closing_speed"]),
            float(s["theta_rad"]),
            float(s["agl"]),
            float(s["alt_error"]),
            float(telemetry.get("target_speed", TARGET_VELOCITY)),
            rocket_speed,
        ], dtype=np.float32)

    def parse_body_accel_state(self, raw_state):
        """Body-accel SAC icin hedefi roket govde frame'inde okuyan state vektoru kurar."""
        s = raw_state["states"]
        telemetry = raw_state.get("telemetry", {})

        rel_pos = self._telemetry_vec(telemetry, "rel_pos_world")
        rel_vel = self._telemetry_vec(telemetry, "rel_vel_world")
        rocket_vel = self._telemetry_vec(telemetry, "rocket_vel_world")
        body_right = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_right_world"),
            np.array([1.0, 0.0, 0.0]),
        )
        body_up = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_up_world"),
            np.array([0.0, 0.0, 1.0]),
        )
        body_forward = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_forward_world"),
            np.array([0.0, 1.0, 0.0]),
        )

        distance = float(s["distance"])
        rel_dir = self._safe_unit(rel_pos, body_forward)
        rocket_speed = float(np.linalg.norm(rocket_vel))

        return np.array([
            distance,
            float(np.dot(rel_dir, body_right)),
            float(np.dot(rel_dir, body_up)),
            float(np.dot(rel_dir, body_forward)),
            float(np.dot(rel_vel, body_right)),
            float(np.dot(rel_vel, body_up)),
            float(np.dot(rel_vel, body_forward)),
            float(np.dot(rocket_vel, body_right)),
            float(np.dot(rocket_vel, body_up)),
            float(np.dot(rocket_vel, body_forward)),
            float(s["closing_speed"]),
            float(s["theta_rad"]),
            float(s["agl"]),
            float(s["alt_error"]),
            float(telemetry.get("target_speed", TARGET_VELOCITY)),
            rocket_speed,
        ], dtype=np.float32)

    @staticmethod
    def _telemetry_vec(telemetry, name):
        values = telemetry.get(name, [0.0, 0.0, 0.0])
        if not isinstance(values, (list, tuple)) or len(values) < 3:
            return np.zeros(3, dtype=np.float32)
        return np.asarray(values[:3], dtype=np.float32)

    def _target_horizontal_distance(self, telemetry, fallback_distance):
        rocket_pos = self._telemetry_vec(telemetry, "rocket_point_pos_world")
        target_pos = self._telemetry_vec(telemetry, "target_point_pos_world")
        delta = target_pos - rocket_pos
        horizontal = float(np.linalg.norm(delta[[0, 2]]))
        if horizontal <= 1e-6:
            return float(fallback_distance)
        return horizontal

    @staticmethod
    def _safe_unit(value, fallback):
        value = np.asarray(value, dtype=np.float32)
        norm = float(np.linalg.norm(value))
        if norm <= 1e-6:
            return np.asarray(fallback, dtype=np.float32)
        return value / norm

    @staticmethod
    def _clamp_magnitude(value, max_magnitude):
        """Vektor buyuklugunu Unity'ye gitmeden once sinirlar; log ile fizik ayni kalir."""
        value = np.asarray(value, dtype=np.float32)
        norm = float(np.linalg.norm(value))
        if norm <= 1e-6 or norm <= max_magnitude:
            return value
        return value * (float(max_magnitude) / norm)

    @staticmethod
    def _is_accel_action_packet(values):
        """Unity marker'li ivme paketlerini reward tarafinda clock action gibi okumamayi saglar."""
        if values is None or len(values) < 7:
            return False

        marker = float(values[0])
        return any(
            abs(marker - expected) <= 0.5
            for expected in (
                DIRECT_ACTION_MARKER,
                BODY_ACCEL_ACTION_MARKER,
                GUIDANCE_ACCEL_ACTION_MARKER,
            )
        )

    def normalize_state(self, vector_state):
        if CONTROL_MODE in ("direct_accel", "body_accel", "guidance_accel"):
            return self.normalize_direct_state(vector_state)

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

    def normalize_direct_state(self, vector_state):
        """Direct state icin her alani basit ve okunur araliklara sikistirir."""
        s = vector_state.copy()
        s[0] = np.tanh(s[0] / 300.0)
        s[1:4] = np.clip(s[1:4], -1.0, 1.0)
        s[4:7] = np.tanh(s[4:7] / 60.0)
        s[7:10] = np.tanh(s[7:10] / 100.0)
        s[10] = np.tanh(s[10] / 60.0)
        s[11] = np.clip(s[11] / np.pi, 0.0, 1.0)
        s[12] = np.tanh(s[12] / 100.0)
        s[13] = np.tanh(s[13] / 100.0)
        s[14] = np.tanh(s[14] / 50.0)
        s[15] = np.tanh(s[15] / 120.0)
        return s.astype(np.float32)

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def _balanced_heading_magnitudes(self):
        candidates = valid_heading_offsets(
            self.phase["heading_offset_min"],
            self.phase["heading_offset_max"],
            self.phase.get("heading_offset_abs_min", 0.0),
        )
        if not candidates:
            return []

        available = {int(abs(value)) for value in candidates if abs(value) > 0.0}
        configured = self.phase.get("balanced_heading_offset_order")
        if configured:
            ordered = [int(abs(value)) for value in configured if int(abs(value)) in available]
            if ordered:
                return ordered

        return sorted(available)

    def _next_balanced_heading_loc(self):
        magnitudes = self._balanced_heading_magnitudes()
        sign_order = [int(np.sign(value)) for value in self.phase.get("balanced_heading_sign_order", [1, -1])]
        sign_order = [value for value in sign_order if value != 0]

        if not magnitudes or not sign_order:
            return calculate_new_loc(
                self.phase["spawn_radius_min"],
                self.phase["spawn_radius_max"],
                self.phase["heading_offset_min"],
                self.phase["heading_offset_max"],
                self.phase.get("heading_offset_abs_min", 0.0),
            )

        pair_size = len(sign_order)
        sequence_index = self._balanced_heading_index
        magnitude = magnitudes[(sequence_index // pair_size) % len(magnitudes)]
        sign = sign_order[sequence_index % pair_size]
        self._balanced_heading_index = (self._balanced_heading_index + 1) % (len(magnitudes) * pair_size)

        if sequence_index % pair_size == 0 or not self._balanced_heading_pair:
            self._balanced_heading_pair = {
                "magnitude": magnitude,
                "theta": np.random.uniform(0, 2 * np.pi),
                "radius": np.random.uniform(
                    self.phase["spawn_radius_min"],
                    self.phase["spawn_radius_max"],
                ),
            }

        pair = self._balanced_heading_pair
        if pair.get("magnitude") != magnitude:
            pair = {
                "magnitude": magnitude,
                "theta": np.random.uniform(0, 2 * np.pi),
                "radius": np.random.uniform(
                    self.phase["spawn_radius_min"],
                    self.phase["spawn_radius_max"],
                ),
            }
            self._balanced_heading_pair = pair

        heading_offset = float(sign * magnitude)
        return loc_from_theta_radius_heading(pair["theta"], pair["radius"], heading_offset)

    def reset(self):
        if self.phase.get("balanced_heading_offsets", False):
            px, pz, ry, rz, heading_offset, target_miss_distance = self._next_balanced_heading_loc()
        else:
            px, pz, ry, rz, heading_offset, target_miss_distance = calculate_new_loc(
                self.phase["spawn_radius_min"],
                self.phase["spawn_radius_max"],
                self.phase["heading_offset_min"],
                self.phase["heading_offset_max"],
                self.phase.get("heading_offset_abs_min", 0.0),
            )
        py = float(self.phase.get("target_y", 50.0))

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
        self.last_raw_state = raw_state
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)
        self.prev_distance = float(raw_state["states"]["distance"])
        telemetry = raw_state.get("telemetry", {})
        initial_target_distance = float(telemetry.get("target_distance", self.prev_distance))
        self.reset_distance = initial_target_distance
        self.reset_horizontal_distance = self._target_horizontal_distance(telemetry, initial_target_distance)
        self.min_distance_seen = initial_target_distance
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
        beta_validity = float(telemetry.get("beta_validity", 1.0))
        alignment = float(np.cos(theta_rad))
        target_distance = float(telemetry.get("target_distance", distance))
        target_closing_speed = float(telemetry.get("target_closing_speed", closing_speed))
        target_alignment = float(telemetry.get("target_alignment", alignment))
        target_theta_deg = float(telemetry.get("target_theta_deg", theta_deg))
        target_hit_triggered = float(telemetry.get("target_hit_trigger", 0.0)) > 0.5
        target_horizontal_distance = self._target_horizontal_distance(telemetry, target_distance)
        turn_rate_clock = np.asarray(states.get("turn_rate_clock", [0.0, 0.0, 0.0, 0.0]), dtype=np.float32)
        turn_rate_roll = float(states.get("turn_rate_roll", states.get("turn_rate_ref", [0.0, 0.0, 0.0])[2]))
        ang_vel_mag = float(np.sqrt(np.sum(np.square(turn_rate_clock)) + turn_rate_roll ** 2))
        guidance_forward = self._safe_unit(
            self._telemetry_vec(telemetry, "guidance_forward_world"),
            np.array([0.0, 0.0, 1.0]),
        )
        rel_pos_world = self._telemetry_vec(telemetry, "rel_pos_world")
        target_vel_world = self._telemetry_vec(telemetry, "target_vel_world")
        rocket_vel_world = self._telemetry_vec(telemetry, "rocket_vel_world")
        rel_dir_world = self._safe_unit(rel_pos_world, guidance_forward)
        rocket_forward_world = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_forward_world"),
            guidance_forward,
        )
        rocket_toward_target = float(np.dot(rocket_vel_world, rel_dir_world))

        # V16: Unity artik state distance/theta/closing degerlerini lead aim point'e gore yollar.
        # Bu nedenle Python tarafinda ikinci kez ileri tasima yapmiyoruz; lead metrikleri debug icin ayni aim frame'i anlatir.
        lead_time = float(telemetry.get("aim_lead_time", 0.0))
        lead_distance = float(telemetry.get("aim_distance", distance))
        lead_alignment = alignment

        prev_distance = distance if self.prev_distance is None else self.prev_distance
        delta_distance = float(np.clip(
            prev_distance - distance,
            -phase["distance_progress_scale"],
            phase["distance_progress_scale"],
        ))
        distance_progress = delta_distance / max(phase["distance_progress_scale"], 1e-6)
        closing_norm = float(np.clip(
            closing_speed / max(phase["closing_speed_scale"], 1e-6),
            -1.0,
            1.0,
        ))

        step_penalty = float(phase["step_penalty"])
        distance_reward = float(phase["distance_gain"] * distance_progress)
        alignment_base_reward = float(phase["alignment_gain"] * (alignment - phase["alignment_reward_floor"]))
        if (
            alignment_base_reward > 0.0
            and (closing_speed <= 0.0 or delta_distance <= 0.0 or rocket_toward_target <= 0.0)
        ):
            # Hedefin kendiliginden yaklasmasi veya kacirdiktan sonra arkadan bakmak alignment odulu toplatmasin.
            alignment_reward = 0.0
        else:
            alignment_reward = alignment_base_reward

        lead_reward_proximity = float(np.clip(
            1.0 - (distance / max(phase["lead_reward_distance"], 1e-6)),
            0.0,
            1.0,
        ))
        lead_alignment_base_reward = float(
            phase["lead_alignment_gain"]
            * lead_reward_proximity
            * (lead_alignment - phase["lead_alignment_reward_floor"])
        )
        if (
            lead_alignment_base_reward > 0.0
            and (closing_speed <= 0.0 or delta_distance <= 0.0 or rocket_toward_target <= 0.0)
        ):
            lead_alignment_reward = 0.0
        else:
            lead_alignment_reward = lead_alignment_base_reward

        prev_theta = theta_deg if self.prev_theta is None else self.prev_theta
        delta_theta_deg = float(np.clip(
            prev_theta - theta_deg,
            -phase["theta_progress_scale_deg"],
            phase["theta_progress_scale_deg"],
        ))
        theta_progress_scale = phase["theta_progress_scale_deg"]
        theta_progress_reward = float(
            phase["theta_progress_gain"]
            * delta_theta_deg
            / max(theta_progress_scale, 1e-6)
        )
        if theta_progress_reward < 0.0:
            theta_progress_reward *= phase["theta_regress_penalty_scale"]
        closing_reward = float(phase["closing_gain"] * closing_norm)

        reset_horizontal_distance = max(
            float(self.reset_horizontal_distance or self.reset_distance or target_horizontal_distance),
            1e-6,
        )
        altitude_schedule_progress = float(np.clip(
            1.0 - (target_horizontal_distance / reset_horizontal_distance),
            0.0,
            1.0,
        ))
        altitude_schedule_target_agl = float(phase.get(
            "altitude_schedule_target_agl",
            phase.get("target_y", 100.0),
        ))
        altitude_schedule_desired_agl = float(
            altitude_schedule_target_agl
            * (altitude_schedule_progress ** float(phase["altitude_schedule_power"]))
        )
        altitude_schedule_deficit = max(
            altitude_schedule_desired_agl
            - agl
            - float(phase["altitude_schedule_tolerance"]),
            0.0,
        )
        altitude_schedule_reward = 0.0
        if self.step_count > int(phase["altitude_schedule_grace_steps"]):
            altitude_schedule_reward = -float(phase["altitude_schedule_gain"]) * (
                altitude_schedule_deficit / max(altitude_schedule_target_agl, 1e-6)
            )

        final_approach_proximity = float(np.clip(
            1.0 - (distance / max(phase["final_approach_distance"], 1e-6)),
            0.0,
            1.0,
        ))
        lead_blend = float(np.clip(phase["final_approach_lead_blend"], 0.0, 1.0))
        final_approach_aim_alignment = float(
            ((1.0 - lead_blend) * alignment) + (lead_blend * lead_alignment)
        )
        final_approach_alignment = float(np.clip(
            (final_approach_aim_alignment - phase["final_approach_alignment_floor"])
            / max(1.0 - phase["final_approach_alignment_floor"], 1e-6),
            0.0,
            1.0,
        ))
        final_approach_closing = max(closing_norm, 0.0)
        final_approach_progress = max(distance_progress, 0.0)
        final_approach_bad_angle = float(np.clip(
            (phase["final_approach_alignment_floor"] - final_approach_aim_alignment)
            / max(phase["final_approach_alignment_floor"] + 1.0, 1e-6),
            0.0,
            1.0,
        ))
        final_approach_bad_closing = max(-closing_norm, 0.0)
        final_approach_bad_progress = max(-distance_progress, 0.0)
        final_approach_reward = float(
            phase["final_approach_gain"]
            * final_approach_proximity
            * final_approach_alignment
            * final_approach_closing
            * final_approach_progress
            - phase["final_approach_bad_angle_gain"]
            * final_approach_proximity
            * final_approach_bad_angle
            - phase["final_approach_bad_closing_gain"]
            * final_approach_proximity
            * final_approach_bad_closing
            - phase["final_approach_bad_progress_gain"]
            * final_approach_proximity
            * final_approach_bad_progress
        )

        reward = (
            step_penalty
            + distance_reward
            + alignment_reward
            + theta_progress_reward
            + closing_reward
            + lead_alignment_reward
            + final_approach_reward
            + altitude_schedule_reward
        )
        done = False
        done_reason = None
        success = False
        terminal_reward = 0.0
        wrong_way_distance_ratio = target_distance / max(self.reset_distance or target_distance, 1e-6)
        previous_min_distance = target_distance if self.min_distance_seen is None else self.min_distance_seen
        min_distance_seen = min(previous_min_distance, target_distance)

        distance_success_fallback = (
            bool(phase.get("distance_success_fallback", False))
            and target_distance <= phase["hit_success_distance"]
        )
        physical_hit_success = target_hit_triggered or distance_success_fallback
        guided_success = (
            bool(phase.get("guided_success_enabled", False))
            and target_distance <= phase["success_distance"]
            and target_alignment >= phase["success_alignment"]
            and target_closing_speed >= phase["success_min_closing"]
        )
        missed_intercept = (
            min_distance_seen <= phase["missed_intercept_distance"]
            and target_distance - min_distance_seen >= phase["missed_intercept_recede_distance"]
            and target_closing_speed <= phase["missed_intercept_closing_speed"]
        )

        near_miss_candidate = (
            target_distance <= phase["near_miss_distance"]
            and not physical_hit_success
            and target_alignment < phase["success_alignment"]
        )

        if physical_hit_success or guided_success:
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
        elif missed_intercept:
            terminal_reward = phase["missed_intercept_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "missed_intercept"
        elif (
            self.step_count > phase["bad_angle_grace_steps"]
            and theta_deg > phase["max_theta_deg"]
        ):
            terminal_reward = phase["bad_angle_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "bad_angle"
        elif (
            self.step_count >= phase["wrong_way_grace_steps"]
            and alignment <= phase["wrong_way_alignment"]
            and closing_speed <= phase["wrong_way_closing_speed"]
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
        self.min_distance_seen = min_distance_seen
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
            "target_distance": float(target_distance),
            "altitude_schedule_progress": float(altitude_schedule_progress),
            "altitude_schedule_desired_agl": float(altitude_schedule_desired_agl),
            "altitude_schedule_deficit": float(altitude_schedule_deficit),
            "altitude_schedule_horizontal_distance": float(target_horizontal_distance),
            "target_closing_speed": float(target_closing_speed),
            "target_alignment": float(target_alignment),
            "target_theta_deg": float(target_theta_deg),
            "target_hit_trigger": 1.0 if target_hit_triggered else 0.0,
            "lead_time": float(lead_time),
            "lead_distance": float(lead_distance),
            "lead_alignment": float(lead_alignment),
            "final_approach_aim_alignment": float(final_approach_aim_alignment),
            "theta_rad": float(theta_rad),
            "theta_deg": float(theta_deg),
            "alpha_rad": float(alpha_rad),
            "alpha_deg": float(alpha_deg),
            "beta_rad": float(beta_rad),
            "beta_deg": float(beta_deg),
            "beta_validity": float(beta_validity),
            "ang_vel_mag": float(ang_vel_mag),
            "reward_step_penalty": float(step_penalty),
            "reward_distance": float(distance_reward),
            "reward_alignment": float(alignment_reward),
            "reward_theta_progress": float(theta_progress_reward),
            "reward_closing": float(closing_reward),
            "reward_lead_alignment": float(lead_alignment_reward),
            "reward_final_approach": float(final_approach_reward),
            "reward_altitude_schedule": float(altitude_schedule_reward),
            "reward_terminal": float(terminal_reward),
            "near_miss_candidate": 1.0 if near_miss_candidate else 0.0,
            "grounded_flag": 1.0 if grounded else 0.0,
            "done_reason": done_reason,
            "success": success,
        }
        return float(reward), done, reward_info

    # STEP

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
        self.last_raw_state = raw_state
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)

        is_direct_guidance = self._is_accel_action_packet(denorm_action)
        reward_action = (
            np.asarray([MAX_THRUST, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
            if is_direct_guidance
            else denorm_action
        )
        reward, done, reward_info = self.calculate_reward(raw_state, denorm_action=reward_action)

        info = self.build_info(
            raw_state=raw_state,
            denorm_action=reward_action,
            reward=reward,
            done=done,
            done_reason=reward_info["done_reason"]
        )
        info["grounded_flag"] = reward_info["grounded_flag"]
        info["alignment"] = reward_info["alignment"]
        info["ang_vel_mag"] = reward_info["ang_vel_mag"]
        info["closing_speed"] = reward_info["closing_speed"]
        info["delta_distance"] = reward_info["delta_distance"]
        info["target_distance"] = reward_info["target_distance"]
        info["altitude_schedule_progress"] = reward_info["altitude_schedule_progress"]
        info["altitude_schedule_desired_agl"] = reward_info["altitude_schedule_desired_agl"]
        info["altitude_schedule_deficit"] = reward_info["altitude_schedule_deficit"]
        info["altitude_schedule_horizontal_distance"] = reward_info["altitude_schedule_horizontal_distance"]
        info["target_closing_speed"] = reward_info["target_closing_speed"]
        info["target_alignment"] = reward_info["target_alignment"]
        info["target_theta_deg"] = reward_info["target_theta_deg"]
        info["target_hit_trigger"] = reward_info["target_hit_trigger"]
        info["lead_time"] = reward_info["lead_time"]
        info["lead_distance"] = reward_info["lead_distance"]
        info["lead_alignment"] = reward_info["lead_alignment"]
        info["final_approach_aim_alignment"] = reward_info["final_approach_aim_alignment"]
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

        Bu metot RL action normalizasyonunu kullanmaz. Boylece PN gibi algoritmalar,
        Unity'nin bekledigi fiziksel komutlari dogrudan test edebilir.
        Standart paket: [thrust, clock_12, clock_6, clock_3, clock_9].
        Direct paket: [-7777, accel_x, accel_y, accel_z, look_x, look_y, look_z].
        """
        values = np.asarray(denorm_action, dtype=np.float32).reshape(-1)
        if len(values) < 5:
            raise ValueError("Direct action icin 5 deger gerekir: thrust, clock_12, clock_6, clock_3, clock_9")

        is_direct_guidance = self._is_accel_action_packet(values)
        if is_direct_guidance:
            values = values[:7].astype(np.float32)
        else:
            values = values[:5].astype(np.float32)
        self.step_count += 1

        if is_direct_guidance:
            clock_12_net = 0.0
            clock_3_net = 0.0
            turn_strength = float(np.linalg.norm(values[1:4]))
        else:
            clock_12_net = float(values[1] - values[2])
            clock_3_net = float(values[3] - values[4])
            turn_strength = float(np.sqrt(clock_12_net ** 2 + clock_3_net ** 2))

        self.last_action_info = {
            "action_direction_id": -1,
            "turn_direction_id": -1,
            "turn_direction_name": action_label,
            "action_direction_clock12": clock_12_net,
            "action_direction_clock3": clock_3_net,
            "turn_strength": turn_strength,
        }

        action_dict = {
            "episode_id": self.episode_id,
            "step_id": self.step_count,
            "type": "action",
            "values": [float(v) for v in values],
        }

        self.connect.send_packet(action_dict)

        raw_state = self.read_state()
        self.last_raw_state = raw_state
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)

        # Direct paket reward icin sahte clock action gibi yorumlanmasin.
        # Reward terminal/success analizi state'ten gelir; action cezalari bu baseline testinde anlamsizdir.
        reward_action = np.asarray([MAX_THRUST, 0.0, 0.0, 0.0, 0.0], dtype=np.float32) if is_direct_guidance else values
        reward, done, reward_info = self.calculate_reward(raw_state, denorm_action=reward_action)
        info = self.build_info(
            raw_state=raw_state,
            denorm_action=reward_action,
            reward=reward,
            done=done,
            done_reason=reward_info["done_reason"],
        )

        info["grounded_flag"] = reward_info["grounded_flag"]
        info["alignment"] = reward_info["alignment"]
        info["ang_vel_mag"] = reward_info["ang_vel_mag"]
        info["closing_speed"] = reward_info["closing_speed"]
        info["delta_distance"] = reward_info["delta_distance"]
        info["target_distance"] = reward_info["target_distance"]
        info["altitude_schedule_progress"] = reward_info["altitude_schedule_progress"]
        info["altitude_schedule_desired_agl"] = reward_info["altitude_schedule_desired_agl"]
        info["altitude_schedule_deficit"] = reward_info["altitude_schedule_deficit"]
        info["altitude_schedule_horizontal_distance"] = reward_info["altitude_schedule_horizontal_distance"]
        info["target_closing_speed"] = reward_info["target_closing_speed"]
        info["target_alignment"] = reward_info["target_alignment"]
        info["target_theta_deg"] = reward_info["target_theta_deg"]
        info["target_hit_trigger"] = reward_info["target_hit_trigger"]
        info["lead_time"] = reward_info["lead_time"]
        info["lead_distance"] = reward_info["lead_distance"]
        info["lead_alignment"] = reward_info["lead_alignment"]
        info["final_approach_aim_alignment"] = reward_info["final_approach_aim_alignment"]
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
        if CONTROL_MODE == "guidance_accel":
            return self.denormalize_guidance_accel_action(action)
        if CONTROL_MODE == "body_accel":
            return self.denormalize_body_accel_action(action)
        if CONTROL_MODE == "direct_accel":
            return self.denormalize_direct_accel_action(action)

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

    def denormalize_guidance_accel_action(self, action):
        """
        SAC action'ini guidance frame'inde ivme komutuna cevirir.

        Bu mod hedefe otomatik bakis/PN kullanmaz. Ajan sag-sol, yukari-asagi ve
        ileri ivmeyi secer; Unity sadece bu ivmeyi uygular ve gorsel govdeyi hiz
        yonune hizalar. Boylece roll problemi egitimin ana hedefi olmaktan cikar.
        """
        a = np.asarray(action, dtype=np.float32).reshape(-1)
        if len(a) < 3:
            a = np.pad(a, (0, 3 - len(a)), mode="constant")
        a = np.clip(a[:3], -1.0, 1.0)

        raw_state = self.last_raw_state or {}
        states = raw_state.get("states", {})
        telemetry = raw_state.get("telemetry", {})

        right_ref = self._safe_unit(
            self._telemetry_vec(telemetry, "guidance_right_world"),
            np.array([1.0, 0.0, 0.0]),
        )
        up_ref = self._safe_unit(
            self._telemetry_vec(telemetry, "guidance_up_world"),
            np.array([0.0, 1.0, 0.0]),
        )
        forward_ref = self._safe_unit(
            self._telemetry_vec(telemetry, "guidance_forward_world"),
            np.array([0.0, 0.0, 1.0]),
        )

        agl = float(states.get("agl", 0.0))
        launch_progress = max(
            np.clip(agl / max(GUIDANCE_ACCEL_LAUNCH_SAFE_AGL, 1e-6), 0.0, 1.0),
            np.clip(float(self.step_count) / max(GUIDANCE_ACCEL_LAUNCH_SAFE_STEPS, 1), 0.0, 1.0),
        )
        launch_lateral_scale = GUIDANCE_ACCEL_LAUNCH_MIN_LATERAL_SCALE + (
            1.0 - GUIDANCE_ACCEL_LAUNCH_MIN_LATERAL_SCALE
        ) * launch_progress
        launch_forward_scale = GUIDANCE_ACCEL_LAUNCH_MIN_FORWARD_SCALE + (
            1.0 - GUIDANCE_ACCEL_LAUNCH_MIN_FORWARD_SCALE
        ) * launch_progress

        right_accel = float(a[0]) * GUIDANCE_ACCEL_LATERAL_MAX_ACCEL * launch_lateral_scale
        up_accel = float(a[1]) * GUIDANCE_ACCEL_UP_MAX_ACCEL
        up_accel += (1.0 - launch_progress) * GUIDANCE_ACCEL_LAUNCH_UP_BIAS
        min_up_accel = (1.0 - launch_progress) * GUIDANCE_ACCEL_LAUNCH_MIN_UP_ACCEL
        up_accel = max(up_accel, min_up_accel)
        forward_accel = GUIDANCE_ACCEL_FORWARD_MIN_ACCEL + ((float(a[2]) + 1.0) * 0.5) * (
            GUIDANCE_ACCEL_FORWARD_MAX_ACCEL - GUIDANCE_ACCEL_FORWARD_MIN_ACCEL
        )
        forward_accel *= launch_forward_scale

        accel_world = (
            right_ref * right_accel
            + up_ref * up_accel
            + forward_ref * forward_accel
        )
        accel_world = self._clamp_magnitude(accel_world, GUIDANCE_ACCEL_MAX_ACCEL)

        rocket_vel = self._telemetry_vec(telemetry, "rocket_vel_world")
        velocity_look = rocket_vel + (accel_world * 0.25)
        look_dir = self._safe_unit(velocity_look, self._safe_unit(accel_world, forward_ref))

        self.last_action_info = {
            "action_direction_id": -1,
            "turn_direction_id": -1,
            "turn_direction_name": "guidance_accel",
            "action_direction_clock12": float(a[1]),
            "action_direction_clock3": float(a[0]),
            "turn_strength": float(np.linalg.norm(a)),
            "action_norm_0": float(a[0]),
            "action_norm_1": float(a[1]),
            "action_norm_2": float(a[2]),
            "direct_accel_world_x": float(accel_world[0]),
            "direct_accel_world_y": float(accel_world[1]),
            "direct_accel_world_z": float(accel_world[2]),
            "direct_accel_cmd_right": float(right_accel),
            "direct_accel_cmd_up": float(up_accel),
            "direct_accel_cmd_forward": float(forward_accel),
            "direct_launch_guard": float(launch_progress < 1.0),
        }

        return [
            float(GUIDANCE_ACCEL_ACTION_MARKER),
            float(accel_world[0]),
            float(accel_world[1]),
            float(accel_world[2]),
            float(look_dir[0]),
            float(look_dir[1]),
            float(look_dir[2]),
        ]

    def denormalize_direct_accel_action(self, action):
        """RL action'ini burun referansli direct packet'e cevirir.

        Bu modda sifir action hedefe otomatik bakmaz; mevcut roket burnunu korur.
        Ajan, hedefe donmek icin action[0]/action[1] ile sag-yukari sapma ogrenmelidir.
        """
        a = np.asarray(action, dtype=np.float32).reshape(-1)
        if len(a) < 3:
            a = np.pad(a, (0, 3 - len(a)), mode="constant")
        a = np.clip(a[:3], -1.0, 1.0)

        raw_state = self.last_raw_state or {}
        telemetry = raw_state.get("telemetry", {})
        right_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_right_world"), np.array([1.0, 0.0, 0.0]))
        up_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_up_world"), np.array([0.0, 1.0, 0.0]))
        forward_ref = self._safe_unit(self._telemetry_vec(telemetry, "guidance_forward_world"), np.array([0.0, 0.0, 1.0]))
        rocket_forward = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_forward_world"),
            forward_ref,
        )

        # action[0] ve action[1] serbest dunya ivmesi degil, mevcut burun yonune gore
        # sag/yukari direksiyon komutudur. Hedef yonu state icindedir; buraya otomatik
        # eklenmez. Boylece success, wrapper'in hedef kilidinden degil policy kararindan gelir.
        aim_offset = (
            right_ref * float(a[0]) * DIRECT_ACTION_RIGHT_AIM_OFFSET
            + up_ref * float(a[1]) * DIRECT_ACTION_UP_AIM_OFFSET
        )
        look_dir = self._safe_unit(rocket_forward + aim_offset, rocket_forward)

        # action[2] ileri ivme siddetidir. Negatif deger bile geri itki degil, daha dusuk ileri itki anlamina gelir.
        accel_mag = DIRECT_ACTION_MIN_ACCEL + ((float(a[2]) + 1.0) * 0.5) * (
            DIRECT_ACTION_MAX_ACCEL - DIRECT_ACTION_MIN_ACCEL
        )

        states = raw_state.get("states", {})
        agl = float(states.get("agl", 0.0))

        launch_progress = max(
            np.clip(agl / max(DIRECT_LAUNCH_SAFE_AGL, 1e-6), 0.0, 1.0),
            np.clip(float(self.step_count) / max(DIRECT_LAUNCH_SAFE_STEPS, 1), 0.0, 1.0),
        )
        launch_guard = float(launch_progress < 1.0)

        if launch_guard > 0.0:
            # Kalkista rastgele action'in roketi yere bastirmasini engeller.
            # Bu bias hedefe kilit degil, sadece rampadan guvenli ayrilma destegidir.
            up_bias = (1.0 - launch_progress) * DIRECT_LAUNCH_UP_BIAS
            look_dir = self._safe_unit(look_dir + up_ref * up_bias, look_dir)

        accel_world = look_dir * float(accel_mag)
        accel_world = self._clamp_magnitude(accel_world, DIRECT_ACTION_MAX_ACCEL)

        self.last_action_info = {
            "action_direction_id": -1,
            "turn_direction_id": -1,
            "turn_direction_name": "direct_accel",
            "action_direction_clock12": float(a[1]),
            "action_direction_clock3": float(a[0]),
            "turn_strength": float(np.linalg.norm(a)),
            "action_norm_0": float(a[0]),
            "action_norm_1": float(a[1]),
            "action_norm_2": float(a[2]),
            "direct_accel_world_x": float(accel_world[0]),
            "direct_accel_world_y": float(accel_world[1]),
            "direct_accel_world_z": float(accel_world[2]),
            "direct_accel_cmd_right": float(a[0] * DIRECT_ACTION_RIGHT_AIM_OFFSET),
            "direct_accel_cmd_up": float(a[1] * DIRECT_ACTION_UP_AIM_OFFSET),
            "direct_accel_cmd_forward": float(accel_mag),
            "direct_launch_guard": launch_guard,
        }

        return [
            float(DIRECT_ACTION_MARKER),
            float(accel_world[0]),
            float(accel_world[1]),
            float(accel_world[2]),
            float(look_dir[0]),
            float(look_dir[1]),
            float(look_dir[2]),
        ]

    def denormalize_body_accel_action(self, action):
        """SAC action'ini roket govde frame'inde ivmeye cevirir; hedefe otomatik kilitlenmez."""
        a = np.asarray(action, dtype=np.float32).reshape(-1)
        if len(a) < 3:
            a = np.pad(a, (0, 3 - len(a)), mode="constant")
        a = np.clip(a[:3], -1.0, 1.0)

        raw_state = self.last_raw_state or {}
        states = raw_state.get("states", {})
        telemetry = raw_state.get("telemetry", {})

        body_right = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_right_world"),
            np.array([1.0, 0.0, 0.0]),
        )
        body_up = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_up_world"),
            np.array([0.0, 0.0, 1.0]),
        )
        body_forward = self._safe_unit(
            self._telemetry_vec(telemetry, "rocket_point_forward_world"),
            np.array([0.0, 1.0, 0.0]),
        )

        agl = float(states.get("agl", 0.0))
        launch_progress = max(
            np.clip(agl / max(BODY_ACCEL_LAUNCH_SAFE_AGL, 1e-6), 0.0, 1.0),
            np.clip(float(self.step_count) / max(BODY_ACCEL_LAUNCH_SAFE_STEPS, 1), 0.0, 1.0),
        )
        launch_lateral_scale = BODY_ACCEL_LAUNCH_MIN_LATERAL_SCALE + (
            1.0 - BODY_ACCEL_LAUNCH_MIN_LATERAL_SCALE
        ) * launch_progress

        right_accel = float(a[0]) * BODY_ACCEL_LATERAL_MAX_ACCEL * launch_lateral_scale
        up_accel = float(a[1]) * BODY_ACCEL_LATERAL_MAX_ACCEL * launch_lateral_scale
        forward_accel = BODY_ACCEL_FORWARD_MIN_ACCEL + ((float(a[2]) + 1.0) * 0.5) * (
            BODY_ACCEL_FORWARD_MAX_ACCEL - BODY_ACCEL_FORWARD_MIN_ACCEL
        )

        accel_world = (
            body_right * right_accel
            + body_up * up_accel
            + body_forward * forward_accel
        )
        accel_world = self._clamp_magnitude(accel_world, BODY_ACCEL_FORWARD_MAX_ACCEL)

        self.last_action_info = {
            "action_direction_id": -1,
            "turn_direction_id": -1,
            "turn_direction_name": "body_accel",
            "action_direction_clock12": float(a[1]),
            "action_direction_clock3": float(a[0]),
            "turn_strength": float(np.linalg.norm(a)),
            "action_norm_0": float(a[0]),
            "action_norm_1": float(a[1]),
            "action_norm_2": float(a[2]),
            "direct_accel_world_x": float(accel_world[0]),
            "direct_accel_world_y": float(accel_world[1]),
            "direct_accel_world_z": float(accel_world[2]),
            "direct_accel_cmd_right": float(right_accel),
            "direct_accel_cmd_up": float(up_accel),
            "direct_accel_cmd_forward": float(forward_accel),
            "direct_launch_guard": float(launch_progress < 1.0),
        }

        return [
            float(BODY_ACCEL_ACTION_MARKER),
            float(accel_world[0]),
            float(accel_world[1]),
            float(accel_world[2]),
            float(body_forward[0]),
            float(body_forward[1]),
            float(body_forward[2]),
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
