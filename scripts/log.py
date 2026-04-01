import csv
import os
from datetime import datetime

LOG_DIR = "logs"
STEP_LOG_FILE = os.path.join(LOG_DIR, "step_log.csv")
EPISODE_LOG_FILE = os.path.join(LOG_DIR, "episode_log.csv")
UPDATE_LOG_FILE = os.path.join(LOG_DIR, "update_log.csv")

STEP_PRINT_EVERY = 25

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"


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
                "distance",
                "closing_speed",
                "los_yaw_deg",
                "los_pitch_deg",
                "alignment",
                "agl",
                "alt_error",
                "grounded_flag",
                "ang_vel_mag",
                "rel_vel_x",
                "rel_vel_y",
                "rel_vel_z",
                "roc_ang_vel_x",
                "roc_ang_vel_y",
                "roc_ang_vel_z",
                "g_x",
                "g_y",
                "g_z",
                "time_remaining",
                "thrust",
                "pitch_f",
                "yaw_f",
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
                "start_agl",
                "final_agl",
                "start_alt_error",
                "final_alt_error",
                "final_closing_speed",
                "final_los_yaw_deg",
                "final_los_pitch_deg",
                "final_alignment",
                "final_grounded_flag",
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
                "lr",
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
            info["closing_speed"],
            info["los_yaw_deg"],
            info["los_pitch_deg"],
            info.get("alignment", ""),
            info["agl"],
            info["alt_error"],
            info.get("grounded_flag", ""),
            info.get("ang_vel_mag", ""),
            info["rel_vel_x"],
            info["rel_vel_y"],
            info["rel_vel_z"],
            info["roc_ang_vel_x"],
            info["roc_ang_vel_y"],
            info["roc_ang_vel_z"],
            info["g_x"],
            info["g_y"],
            info["g_z"],
            info["time_remaining"],
            info["thrust"],
            info["pitch_f"],
            info["yaw_f"],
        ])


def append_episode_csv(update_id, episode_id, episode_return, episode_len,
                       done_reason, start_info, final_info):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            start_info["agl"],
            final_info["agl"],
            start_info["alt_error"],
            final_info["alt_error"],
            final_info.get("closing_speed", ""),
            final_info.get("los_yaw_deg", ""),
            final_info.get("los_pitch_deg", ""),
            final_info.get("alignment", ""),
            final_info.get("grounded_flag", ""),
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
            lr,
        ])


def print_step_console(update_id, info):
    msg = (
        f"[UP {update_id:<4} | EP {info['episode_id']:<4} | ST {info['step_id']:<4}] "
        f"Dst: {info['distance']:>7.2f} | "
        f"Cls: {info['closing_speed']:>6.2f} | "
        f"Yaw: {info['los_yaw_deg']:>7.2f} deg | "
        f"Pit: {info['los_pitch_deg']:>7.2f} deg | "
        f"AGL: {info['agl']:>6.2f} | "
        f"AltE: {info['alt_error']:>6.2f} | "
        f"Aln: {info.get('alignment', 0.0):>5.2f} | "
        f"R: {info['reward']:>7.3f} | "
        f"Act: [{info['thrust']:.2f}, {info['pitch_f']:.2f}, {info['yaw_f']:.2f}]"
    )
    print(msg, flush=True)


def print_episode_console(episode_id, episode_return, episode_len,
                          done_reason, start_info, final_info,
                          success_count, total_episode_count):
    timestamp = datetime.now().strftime("%H:%M:%S")
    success_rate = 100.0 * success_count / max(1, total_episode_count)

    msg = (
        f"[EP {episode_id:<5}] {done_reason:<12} | "
        f"Ret: {episode_return:>8.2f} | "
        f"Len: {episode_len:>4} | "
        f"Start D/AGL: {start_info['distance']:>6.1f} / {start_info['agl']:>6.1f} | "
        f"End D/AGL: {final_info['distance']:>6.1f} / {final_info['agl']:>6.1f} | "
        f"Cls: {final_info.get('closing_speed', 0.0):>6.2f} | "
        f"Aln: {final_info.get('alignment', 0.0):>5.2f} | "
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
    msg = (
        f"[EP {episode_id:<5}] RESET | "
        f"Target Pos: ({start_info['reset_px']:.2f}, {start_info['reset_py']:.2f}, {start_info['reset_pz']:.2f}) | "
        f"Rot: ({start_info['reset_ry']:.2f}, {start_info['reset_rz']:.2f})"
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
