import os
from datetime import datetime

import connector
import numpy as np

STATE_KEYS = [
    "distance",
    "look_angle_rad",
    "closing_speed",
    "rel_vel_x",
    "rel_vel_y",
    "rel_vel_z",
    "roc_ang_vel_x",
    "roc_ang_vel_y",
    "roc_ang_vel_z",
    "g_x",
    "g_y",
    "g_z",
    "agl",
    "alt_error",
]

ACTION_KEYS = ["thrust", "pitch_f", "yaw_f"]

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
    "reward_angular_penalty",
    "reward_altitude",
    "reward_soft_floor_penalty",
    "reward_terminal",
]

TELEMETRY_VECTOR_SPECS = [
    ("rocket_pos_world", ("x", "y", "z")),
    ("rocket_euler_world", ("x", "y", "z")),
    ("rocket_rot_world", ("x", "y", "z", "w")),
    ("rocket_point_pos_world", ("x", "y", "z")),
    ("rocket_point_forward_world", ("x", "y", "z")),
    ("rocket_point_up_world", ("x", "y", "z")),
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
]

TELEMETRY_SCALAR_KEYS = [
    "target_speed",
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

MIN_THRUST = 600.0
MAX_THRUST = 1050.0
MAX_PITCH_FORCE = 1.7
MAX_YAW_FORCE = 1.7
TARGET_VELOCITY = 25.0

REWARD_CONFIG = {
    "step_penalty": -0.08,
    "distance_gain": 0.12,
    "distance_delta_clip": 6.0,
    "alignment_gain": 0.16,
    "closing_gain": 0.10,
    "closing_speed_clip": 30.0,
    "ang_vel_penalty": 0.02,
    "ang_vel_clip": 10.0,
    "height_align_gain": 0.012,
    "soft_floor": 8.0,
    "soft_floor_gain": 0.12,
    "min_agl": 0.40,
    "low_agl_grace_steps": 15,
    "collision_grace_steps": 8,
    "max_altitude": 100.0,
    "success_reward": 180.0,
    "collision_penalty": -130.0,
    "low_altitude_penalty": -110.0,
    "high_altitude_penalty": -85.0,
}

CURRICULUM_PHASES = {
    1: {
        "name": "phase_1_2_guided_close_range_refine",
        "spawn_radius_min": 50.0,
        "spawn_radius_max": 75.0,
        "heading_offset_min": -5,
        "heading_offset_max": 5,
        "max_step": 500,
        "step_penalty": -0.12,
        "distance_gain": 0.26,
        "alignment_gain": 0.52,
        "closing_gain": 0.18,
        "ang_vel_penalty": 0.03,
        "height_align_gain": 0.018,
        "soft_floor_gain": 0.12,
        "low_altitude_penalty": -110.0,
        "high_altitude_penalty": -95.0,
        "success_distance": 14.0,
        "success_alignment": 0.80,
        "success_min_closing": 0.0,
        "timeout_penalty": -80.0,
    },
    2: {
        "name": "phase_2_longer_horizon",
        "spawn_radius_min": 75.0,
        "spawn_radius_max": 120.0,
        "heading_offset_min": -10,
        "heading_offset_max": 10,
        "max_step": 700,
        "success_distance": 12.0,
        "success_alignment": 0.88,
        "success_min_closing": 1.0,
        "timeout_penalty": -55.0,
    },
    3: {
        "name": "phase_3_strict_intercept",
        "spawn_radius_min": 120.0,
        "spawn_radius_max": 200.0,
        "heading_offset_min": -15,
        "heading_offset_max": 15,
        "max_step": 900,
        "success_distance": 10.0,
        "success_alignment": 0.92,
        "success_min_closing": 2.0,
        "timeout_penalty": -70.0,
    },
}


def get_active_phase_id():
    raw_value = os.getenv("ADS_AI_PHASE", "1").strip()

    try:
        phase_id = int(raw_value)
    except ValueError:
        phase_id = 1

    if phase_id not in CURRICULUM_PHASES:
        phase_id = 1

    return phase_id


def get_phase_config(phase_id):
    config = dict(REWARD_CONFIG)
    config.update(CURRICULUM_PHASES[phase_id])
    return config


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
        self.state_size = 14
        self.action_size = 3
        self.phase_id = get_active_phase_id()
        self.phase = get_phase_config(self.phase_id)
        self.max_step = int(self.phase["max_step"])
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None
        self.reset_distance = None

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def read_state(self):
        return self.connect.read_packet()

    def parse_state(self, raw_state):
        s = raw_state["states"]

        return np.array([
            s["distance"],
            s["look_angle_rad"],
            s["closing_speed"],
            s["rel_vel"][0],
            s["rel_vel"][1],
            s["rel_vel"][2],
            s["roc_ang_vel"][0],
            s["roc_ang_vel"][1],
            s["roc_ang_vel"][2],
            s["g"][0],
            s["g"][1],
            s["g"][2],
            s["agl"],
            s["alt_error"],
        ], dtype=np.float32)

    def normalize_state(self, vector_state):
        s = vector_state.copy()
        s[0] = np.tanh(s[0] / DISTANCE_TANH_SCALE)
        s[1] = np.clip(s[1] / np.pi, 0.0, 1.0)
        s[2] = np.tanh(s[2] / CLOSING_TANH_SCALE)
        s[3:6] = np.tanh(s[3:6] / REL_VEL_TANH_SCALE)
        s[6:9] = np.tanh(s[6:9] / ROC_ANG_VEL_TANH_SCALE)
        s[9:12] = np.clip(s[9:12] / GRAVITY_SCALE, -1.0, 1.0)
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

    def calculate_reward(self, raw_state):
        phase = self.phase
        states = raw_state["states"]

        distance = float(states["distance"])
        agl = float(states["agl"])
        alt_error = float(states["alt_error"])
        grounded = float(states["grounded_flag"]) > 0.5
        closing_speed = float(states["closing_speed"])
        look_angle_rad = float(states["look_angle_rad"])
        look_angle_deg = float(np.degrees(look_angle_rad))
        alignment = float(np.cos(look_angle_rad))
        alignment_positive = max(alignment, 0.0)
        positive_closing = np.clip(closing_speed / phase["closing_speed_clip"], 0.0, 1.0)

        av = states["roc_ang_vel"]
        ang_vel_mag = float(np.sqrt(av[0] ** 2 + av[1] ** 2 + av[2] ** 2))

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

        progress_factor = 0.20 + 0.80 * alignment_positive
        distance_reward = phase["distance_gain"] * delta_distance * progress_factor
        alignment_reward = phase["alignment_gain"] * alignment * (0.30 + 0.70 * positive_closing)
        closing_reward = phase["closing_gain"] * positive_closing * (0.20 + 0.80 * alignment_positive)
        angular_penalty = phase["ang_vel_penalty"] * min(ang_vel_mag, phase["ang_vel_clip"])
        altitude_reward = phase["height_align_gain"] * np.clip(1.0 - np.abs(alt_error) / 50.0, 0.0, 1.0)
        soft_floor_penalty = 0.0

        if agl < phase["soft_floor"]:
            soft_floor_penalty = phase["soft_floor_gain"] * (phase["soft_floor"] - agl)

        reward += distance_reward
        reward += alignment_reward
        reward += closing_reward
        reward -= angular_penalty
        reward += altitude_reward
        reward -= soft_floor_penalty

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
        elif self.step_count >= self.max_step:
            terminal_reward = phase["timeout_penalty"]
            reward += terminal_reward
            done = True
            done_reason = "timeout"

        self.prev_distance = distance

        reward_info = {
            "reward_total": float(reward),
            "distance": float(distance),
            "delta_distance": float(delta_distance),
            "agl": float(agl),
            "alt_error": float(alt_error),
            "closing_speed": float(closing_speed),
            "alignment": float(alignment),
            "look_angle_rad": float(look_angle_rad),
            "look_angle_deg": float(look_angle_deg),
            "ang_vel_mag": float(ang_vel_mag),
            "reward_step_penalty": float(phase["step_penalty"]),
            "reward_distance": float(distance_reward),
            "reward_alignment": float(alignment_reward),
            "reward_closing": float(closing_reward),
            "reward_angular_penalty": float(angular_penalty),
            "reward_altitude": float(altitude_reward),
            "reward_soft_floor_penalty": float(soft_floor_penalty),
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

        reward, done, reward_info = self.calculate_reward(raw_state)

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
        info["look_angle_rad"] = reward_info["look_angle_rad"]
        info["look_angle_deg"] = reward_info["look_angle_deg"]
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
        pitch_f = a[1] * MAX_PITCH_FORCE
        yaw_f = a[2] * MAX_YAW_FORCE

        return [float(thrust), float(pitch_f), float(yaw_f)]

    def build_info(self, raw_state, denorm_action=None, reward=None, done=None, done_reason=None):
        s = raw_state["states"]
        telemetry = raw_state.get("telemetry", {})

        look_angle_rad = float(s["look_angle_rad"])
        alignment = float(np.cos(look_angle_rad))

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
            "look_angle_rad": look_angle_rad,
            "look_angle_deg": float(np.degrees(look_angle_rad)),
            "alignment": alignment,
            "rel_vel_x": float(s["rel_vel"][0]),
            "rel_vel_y": float(s["rel_vel"][1]),
            "rel_vel_z": float(s["rel_vel"][2]),
            "roc_ang_vel_x": float(s["roc_ang_vel"][0]),
            "roc_ang_vel_y": float(s["roc_ang_vel"][1]),
            "roc_ang_vel_z": float(s["roc_ang_vel"][2]),
            "g_x": float(s["g"][0]),
            "g_y": float(s["g"][1]),
            "g_z": float(s["g"][2]),
            "agl": float(s["agl"]),
            "alt_error": float(s["alt_error"]),
            "grounded_flag": float(s["grounded_flag"]),
        }

        info.update(flatten_telemetry(telemetry))

        if denorm_action is not None:
            info["thrust"] = denorm_action[0]
            info["pitch_f"] = denorm_action[1]
            info["yaw_f"] = denorm_action[2]
        else:
            info["thrust"] = None
            info["pitch_f"] = None
            info["yaw_f"] = None

        return info

    def close(self):
        self.connect.close()
