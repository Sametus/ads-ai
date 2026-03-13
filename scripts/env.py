import connector
import numpy as np
from datetime import datetime

STATE_KEYS = [
    "target_dir_x", "target_dir_y", "target_dir_z",
    "rel_vel_x", "rel_vel_y", "rel_vel_z",
    "roc_vel_x", "roc_vel_y", "roc_vel_z",
    "roc_ang_vel_x", "roc_ang_vel_y", "roc_ang_vel_z",
    "roc_h", "target_h", "gx", "gy", "gz",
    "distance", "closing_rate", "blend_w"
]

ACTION_KEYS = ["thrust", "pitch_f", "yaw_f"]

TARGET_DIR_SCALE = 1.0
REL_VEL_SCALE = 100.0
ROC_VEL_SCALE = 100.0
ROC_ANG_VEL_SCALE = 10.0
HEIGHT_SCALE = 100.0
GRAVITY_SCALE = 9.81
DISTANCE_SCALE = 500.0
CLOSING_RATE_SCALE = 120.0

MIN_THRUST = 600.0
MAX_THRUST = 1000.0
MAX_PITCH_FORCE = 1.5
MAX_YAW_FORCE = 1.5
TARGET_VELOCITY = 25.0


def calculate_new_loc():
    theta = np.random.uniform(0, 2 * np.pi)
    px = 300 * np.cos(theta)
    pz = 300 * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz, px))
    return px, pz, ry, rz


class Env:
    def __init__(self, ip, port):
        self.connect = connector.Connector(ip, port)
        self.done = False
        self.state_size = 20
        self.action_size = 3
        self.max_step = 1300
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None

    def read_state(self):
        return self.connect.read_packet()

    def parse_state(self, raw_state):
        s = raw_state["states"]
        return np.array([
            s["target_dir"][0], s["target_dir"][1], s["target_dir"][2],
            s["rel_vel"][0], s["rel_vel"][1], s["rel_vel"][2],
            s["roc_vel"][0], s["roc_vel"][1], s["roc_vel"][2],
            s["roc_ang_vel"][0], s["roc_ang_vel"][1], s["roc_ang_vel"][2],
            s["roc_h"], s["target_h"],
            s["g"][0], s["g"][1], s["g"][2],
            s["distance"], s["closing_rate"], s["blend_w"],
        ], dtype=np.float32)

    def normalize_state(self, vector_state):
        s = vector_state.copy()
        s[0:3] = np.clip(s[0:3] / TARGET_DIR_SCALE, -1.0, 1.0)
        s[3:6] = np.clip(s[3:6] / REL_VEL_SCALE, -1.0, 1.0)
        s[6:9] = np.clip(s[6:9] / ROC_VEL_SCALE, -1.0, 1.0)
        s[9:12] = np.clip(s[9:12] / ROC_ANG_VEL_SCALE, -1.0, 1.0)
        s[12] = np.clip(s[12] / HEIGHT_SCALE, -1.0, 1.0)    # roc_h artık AGL
        s[13] = np.clip(s[13] / HEIGHT_SCALE, -1.0, 1.0)
        s[14:17] = np.clip(s[14:17] / GRAVITY_SCALE, -1.0, 1.0)
        s[17] = np.clip(s[17] / DISTANCE_SCALE, -1.0, 1.0)
        s[18] = np.clip(s[18] / CLOSING_RATE_SCALE, -1.0, 1.0)
        s[19] = np.clip(s[19], 0.0, 1.0)                     # grounded flag
        return s.astype(np.float32)

    def reset(self):
        self.episode_id += 1
        px, pz, ry, rz = calculate_new_loc()
        random_rot_degree = np.random.randint(-45, +45)
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

    def calculate_reward(self, raw_state):
        states = raw_state["states"]
        distance = float(states["distance"])
        agl = float(states["roc_h"])
        grounded = float(states["blend_w"]) > 0.5
        closing_rate = float(states["closing_rate"])

        STEP_PENALTY = -0.02
        DISTANCE_GAIN = 0.35
        DISTANCE_DELTA_CLIP = 10.0
        CLOSING_RATE_GAIN = 0.004
        CLOSING_RATE_CLIP = 80.0

        SUCCESS_DISTANCE = 12.0
        MIN_AGL = 0.20
        MAX_ALTITUDE = 150.0

        SUCCESS_REWARD = 200.0
        COLLISION_PENALTY = -100.0
        LOW_ALTITUDE_PENALTY = -70.0
        HIGH_ALTITUDE_PENALTY = -80.0
        TIMEOUT_PENALTY = -60.0

        reward = STEP_PENALTY
        done = False
        done_reason = None
        success = False

        delta_distance = self.prev_distance - distance
        delta_distance = np.clip(delta_distance, -DISTANCE_DELTA_CLIP, DISTANCE_DELTA_CLIP)
        reward += DISTANCE_GAIN * delta_distance

        reward += CLOSING_RATE_GAIN * np.clip(closing_rate, -CLOSING_RATE_CLIP, CLOSING_RATE_CLIP)

        if distance <= SUCCESS_DISTANCE:
            reward += SUCCESS_REWARD
            done = True
            done_reason = "success"
            success = True
        elif grounded and self.step_count > 8:
            reward += COLLISION_PENALTY
            done = True
            done_reason = "collision"
        elif agl <= MIN_AGL and self.step_count > 8:
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
            "roc_h": float(agl),
            "closing_rate": float(closing_rate),
            "grounded": grounded,
            "done_reason": done_reason,
            "success": success
        }
        return float(reward), done, reward_info

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
        info["grounded"] = reward_info["grounded"]

        self.done = done
        return normalized_state, reward, done, info

    def denormalize_action(self, action):
        a = np.asarray(action, dtype=np.float32)
        a = np.clip(a, -1.0, 1.0)

        thrust = MIN_THRUST + ((a[0] + 1.0) / 2.0) * (MAX_THRUST - MIN_THRUST)
        pitch_f = a[1] * MAX_PITCH_FORCE
        yaw_f = a[2] * MAX_YAW_FORCE

        return [float(thrust), float(pitch_f), float(yaw_f)]

    def build_info(self, raw_state, denorm_action=None, reward=None, done=None, done_reason=None):
        s = raw_state["states"]
        info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "episode_id": raw_state["episode_id"],
            "step_id": raw_state["step_id"],
            "reward": reward,
            "done": done,
            "done_reason": done_reason,
            "target_dir_x": s["target_dir"][0],
            "target_dir_y": s["target_dir"][1],
            "target_dir_z": s["target_dir"][2],
            "rel_vel_x": s["rel_vel"][0],
            "rel_vel_y": s["rel_vel"][1],
            "rel_vel_z": s["rel_vel"][2],
            "roc_vel_x": s["roc_vel"][0],
            "roc_vel_y": s["roc_vel"][1],
            "roc_vel_z": s["roc_vel"][2],
            "roc_ang_vel_x": s["roc_ang_vel"][0],
            "roc_ang_vel_y": s["roc_ang_vel"][1],
            "roc_ang_vel_z": s["roc_ang_vel"][2],
            "roc_h": s["roc_h"],
            "target_h": s["target_h"],
            "gx": s["g"][0],
            "gy": s["g"][1],
            "gz": s["g"][2],
            "distance": s["distance"],
            "closing_rate": s["closing_rate"],
            "blend_w": s["blend_w"],
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
