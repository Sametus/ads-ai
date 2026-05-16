import csv
import os
from datetime import datetime

from env import PYTHON_STEP_LOG_KEYS, REWARD_BREAKDOWN_KEYS, TELEMETRY_FLAT_KEYS

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


def _terminal_color(done_reason):
    """Terminal nedenlerini konsolda ayni renklerle gosterir."""
    if done_reason == "success":
        return GREEN
    if done_reason in ["low_agl", "low_altitude"]:
        return YELLOW
    if done_reason == "high_altitude":
        return MAGENTA
    if done_reason in ["bad_angle", "wrong_way", "collision", "timeout", "missed_intercept"]:
        return RED
    if done_reason in ["near_miss", "escaped"]:
        return CYAN
    return RESET

STEP_HEADER = [
    "timestamp",
    "update_id",
    "episode_id",
    "step_id",
    "phase_id",
    "phase_name",
    "max_step",
    "reward",
    "reward_total",
    "done",
    "done_reason",
    "success",
    "near_miss_candidate",
    "distance",
    "delta_distance",
    "theta_rad",
    "theta_deg",
    "alpha_rad",
    "alpha_deg",
    "beta_rad",
    "beta_deg",
    "alignment",
    "closing_speed",
    "forward_up_dot",
    "clock_validity",
    "agl",
    "alt_error",
    "grounded_flag",
    "ang_vel_mag",
    "target_clock_12",
    "target_clock_6",
    "target_clock_3",
    "target_clock_9",
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
    "thrust",
    "clock_12_cmd",
    "clock_6_cmd",
    "clock_3_cmd",
    "clock_9_cmd",
] + PYTHON_STEP_LOG_KEYS + REWARD_BREAKDOWN_KEYS + TELEMETRY_FLAT_KEYS

EPISODE_HEADER = [
    "timestamp",
    "update_id",
    "episode_id",
    "phase_id",
    "phase_name",
    "max_step",
    "episode_return",
    "episode_len",
    "done_reason",
    "start_distance",
    "final_distance",
    "start_target_distance",
    "final_target_distance",
    "final_target_hit_trigger",
    "start_agl",
    "final_agl",
    "start_alt_error",
    "final_alt_error",
    "final_closing_speed",
    "final_theta_deg",
    "final_alpha_deg",
    "final_beta_deg",
    "final_alignment",
    "final_forward_up_dot",
    "final_grounded_flag",
    "final_ang_vel_mag",
]

UPDATE_HEADER = [
    "timestamp",
    "update_id",
    "loss",
    "policy_loss",
    "value_loss",
    "entropy",
    "kl",
    "clip_frac",
    "alpha",
    "q1_loss",
    "q2_loss",
    "gamma",
    "lam",
    "lr",
]


def _rotate_if_header_mismatch(path, header):
    if not os.path.exists(path):
        return

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        existing_header = next(reader, None)

    if existing_header == header:
        return

    stem, ext = os.path.splitext(path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{stem}.bak_{timestamp}{ext}"
    os.replace(path, backup_path)


def _ensure_csv(path, header):
    _rotate_if_header_mismatch(path, header)

    if os.path.exists(path):
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def _normalize_row(header, values):
    row = []

    for key in header:
        value = values.get(key, "")

        if value is None:
            row.append("")
        elif isinstance(value, bool):
            row.append(int(value))
        else:
            row.append(value)

    return row


def ensure_log_files():
    os.makedirs(LOG_DIR, exist_ok=True)
    _ensure_csv(STEP_LOG_FILE, STEP_HEADER)
    _ensure_csv(EPISODE_LOG_FILE, EPISODE_HEADER)
    _ensure_csv(UPDATE_LOG_FILE, UPDATE_HEADER)


def append_step_csv(update_id, info):
    record = dict(info)
    record["update_id"] = update_id

    with open(STEP_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_normalize_row(STEP_HEADER, record))


def append_episode_csv(update_id, episode_id, episode_return, episode_len,
                       done_reason, start_info, final_info):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "update_id": update_id,
        "episode_id": episode_id,
        "phase_id": final_info.get("phase_id", start_info.get("phase_id", "")),
        "phase_name": final_info.get("phase_name", start_info.get("phase_name", "")),
        "max_step": final_info.get("max_step", start_info.get("max_step", "")),
        "episode_return": episode_return,
        "episode_len": episode_len,
        "done_reason": done_reason,
        "start_distance": start_info["distance"],
        "final_distance": final_info["distance"],
        "start_target_distance": start_info.get("target_distance", ""),
        "final_target_distance": final_info.get("target_distance", ""),
        "final_target_hit_trigger": final_info.get("target_hit_trigger", ""),
        "start_agl": start_info["agl"],
        "final_agl": final_info["agl"],
        "start_alt_error": start_info["alt_error"],
        "final_alt_error": final_info["alt_error"],
        "final_closing_speed": final_info.get("closing_speed", ""),
        "final_theta_deg": final_info.get("theta_deg", ""),
        "final_alpha_deg": final_info.get("alpha_deg", ""),
        "final_beta_deg": final_info.get("beta_deg", ""),
        "final_alignment": final_info.get("alignment", ""),
        "final_forward_up_dot": final_info.get("forward_up_dot", ""),
        "final_grounded_flag": final_info.get("grounded_flag", ""),
        "final_ang_vel_mag": final_info.get("ang_vel_mag", ""),
    }

    with open(EPISODE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_normalize_row(EPISODE_HEADER, record))


