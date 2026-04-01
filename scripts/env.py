import connector
import numpy as np
from datetime import datetime

STATE_KEYS = [
    "los_yaw_sin",
    "los_yaw_cos",
    "los_pitch_sin",
    "los_pitch_cos",
    "distance",
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
    "time_remaining",
]

ACTION_KEYS = ["thrust", "pitch_f", "yaw_f"]

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
TARGET_VELOCITY = 0.0


def calculate_new_loc():
    theta = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(10.5, 20.0)
    px = radius * np.cos(theta)
    pz = radius * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz, px))
    return px, pz, ry, rz


class Env:
    def __init__(self, ip, port):
        self.connect = connector.Connector(ip, port)
        self.done = False
        self.state_size = 18
        self.action_size = 3
        self.max_step = 255
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
        time_remaining = np.clip(
            (self.max_step - self.step_count) / self.max_step,
            0.0,
            1.0,
        )

        return np.array([
            s["los_yaw_sin"],
            s["los_yaw_cos"],
            s["los_pitch_sin"],
            s["los_pitch_cos"],
            s["distance"],
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
            time_remaining,
        ], dtype=np.float32)

    def normalize_state(self, vector_state):
        s = vector_state.copy()
        s[4] = np.tanh(s[4] / DISTANCE_TANH_SCALE)
        s[5] = np.tanh(s[5] / CLOSING_TANH_SCALE)
        s[6:9] = np.tanh(s[6:9] / REL_VEL_TANH_SCALE)
        s[9:12] = np.tanh(s[9:12] / ROC_ANG_VEL_TANH_SCALE)
        s[12:15] = np.clip(s[12:15] / GRAVITY_SCALE, -1.0, 1.0)
        s[15] = np.tanh(s[15] / AGL_TANH_SCALE)
        s[16] = np.tanh(s[16] / ALT_ERROR_TANH_SCALE)
        s[17] = np.clip(s[17], 0.0, 1.0)
        return s.astype(np.float32)

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def reset(self):
        self.episode_id += 1
        px, pz, ry, rz = calculate_new_loc()
        random_rot_degree = np.random.randint(-5, +5)
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
        states = raw_state["states"]

        distance = float(states["distance"])
        agl = float(states["agl"])
        alt_error = float(states["alt_error"])
        grounded = float(states["grounded_flag"]) > 0.5
        closing_speed = float(states["closing_speed"])

        los_yaw_sin = float(states["los_yaw_sin"])
        los_yaw_cos = float(states["los_yaw_cos"])
        los_pitch_sin = float(states["los_pitch_sin"])
        los_pitch_cos = float(states["los_pitch_cos"])

        los_yaw_rad = float(np.arctan2(los_yaw_sin, los_yaw_cos))
        los_pitch_rad = float(np.arctan2(los_pitch_sin, los_pitch_cos))
        los_yaw_deg = float(np.degrees(los_yaw_rad))
        los_pitch_deg = float(np.degrees(los_pitch_rad))
        alignment = float(los_yaw_cos * los_pitch_cos)

        av = states["roc_ang_vel"]
        ang_vel_mag = float(np.sqrt(av[0] ** 2 + av[1] ** 2 + av[2] ** 2))

        STEP_PENALTY = -0.03
        DISTANCE_GAIN = 0.17
        DISTANCE_DELTA_CLIP = 10.0
        ALIGNMENT_GAIN = 0.4
        CLOSING_GAIN = 0.08
        CLOSING_SPEED_CLIP = 30.0
        ANG_VEL_PENALTY = 0.005
        ANG_VEL_CLIP = 10.0
        SUCCESS_DISTANCE = 12.0
        MIN_AGL = 0.35
        LOW_AGL_GRACE_STEPS = 15
        MAX_ALTITUDE = 100.0
        SUCCESS_REWARD = 250.0
        COLLISION_PENALTY = -100.0
        LOW_ALTITUDE_PENALTY = -75.0
        HIGH_ALTITUDE_PENALTY = -90.0
        TIMEOUT_PENALTY = -90.0
        HEIGHT_ALIGN_GAIN = 0.025
        SOFT_FLOOR = 5.0
        SOFT_FLOOR_GAIN = 0.040

        reward = STEP_PENALTY
        done = False
        done_reason = None
        success = False

        delta_distance = self.prev_distance - distance
        delta_distance = np.clip(delta_distance, -DISTANCE_DELTA_CLIP, DISTANCE_DELTA_CLIP)
        reward += DISTANCE_GAIN * delta_distance

        reward += ALIGNMENT_GAIN * alignment

        closing_term = np.clip(closing_speed, -CLOSING_SPEED_CLIP, CLOSING_SPEED_CLIP) / CLOSING_SPEED_CLIP
        reward += CLOSING_GAIN * closing_term

        reward -= ANG_VEL_PENALTY * min(ang_vel_mag, ANG_VEL_CLIP)

        reward += HEIGHT_ALIGN_GAIN * np.clip(1.0 - np.abs(alt_error) / 50.0, 0.0, 1.0)

        if agl < SOFT_FLOOR:
            reward -= SOFT_FLOOR_GAIN * (SOFT_FLOOR - agl)

        if distance <= SUCCESS_DISTANCE:
            reward += SUCCESS_REWARD
            done = True
            done_reason = "success"
            success = True
        elif grounded and self.step_count > 8:
            reward += COLLISION_PENALTY
            done = True
            done_reason = "collision"
        elif agl <= MIN_AGL and self.step_count > LOW_AGL_GRACE_STEPS:
            reward += LOW_ALTITUDE_PENALTY
            done = True
            done_reason = "low_agl"
        elif agl >= MAX_ALTITUDE:
            reward += HIGH_ALTITUDE_PENALTY
            done = True
            done_reason = "high_altitude"
        elif self.step_count >= self.max_step:
            reward += TIMEOUT_PENALTY
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
            "los_yaw_rad": float(los_yaw_rad),
            "los_yaw_deg": float(los_yaw_deg),
            "los_pitch_rad": float(los_pitch_rad),
            "los_pitch_deg": float(los_pitch_deg),
            "ang_vel_mag": float(ang_vel_mag),
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
        info["los_yaw_rad"] = reward_info["los_yaw_rad"]
        info["los_yaw_deg"] = reward_info["los_yaw_deg"]
        info["los_pitch_rad"] = reward_info["los_pitch_rad"]
        info["los_pitch_deg"] = reward_info["los_pitch_deg"]

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

        los_yaw_rad = float(np.arctan2(s["los_yaw_sin"], s["los_yaw_cos"]))
        los_pitch_rad = float(np.arctan2(s["los_pitch_sin"], s["los_pitch_cos"]))

        info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "episode_id": raw_state["episode_id"],
            "step_id": raw_state["step_id"],
            "reward": reward,
            "done": done,
            "done_reason": done_reason,
            "distance": float(s["distance"]),
            "closing_speed": float(s["closing_speed"]),
            "los_yaw_sin": float(s["los_yaw_sin"]),
            "los_yaw_cos": float(s["los_yaw_cos"]),
            "los_pitch_sin": float(s["los_pitch_sin"]),
            "los_pitch_cos": float(s["los_pitch_cos"]),
            "los_yaw_rad": los_yaw_rad,
            "los_yaw_deg": float(np.degrees(los_yaw_rad)),
            "los_pitch_rad": los_pitch_rad,
            "los_pitch_deg": float(np.degrees(los_pitch_rad)),
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
            "time_remaining": float(np.clip((self.max_step - self.step_count) / self.max_step, 0.0, 1.0)),
        }

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
