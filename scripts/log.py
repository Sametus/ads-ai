import os
import csv
from datetime import datetime

LOG_DIR = "logs"
STEP_LOG_FILE    = os.path.join(LOG_DIR, "step_log.csv")
EPISODE_LOG_FILE = os.path.join(LOG_DIR, "episode_log.csv")
UPDATE_LOG_FILE  = os.path.join(LOG_DIR, "update_log.csv")

STEP_PRINT_EVERY = 25

GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
RESET   = "\033[0m"

def ensure_log_files():
    os.makedirs(LOG_DIR, exist_ok=True)

    if not os.path.exists(STEP_LOG_FILE):
        with open(STEP_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "update_id",
                "episode_id",
                "step_id",
                "reward",
                "done",
                "done_reason",
                # --- durum bileşenleri ---
                "distance",
                "look_angle_rad",
                "look_angle_deg",
                "roc_h",
                "height_error",
                "blend_w",          # Unity'den gelen ham grounded flag (reward hesabında kullanılır)
                                    # NOT: state vektörü index 19 = time_remaining (Python'da hesaplanır)
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
                "gx",
                "gy",
                "gz",
                # --- aksiyon ---
                "thrust",
                "pitch_f",
                "yaw_f",
                # --- yeni reward sinyal tanıları ---
                "alignment",        # target_dir[2] = cos(sapma açısı), +1 = mükemmel hizalama
                "ang_vel_mag",      # |ω| rad/s, yüksekse ceza alıyor
            ])

    if not os.path.exists(EPISODE_LOG_FILE):
        with open(EPISODE_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "update_id",
                "episode_id",
                "episode_return",
                "episode_len",
                "done_reason",
                "start_distance",
                "final_distance",
                "start_roc_h",
                "final_roc_h",
                "start_height_error",
                "final_height_error",
                "final_look_angle_rad",
                "final_look_angle_deg",
                "final_alignment",
                "final_ang_vel_mag",
            ])

    if not os.path.exists(UPDATE_LOG_FILE):
        with open(UPDATE_LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "update_id",
                "loss",
                "policy_loss",
                "value_loss",
                "entropy",
                "kl",
                "clip_frac",
                "gamma",
                "lam",
                "lr"
            ])


def append_step_csv(update_id, info):
    with open(STEP_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            info["timestamp"],
            update_id,
            info["episode_id"],
            info["step_id"],
            info["reward"],
            int(info["done"]) if info["done"] is not None else "",
            info["done_reason"],
            info["distance"],
            info["look_angle_rad"],
            info["look_angle_deg"],
            info["roc_h"],
            info["height_error"],
            info["blend_w"],
            info["target_dir_x"],
            info["target_dir_y"],
            info["target_dir_z"],
            info["rel_vel_x"],
            info["rel_vel_y"],
            info["rel_vel_z"],
            info["roc_vel_x"],
            info["roc_vel_y"],
            info["roc_vel_z"],
            info["roc_ang_vel_x"],
            info["roc_ang_vel_y"],
            info["roc_ang_vel_z"],
            info["gx"],
            info["gy"],
            info["gz"],
            info["thrust"],
            info["pitch_f"],
            info["yaw_f"],
            info.get("alignment", ""),      # [YENİ] yoksa boş bırak (reset adımı)
            info.get("ang_vel_mag", ""),     # [YENİ] yoksa boş bırak (reset adımı)
        ])


def append_episode_csv(update_id, episode_id, episode_return, episode_len,
                       done_reason, start_info, final_info):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M-%S")

    with open(EPISODE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
        timestamp,
        update_id,
        episode_id,
        episode_return,
        episode_len,
        done_reason,
        start_info["distance"],
        final_info["distance"],
        start_info["roc_h"],
        final_info["roc_h"],
        start_info["height_error"],
        final_info["height_error"],
        final_info.get("look_angle_rad", ""),
        final_info.get("look_angle_deg", ""),
        final_info.get("alignment", ""),
        final_info.get("ang_vel_mag", ""),
    ])


def append_update_csv(update_id, logs, gamma, lam, lr):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(UPDATE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            update_id,
            logs.get("loss"),
            logs.get("policy_loss"),
            logs.get("value_loss"),
            logs.get("entropy"),
            logs.get("kl"),
            logs.get("clip_frac"),
            gamma,
            lam,
            lr
        ])


###############
# CONSOLE LOG #
###############