def append_update_csv(update_id, logs, gamma, lam, lr):
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "update_id": update_id,
        "loss": logs.get("loss"),
        "policy_loss": logs.get("policy_loss"),
        "value_loss": logs.get("value_loss"),
        "entropy": logs.get("entropy"),
        "kl": logs.get("kl"),
        "clip_frac": logs.get("clip_frac"),
        "alpha": logs.get("alpha", logs.get("clip_frac")),
        "q1_loss": logs.get("q1_loss"),
        "q2_loss": logs.get("q2_loss"),
        "gamma": gamma,
        "lam": lam,
        "lr": lr,
    }

    with open(UPDATE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(_normalize_row(UPDATE_HEADER, record))


def print_step_console(update_id, info):
    if info.get("turn_direction_name") in ("direct_accel", "body_accel", "guidance_accel"):
        action_text = (
            f"Acc: [{info.get('direct_accel_world_x', 0.0):.1f}, "
            f"{info.get('direct_accel_world_y', 0.0):.1f}, "
            f"{info.get('direct_accel_world_z', 0.0):.1f}]"
        )
    else:
        action_text = (
            f"Act: [{info['thrust']:.2f}, {info['clock_12_cmd']:.2f}, {info['clock_6_cmd']:.2f}, "
            f"{info['clock_3_cmd']:.2f}, {info['clock_9_cmd']:.2f}]"
        )

    msg = (
        f"[UP {update_id:<4} | EP {info['episode_id']:<4} | ST {info['step_id']:<4}] "
        f"Dst: {info['distance']:>7.2f} | "
        f"TgtD: {info.get('target_distance', 0.0):>7.2f} | "
        f"Theta: {info['theta_deg']:>7.2f} | "
        f"Alpha/Beta: {info['alpha_deg']:>6.2f} / {info['beta_deg']:>6.2f} | "
        f"Cls: {info['closing_speed']:>6.2f} | "
        f"AGL: {info['agl']:>6.2f} | "
        f"AltE: {info['alt_error']:>6.2f} | "
        f"Aln: {info.get('alignment', 0.0):>5.2f} | "
        f"R: {info['reward']:>7.3f} | "
        f"TC: [{info.get('target_clock_12', 0.0):.2f},{info.get('target_clock_6', 0.0):.2f},"
        f"{info.get('target_clock_3', 0.0):.2f},{info.get('target_clock_9', 0.0):.2f}] | "
        f"Dir: {info.get('turn_direction_name', 'n/a')}#{info.get('turn_direction_id', '')} | "
        f"{action_text}"
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
        f"End D/TgtD/AGL: {final_info['distance']:>6.1f} / "
        f"{final_info.get('target_distance', 0.0):>6.1f} / {final_info['agl']:>6.1f} | "
        f"Theta: {final_info.get('theta_deg', 0.0):>6.2f} | "
        f"A/B: {final_info.get('alpha_deg', 0.0):>6.2f}/{final_info.get('beta_deg', 0.0):>6.2f} | "
        f"Cls: {final_info.get('closing_speed', 0.0):>6.2f} | "
        f"Aln: {final_info.get('alignment', 0.0):>5.2f} | "
        f"Succ: {success_count}/{total_episode_count} ({success_rate:>6.2f}%) | "
        f"{timestamp}"
    )

    color = _terminal_color(done_reason)

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
        f"alpha={logs.get('alpha', logs.get('clip_frac', 0.0)):.4f} | "
        f"{timestamp}"
    )
    print(msg, flush=True)


def print_reset_console(episode_id, start_info):
    rocket_pos = (
        start_info.get("rocket_pos_world_x", 0.0),
        start_info.get("rocket_pos_world_y", 0.0),
        start_info.get("rocket_pos_world_z", 0.0),
    )
    msg = (
        f"[EP {episode_id:<5}] RESET | "
        f"Phase: {start_info.get('phase_id', '')} {start_info.get('phase_name', '')} | "
        f"Target Pos: ({start_info['reset_px']:.2f}, {start_info['reset_py']:.2f}, {start_info['reset_pz']:.2f}) | "
        f"Rocket Pos: ({rocket_pos[0]:.2f}, {rocket_pos[1]:.2f}, {rocket_pos[2]:.2f}) | "
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
