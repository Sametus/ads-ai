import connector
import numpy as np
from datetime import datetime
"""
STATES:
    {
        target_dir_x     |
        target_dir_y     | => Rocketten targete giden unit vektör (DistanceLine)
        target_dir_z    _|
        rel_vel_x   |
        rel_vel_y   | => Targetin rockete göre hızı
        rel_vel_z  _|
        roc_vel_x   |
        roc_vel_y   | => Rocketin kendi hızı
        roc_vel_z  _| 
        roc_ang_vel_x   |
        roc_ang_vel_y   | => Rocketin açısal hızı
        roc_ang_vel_z  _|
        roc_h   | => Rocket irtifası
        target_h | => Target irtifası
        gx  |
        gy  | => Gravity Vector
        gz _|   
        distance | => Rocket ile Target arası uzaklık
        closing_rate    | => Hedefe yaklaşma hızı (DeltaDistance)
        blend_w | => Guidance - RL Oranı
    }

    STATE ORDER:
    0  target_dir_x
    1  target_dir_y
    2  target_dir_z
    3  rel_vel_x
    4  rel_vel_y
    5  rel_vel_z
    6  roc_vel_x
    7  roc_vel_y
    8  roc_vel_z
    9  roc_ang_vel_x
    10 roc_ang_vel_y
    11 roc_ang_vel_z
    12 roc_h
    13 target_h
    14 gx
    15 gy
    16 gz
    17 distance
    18 closing_rate
    19 blend_w

    JSON - DICT'teki State Yapısı:
    {
        target_dir : [x,y,z],
        rel_vel : [x,y,z],
        roc_vel: [x,y,z],
        roc_ang_vel: [x,y,z],
        roc_h : rh,
        target_h : th,
        g : [x,y,z],
        distance : d,
        closing_rate: cr,
        blend_w: bw
    }
"""

STATE_KEYS = [
    "target_dir_x",
    "target_dir_y",
    "target_dir_z",
    "rel_vel_x",
    "rel_vel_y",
    "rel_vel_z",
    "roc_vel_x",
    "roc_vel_y",
    "roc_vel_z",
    "roc_ang_vel_x",
    "roc_ang_vel_y",
    "roc_ang_vel_z",
    "roc_h",
    "target_h",
    "gx",
    "gy",
    "gz",
    "distance",
    "closing_rate",
    "blend_w"
]

ACTION_KEYS = [
    "thrust",
    "pitch_f",
    "yaw_f"
]

"""
UNITY -> PYTHON : JSON-DICT YAPISI
{
    "episode_id": episode_id,
    "step_id": step_id,
    "states": {
        "target_dir":   [x, y, z],
        "rel_vel":      [x, y, z],
        "roc_vel":      [x, y, z],
        "roc_ang_vel":  [x, y, z],
        "roc_h":        rh,
        "target_h":     th,
        "g":            [x, y, z],
        "distance":     d,
        "closing_rate": cr,
        "blend_w":      bw
    }
}
"""

"""
PYTHON -> UNİTY JSON-DİCT YAPISI
    RESET İSE:
    {
        episode_id :,
        step_id: 0,
        type: reset,
        values: [px,py,pz,ry,rz]
    }
    ACTİON İSE:
    {   
        episode_id:,
        step_id,
        type: action,
        values: [thrust,pitch_f,yaw_f]
    }
    reset
    values[0] → px
    values[1] → py
    values[2] → pz
    values[3] → ry
    values[4] → rz

    actions
    values[0] → thrust
    values[1] → pitch_f
    values[2] → yaw_f
"""


TARGET_DIR_SCALE = 1.0
REL_VEL_SCALE = 100.0
ROC_VEL_SCALE = 100.0
ROC_ANG_VEL_SCALE = 10.0
HEIGHT_SCALE = 100.0
GRAVITY_SCALE = 9.81
DISTANCE_SCALE = 500.0
CLOSING_RATE_SCALE = 100.0