def print_step_console(update_id, info):
    # [DEĞİŞİKLİK] alignment sütunu eklendi, blend_w kaldırıldı (neredeyse hep 0)
    align_str = f"{info['alignment']:>5.2f}" if info.get("alignment") is not None else "  N/A"
    msg = (
        f"[UP {update_id:<4} | EP {info['episode_id']:<4} | ST {info['step_id']:<4}] "
        f"Dst: {info['distance']:>7.2f} | "
        f"RocH: {info['roc_h']:>6.2f} | "
        f"ErrH: {info['height_error']:>6.2f} | "
        f"Ang: {info['look_angle_deg']:>7.2f}° | "
        f"Aln: {align_str} | "
        f"R: {info['reward']:>7.3f} | "
        f"Act: [{info['thrust']:.2f}, {info['pitch_f']:.2f}, {info['yaw_f']:.2f}]"
    )
    print(msg, flush=True)


def print_episode_console(episode_id, episode_return, episode_len,
                          done_reason, start_info, final_info,
                          success_count, total_episode_count):
    timestamp = datetime.now().strftime("%H:%M:%S")

    final_align = final_info.get("alignment")
    align_str = f" | Aln: {final_align:>5.2f}" if final_align is not None else ""

    success_rate = 100.0 * success_count / max(1, total_episode_count)

    msg = (
        f"[EP {episode_id:<5}] {done_reason:<12} | "
        f"Ret: {episode_return:>8.2f} | "
        f"Len: {episode_len:>4} | "
        f"Start D/H: {start_info['distance']:>6.1f} / {start_info['roc_h']:>6.1f} | "
        f"End D/H: {final_info['distance']:>6.1f} / {final_info['roc_h']:>6.1f}"
        f"{align_str} | "
        f"Succ: {success_count}/{total_episode_count} ({success_rate:>6.2f}%) | "
        f"{timestamp}"
    )

    if done_reason == "success":
        color = GREEN
    elif done_reason in ["low_agl", "low_altitude"]:
        color = YELLOW
    elif done_reason == "high_altitude":
        color = MAGENTA
    elif done_reason == "timeout":
        color = RED
    elif done_reason == "escaped":
        color = CYAN
    elif done_reason == "bad_angle":
        color = RED
    else:
        color = RESET

    print(f"{color}{msg}{RESET}", flush=True)


def print_update_console(update_id, logs):
    timestamp = datetime.now().strftime("%H:%M:%S")

    msg = (
        f"[UP {update_id:>4}] "
        f"loss={logs.get('loss', 0.0):.4f} | "
        f"policy={logs.get('policy_loss', 0.0):.4f} | "
        f"value={logs.get('value_loss', 0.0):.4f} | "
        f"ent={logs.get('entropy', 0.0):.4f} | "
        f"kl={logs.get('kl', 0.0):.4f} | "
        f"clip={logs.get('clip_frac', 0.0):.4f} | "
        f"{timestamp}"
    )
    print(msg, flush=True)


def print_reset_console(episode_id, start_info):
    px = start_info["reset_px"]
    py = start_info["reset_py"]
    pz = start_info["reset_pz"]
    ry = start_info["reset_ry"]
    rz = start_info["reset_rz"]

    msg = (
        f"[EP {episode_id:<5}] RESET | "
        f"Target Pos: ({px:.2f}, {py:.2f}, {pz:.2f}) | "
        f"Rot: ({ry:.2f}, {rz:.2f})"
    )
    print(msg, flush=True)



def load_success_counters():
    if not os.path.exists(EPISODE_LOG_FILE):
        return 0, 0

    total_episode_count = 0
    total_success_count = 0

    with open(EPISODE_LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_episode_count += 1
            if row.get("done_reason", "") == "success":
                total_success_count += 1

    return total_episode_count, total_success_count
"""
Başlangıçta:
    ensure_log_files()

Her Step Sonunda:
    append_step_csv(update_id=up, info=info)

    if info["step_id"] % STEP_PRINT_EVERY == 0:
        print_step_console(update_id=up, info=info)

Episode Bitince:
    append_episode_csv(
        update_id=up,
        episode_id=episode_id,
        episode_return=ep_return,
        episode_len=ep_len,
        done_reason=info["done_reason"],
        start_info=start_info,
        final_info=info
    )

    print_episode_console(
        episode_id=episode_id,
        episode_return=ep_return,
        episode_len=ep_len,
        done_reason=info["done_reason"],
        start_info=start_info,
        final_info=info
    )

PPO Bitince:
    append_update_csv(
        update_id=up,
        logs=logs,
        gamma=agent.gamma,
        lam=agent.gae_lambda,
        lr=agent.lr
    )

    print_update_console(update_id=up, logs=logs)
"""