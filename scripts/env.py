import connector
import numpy as np
from datetime import datetime

STATE_KEYS = [
    "target_dir_x", "target_dir_y", "target_dir_z",
    "rel_vel_x", "rel_vel_y", "rel_vel_z",
    "roc_vel_x", "roc_vel_y", "roc_vel_z",
    "roc_ang_vel_x", "roc_ang_vel_y", "roc_ang_vel_z",
    "roc_h", "height_error", "gx", "gy", "gz",
    "distance", "closing_rate",
    "time_remaining",   # [DEĞİŞİKLİK 1] blend_w yerine time_remaining (0→1)
]

ACTION_KEYS = ["thrust", "pitch_f", "yaw_f"]

TARGET_DIR_SCALE   = 1.0
REL_VEL_SCALE      = 100.0
ROC_VEL_SCALE      = 100.0
ROC_ANG_VEL_SCALE  = 10.0
HEIGHT_SCALE       = 100.0
GRAVITY_SCALE      = 9.81
DISTANCE_SCALE     = 500.0
CLOSING_RATE_SCALE = 120.0

MIN_THRUST      = 600.0
MAX_THRUST      = 1050.0
MAX_PITCH_FORCE = 1.7
MAX_YAW_FORCE   = 1.7
TARGET_VELOCITY = 0.0


def calculate_new_loc():
    theta = np.random.uniform(0, 2 * np.pi)
    px = 0 * np.cos(theta)
    pz = 0 * np.sin(theta)
    ry = 180.0
    rz = 90.0 - np.degrees(np.arctan2(pz, px))
    return px, pz, ry, rz