MIN_THRUST = 700.0
MAX_THRUST = 1200.0

MAX_PITCH_FORCE = 1.5
MAX_YAW_FORCE = 1.5
TARGET_VELOCITY = 25 # M/S

def calculate_new_loc():
    theta = np.random.uniform(0, 2*np.pi)
    px = 300 * np.cos(theta)
    pz = 300 * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz,px))
    return px,pz,ry,rz

class Env:
    
    def __init__(self,ip,port):
        self.connect = connector.Connector(ip,port)
        self.done = False
        self.state_size = 20
        self.action_size = 3
        self.max_step = 1300
        self.step_count = 0
        self.episode_id = 0
        self.prev_distance = None

    def read_state(self):
        state_dict = self.connect.read_packet()
        return state_dict
        

    def parse_state(self, raw_state):
        s = raw_state["states"]

        vector_state = np.array([
            s["target_dir"][0],
            s["target_dir"][1],
            s["target_dir"][2],

            s["rel_vel"][0],
            s["rel_vel"][1],
            s["rel_vel"][2],

            s["roc_vel"][0],
            s["roc_vel"][1],
            s["roc_vel"][2],

            s["roc_ang_vel"][0],
            s["roc_ang_vel"][1],
            s["roc_ang_vel"][2],

            s["roc_h"],
            s["target_h"],

            s["g"][0],
            s["g"][1],
            s["g"][2],

            s["distance"],
            s["closing_rate"],
            s["blend_w"]

        ], dtype=np.float32)

        return vector_state


    def normalize_state(self, vector_state):
        s = vector_state.copy()

        # target_dir
        s[0:3] = np.clip(s[0:3] / TARGET_DIR_SCALE, -1.0, 1.0)

        # rel_vel
        s[3:6] = np.clip(s[3:6] / REL_VEL_SCALE, -1.0, 1.0)

        # roc_vel
        s[6:9] = np.clip(s[6:9] / ROC_VEL_SCALE, -1.0, 1.0)

        # roc_ang_vel
        s[9:12] = np.clip(s[9:12] / ROC_ANG_VEL_SCALE, -1.0, 1.0)

        # roc_h 
        s[12] = np.clip(s[12] / HEIGHT_SCALE, -1.0, 1.0)

        # target_h
        s[13] = np.clip(s[13] / HEIGHT_SCALE, -1.0, 1.0)

        # gravity_vector g
        s[14:17] = np.clip(s[14:17] / GRAVITY_SCALE, -1.0, 1.0)
        
        # distance
        s[17] = np.clip(s[17] / DISTANCE_SCALE, -1.0, 1.0)

        # closing_rate
        s[18] = np.clip(s[18] / CLOSING_RATE_SCALE, -1.0, 1.0)

        # blend_w
        s[19] = np.clip(s[19], 0.0, 1.0)

        return s.astype(np.float32)
    
    
    def reset(self):
        self.episode_id += 1
        px, pz, ry, rz = calculate_new_loc()
        random_rot_degree = np.random.randint(-45,+45)
        rz += random_rot_degree
        py = 50.0 # target_h CL için değiştirilebilir.s
        # log dosya
        random_initial_locations = [px,py,pz,ry,rz]

        self.done = False 
        self.step_count = 0

        init_loc = {
            "episode_id":self.episode_id,
            "step_id":0,
            "type":"reset",
            "values":random_initial_locations
        }
        self.connect.send_packet(data=init_loc)

        raw_state = self.read_state()
        vector_state = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)
        self.prev_distance = float(raw_state["states"]["distance"])
        start_info = self.build_info(raw_state)

        start_info["reset_px"] = px
        start_info["reset_py"] = py
        start_info["reset_pz"] = pz
        start_info["reset_ry"] = ry
        start_info["reset_rz"] = rz
        start_info["reset_heading_offset"] = random_rot_degree

        return raw_state, vector_state, normalized_state, start_info


    def calculate_reward(self, raw_state):

        states = raw_state["states"]

        distance = float(states["distance"])
        roc_h = float(states["roc_h"])

        STEP_PENALTY = -0.02

        DISTANCE_GAIN = 0.5
        DISTANCE_DELTA_CLIP = 10.0

        SUCCESS_DISTANCE = 12.0

        MIN_ALTITUDE = 0.8
        MAX_ALTITUDE = 250.0
        
        SUCCESS_REWARD = 200.0
        LOW_ALTITUDE_PENALTY = -100.0
        HIGH_ALTITUDE_PENALTY = -80.0
        TIMEOUT_PENALTY = -60.0

        reward = 0.0
        done = False
        done_reason = None
        success = False

        reward += STEP_PENALTY

        delta_distance = self.prev_distance - distance

        if delta_distance > DISTANCE_DELTA_CLIP:
            delta_distance = DISTANCE_DELTA_CLIP
        elif delta_distance < -DISTANCE_DELTA_CLIP:
            delta_distance = -DISTANCE_DELTA_CLIP
        
        reward += DISTANCE_GAIN * delta_distance

        if distance <= SUCCESS_DISTANCE:
            reward += SUCCESS_REWARD
            done = True
            done_reason = "success"
            success = True
        

        elif roc_h <= MIN_ALTITUDE:
            reward += LOW_ALTITUDE_PENALTY
            done = True
            done_reason = "low_altitude"
        
        elif roc_h >= MAX_ALTITUDE:
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
            "distance":float(distance),
            "delta_distance":float(delta_distance),
            "roc_h":float(roc_h),
            "done_reason":done_reason,
            "success":success
        }

        return float(reward), done, reward_info
    
    
    def step(self, action):
        self.step_count += 1
        ### 1- action oku ve denormalize et
        denorm_action = self.denormalize_action(action)
        
        ### 2- action gönder
        action_dict = {
            "episode_id":self.episode_id,
            "step_id":self.step_count,
            "type":"action",
            "values":denorm_action
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

        self.done = done

        return normalized_state, reward, done, info

    def denormalize_action(self, action):
        a = np.asarray(action, dtype=np.float32)

        # güvenlik
        a = np.clip(a, -1.0, 1.0)

        # thrust
        thrust = MIN_THRUST + ((a[0] + 1.0) / 2.0) * (MAX_THRUST - MIN_THRUST)

        # pitch
        pitch_f = a[1] * MAX_PITCH_FORCE

        # yaw 
        yaw_f = a[2] * MAX_YAW_FORCE

        denorm_action = [
            float(thrust),
            float(pitch_f),
            float(yaw_f)
        ]

        return denorm_action


    def build_info(self, raw_state, denorm_action=None, reward=None, done=None, done_reason=None):

        s = raw_state["states"]

        info = {
            "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "episode_id":raw_state["episode_id"],
            "step_id":raw_state["step_id"],

            "reward": reward,
            "done": done,
            "done_reason": done_reason,

            "target_dir_x" : s["target_dir"][0],
            "target_dir_y" : s["target_dir"][1],
            "target_dir_z" : s["target_dir"][2],

            "rel_vel_x" : s["rel_vel"][0],
            "rel_vel_y" : s["rel_vel"][1],
            "rel_vel_z" : s["rel_vel"][2],

            "roc_vel_x": s["roc_vel"][0],
            "roc_vel_y": s["roc_vel"][1],
            "roc_vel_z": s["roc_vel"][2],

            "roc_ang_vel_x" : s["roc_ang_vel"][0],
            "roc_ang_vel_y" : s["roc_ang_vel"][1],
            "roc_ang_vel_z" : s["roc_ang_vel"][2],

            "roc_h" : s["roc_h"],
            "target_h" : s["target_h"],

            "gx": s["g"][0],
            "gy": s["g"][1],
            "gz": s["g"][2],

            "distance" : s["distance"],
            "closing_rate" : s["closing_rate"],
            "blend_w" : s["blend_w"],

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