class Env:
    def __init__(self, ip, port):
        self.connect = connector.Connector(ip, port)
        self.done = False
        self.state_size  = 20
        self.action_size = 3
        self.max_step    = 1300
        self.step_count  = 0
        self.episode_id  = 0
        self.prev_distance  = None
        self.reset_distance = None  # [YENİ] kaçış tespiti için başlangıç mesafesi

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    def read_state(self):
        return self.connect.read_packet()

    def parse_state(self, raw_state):
        s = raw_state["states"]

        # [DEĞİŞİKLİK 1] blend_w → time_remaining
        # blend_w uçuş boyunca neredeyse daima 0, terminal olduğunda bölüm
        # zaten bitiyor → faydasız bir slot.
        # time_remaining ajanın zamanı ne kadar kaldığını bilmesini sağlar;
        # timeout yaklaştığında daha agresif davranabilir.
        time_remaining = np.clip(
            (self.max_step - self.step_count) / self.max_step,
            0.0, 1.0
        )

        return np.array([
            s["target_dir"][0], s["target_dir"][1], s["target_dir"][2],
            s["rel_vel"][0],    s["rel_vel"][1],    s["rel_vel"][2],
            s["roc_vel"][0],    s["roc_vel"][1],    s["roc_vel"][2],
            s["roc_ang_vel"][0], s["roc_ang_vel"][1], s["roc_ang_vel"][2],
            s["roc_h"],
            s["height_error"],
            s["g"][0], s["g"][1], s["g"][2],
            s["distance"],
            s["closing_rate"],
            time_remaining,     # index 19
        ], dtype=np.float32)

    def normalize_state(self, vector_state):
        s = vector_state.copy()
        s[0:3]  = np.clip(s[0:3]  / TARGET_DIR_SCALE,   -1.0, 1.0)
        s[3:6]  = np.clip(s[3:6]  / REL_VEL_SCALE,      -1.0, 1.0)
        s[6:9]  = np.clip(s[6:9]  / ROC_VEL_SCALE,      -1.0, 1.0)
        s[9:12] = np.clip(s[9:12] / ROC_ANG_VEL_SCALE,  -1.0, 1.0)
        s[12]   = np.clip(s[12]   / HEIGHT_SCALE,        -1.0, 1.0)
        s[13]   = np.clip(s[13]   / HEIGHT_SCALE,        -1.0, 1.0)
        s[14:17]= np.clip(s[14:17]/ GRAVITY_SCALE,       -1.0, 1.0)
        s[17]   = np.clip(s[17]   / DISTANCE_SCALE,      -1.0, 1.0)
        s[18]   = np.clip(s[18]   / CLOSING_RATE_SCALE,  -1.0, 1.0)
        s[19]   = np.clip(s[19],                          0.0,  1.0) # time_remaining zaten [0,1]
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
        vector_state     = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)
        self.prev_distance  = float(raw_state["states"]["distance"])
        self.reset_distance = self.prev_distance  # [YENİ] kaçış tespiti için başlangıç mesafesi
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

        distance    = float(states["distance"])
        agl         = float(states["roc_h"])
        grounded    = float(states["blend_w"]) > 0.5
        closing_rate = float(states["closing_rate"])

        # [DEĞİŞİKLİK 2] Hizalama sinyali için target_dir[2]
        # Roketin yerel ekseninde (rocketPoint.forward = +Z), target_dir[2] = cos(sapma açısı).
        # +1 → burun tam hedefe bakıyor, −1 → tam tersi yön.
        # Sadece pozitif tarafı ödüllendiriyoruz (max 0 ile kırpıyoruz).
        target_dir_z = float(states["target_dir"][2])

        # [DEĞİŞİKLİK 3] Açısal hız büyüklüğü (takla cezası için)
        av = states["roc_ang_vel"]
        ang_vel_mag = float(np.sqrt(av[0]**2 + av[1]**2 + av[2]**2))

        # --- Sabitler ---
        STEP_PENALTY         = -0.018
        DISTANCE_GAIN        =  0.35   # [DEĞİŞİKLİK 4] 0.35 → 0.30 (yeni ödüllerle denge)
        DISTANCE_DELTA_CLIP  = 10.0
        CLOSING_RATE_GAIN    =  0.017  # [DEĞİŞİKLİK 5] 0.004 → 0.010
        CLOSING_RATE_CLIP    = 80.0
        ALIGNMENT_GAIN       =  0.045   # [YENİ] cos(sapma) ödülü, maks 0.04/adım
        ANG_VEL_PENALTY      =  0.004  # [YENİ] açısal hız cezası katsayısı
        ANG_VEL_CLIP         = 10.0    # [YENİ] rad/s üst sınırı

        SUCCESS_DISTANCE     = 12.0
        # [DEĞİŞİKLİK 6] MIN_AGL 0.40 → 0.25
        # Roket rampada 0.406m AGL'de başlıyor, bu değer eski eşiğe çok yakındı.
        # 0.25'e düşürerek kalkış sırasında erken terminal cezası engelleniyor.
        MIN_AGL              =  0.35
        # [DEĞİŞİKLİK 7] Düşük irtifa grace süresi 8 → 15
        # Rampadan kalkış için daha uzun tolerans tanımlıyoruz.
        LOW_AGL_GRACE_STEPS  = 15
        MAX_ALTITUDE         = 100.0

        SUCCESS_REWARD       =  210.0
        COLLISION_PENALTY    = -100.0
        LOW_ALTITUDE_PENALTY =  -75.0
        HIGH_ALTITUDE_PENALTY = -82.0
        TIMEOUT_PENALTY      =  -60.0
        # Kaçış terminali
        ESCAPE_MULTIPLIER    =  1.4    # [DEĞİŞİKLİK] 1.5 → 1.4: EP11'de max mesafe 445m iken
                                       # reset=303m, 1.5×=454m tetiklenmiyordu; 1.4×=424m → step 532'de yakalar
        ESCAPE_PENALTY       = -50.0
        ESCAPE_GRACE_STEPS   =  50

        # [YENİ] İrtifa hizalama ödülü
        # height_error state'te var ama reward'da katkısı sıfırdı; ajan hedef irtifasını görmezden geliyordu.
        # height_error = target_h − agl; 0 olduğunda roket tam hedef irtifasında.
        # Formül: gain × (1 − |height_error| / 100)
        # Katkı aralığı: h_err=0 → +0.020, h_err=50 → +0.010, h_err≥100 → 0
        HEIGHT_ALIGN_GAIN    =  0.015

        # [YENİ] Zemin yumuşak cezası (soft floor)
        # Adımların %19.9'u roc_h < 5m. Terminal gelmeden önce sürekli sinyal olmalı.
        # Formül: −gain × (SOFT_FLOOR − agl) if agl < SOFT_FLOOR else 0
        # Katkı aralığı: agl=0 → −0.200, agl=3 → −0.080, agl≥5 → 0
        SOFT_FLOOR           =  5.0
        SOFT_FLOOR_GAIN      =  0.040

        reward = STEP_PENALTY
        done = False
        done_reason = None
        success = False

        # Mesafe delta ödülü
        delta_distance = self.prev_distance - distance
        delta_distance = np.clip(delta_distance, -DISTANCE_DELTA_CLIP, DISTANCE_DELTA_CLIP)
        reward += DISTANCE_GAIN * delta_distance

        # Kapanma hızı ödülü (artık daha ağırlıklı)
        reward += CLOSING_RATE_GAIN * np.clip(closing_rate, -CLOSING_RATE_CLIP, CLOSING_RATE_CLIP)

        # [YENİ] Hizalama ödülü: burun hedefi gösteriyorsa bonus
        # target_dir[2] yerel eksende cos(sapma açısı), +1 = mükemmel hizalama
        reward += ALIGNMENT_GAIN * max(0.0, target_dir_z)

        # [YENİ] Açısal hız cezası: takla atan roketi caydır
        reward -= ANG_VEL_PENALTY * min(ang_vel_mag, ANG_VEL_CLIP)

        # [YENİ] İrtifa hizalama ödülü: hedef irtifasına yaklaşmayı teşvik eder
        height_error = np.abs(float(states["height_error"]))
        reward -= HEIGHT_ALIGN_GAIN * height_error

        # [YENİ] Zemin yumuşak cezası: terminale ulaşmadan önce sürekli uyarı sinyali
        if agl < SOFT_FLOOR:
            reward -= SOFT_FLOOR_GAIN * (SOFT_FLOOR - agl)

        # Terminal koşullar
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
        elif (self.step_count >= self.max_step):
            reward += TIMEOUT_PENALTY
            done = True
            done_reason = "timeout"
        elif (self.step_count > ESCAPE_GRACE_STEPS
              and self.reset_distance is not None
              and distance > self.reset_distance * ESCAPE_MULTIPLIER):
            # [YENİ] Kaçış tespiti: başlangıç mesafesinin 1.5 katına çıktı
            reward += ESCAPE_PENALTY
            done = True
            done_reason = "escaped"

        self.prev_distance = distance

        reward_info = {
            "reward_total":  float(reward),
            "distance":      float(distance),
            "delta_distance":float(delta_distance),
            "roc_h":         float(agl),
            "closing_rate":  float(closing_rate),
            "height_error":  float(states["height_error"]),
            "alignment":     float(target_dir_z),
            "ang_vel_mag":   float(ang_vel_mag),
            "grounded":      grounded,
            "done_reason":   done_reason,
            "success":       success,
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
            "step_id":    self.step_count,
            "type":       "action",
            "values":     denorm_action
        }

        self.connect.send_packet(action_dict)

        raw_state        = self.read_state()
        vector_state     = self.parse_state(raw_state)
        normalized_state = self.normalize_state(vector_state)

        reward, done, reward_info = self.calculate_reward(raw_state)

        info = self.build_info(
            raw_state=raw_state,
            denorm_action=denorm_action,
            reward=reward,
            done=done,
            done_reason=reward_info["done_reason"]
        )
        info["grounded"]    = reward_info["grounded"]
        info["alignment"]   = reward_info["alignment"]
        info["ang_vel_mag"] = reward_info["ang_vel_mag"]

        self.done = done
        return normalized_state, reward, done, info

    # ------------------------------------------------------------------
    # YARDIMCI METODLAR
    # ------------------------------------------------------------------

    def denormalize_action(self, action):
        a = np.asarray(action, dtype=np.float32)
        a = np.clip(a, -1.0, 1.0)

        thrust  = MIN_THRUST + ((a[0] + 1.0) / 2.0) * (MAX_THRUST - MIN_THRUST)
        pitch_f = a[1] * MAX_PITCH_FORCE
        yaw_f   = a[2] * MAX_YAW_FORCE

        return [float(thrust), float(pitch_f), float(yaw_f)]

    def build_info(self, raw_state, denorm_action=None, reward=None, done=None, done_reason=None):
        s = raw_state["states"]

        info = {
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "episode_id":   raw_state["episode_id"],
            "step_id":      raw_state["step_id"],

            "reward":       reward,
            "done":         done,
            "done_reason":  done_reason,

            "target_dir_x": s["target_dir"][0],
            "target_dir_y": s["target_dir"][1],
            "target_dir_z": s["target_dir"][2],

            "rel_vel_x":    s["rel_vel"][0],
            "rel_vel_y":    s["rel_vel"][1],
            "rel_vel_z":    s["rel_vel"][2],

            "roc_vel_x":    s["roc_vel"][0],
            "roc_vel_y":    s["roc_vel"][1],
            "roc_vel_z":    s["roc_vel"][2],

            "roc_ang_vel_x": s["roc_ang_vel"][0],
            "roc_ang_vel_y": s["roc_ang_vel"][1],
            "roc_ang_vel_z": s["roc_ang_vel"][2],

            "roc_h":         s["roc_h"],
            "height_error":  s["height_error"],

            "gx": s["g"][0],
            "gy": s["g"][1],
            "gz": s["g"][2],

            "distance":      s["distance"],
            "closing_rate":  s["closing_rate"],
            "blend_w":       s["blend_w"],  # sadece log/reward hesabı için saklanıyor
        }

        if denorm_action is not None:
            info["thrust"]   = denorm_action[0]
            info["pitch_f"]  = denorm_action[1]
            info["yaw_f"]    = denorm_action[2]
        else:
            info["thrust"]   = None
            info["pitch_f"]  = None
            info["yaw_f"]    = None

        return info

    def close(self):
        self.connect.close()