import os
import csv
from datetime import datetime

LOG_DIR = "logs"
STEP_LOG_FILE = os.path.join(LOG_DIR,"step_log.csv")
EPISODE_LOG_FILE =  os.path.join(LOG_DIR,"episode_log.csv")
UPDATE_LOG_FILE = os.path.join(LOG_DIR,"update_log.csv")

STEP_PRINT_EVERY = 50

GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def ensure_log_files():
    os.makedirs(LOG_DIR,exist_ok=True)

    if not os.path.exists(STEP_LOG_FILE):
        with open(STEP_LOG_FILE, "w", newline="",encoding="utf-8") as f:
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
                "closing_rate",
                "roc_h",
                "target_h",
                "blend_w",
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
                "thrust",
                "pitch_f",
                "yaw_f",
            ])
    
    if not os.path.exists(EPISODE_LOG_FILE):
        with open(EPISODE_LOG_FILE, "w",newline="",encoding="utf-8") as f:
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
                "start_target_h",
                "final_target_h"
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
            info["closing_rate"],
            info["roc_h"],
            info["target_h"],
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
            info["yaw_f"]
        ])

def append_episode_csv(update_id, episode_id, episode_return, episode_len, done_reason, start_info, final_info):
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
            start_info["target_h"],
            final_info["target_h"]
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
    msg = (
        f"[UP {update_id:<4} | EP {info['episode_id']:<4} | ST {info['step_id']:<4}] "
        f"Dst: {info['distance']:>7.2f} | "
        f"RocH: {info['roc_h']:>6.2f} | "
        f"TarH: {info['target_h']:>6.2f} | "
        f"CR: {info['closing_rate']:>7.2f} | "
        f"R: {info['reward']:>7.3f} | "
        f"Act: [{info['thrust']:.2f}, {info['pitch_f']:.2f}, {info['yaw_f']:.2f}]"
    )
    print(msg, flush=True)


def print_episode_console(episode_id, episode_return, episode_len, done_reason, start_info, final_info):
    timestamp = datetime.now().strftime("%H:%M:%S")

    msg = (
        f"[EP {episode_id:<5}] {done_reason:<12} | "
        f"Ret: {episode_return:>8.2f} | "
        f"Len: {episode_len:>4} | "
        f"Start D/H: {start_info['distance']:>6.1f} / {start_info['roc_h']:>6.1f} | "
        f"End D/H: {final_info['distance']:>6.1f} / {final_info['roc_h']:>6.1f} | "
        f"{timestamp}"
    )

    if done_reason == "success":
        print(f"{GREEN}{msg}{RESET}", flush=True)
    else:
        print(msg, flush=True)


def print_update_console(update_id, logs):
    timestamp = datetime.now().strftime("%H:%M:%S")

    msg = (
        f"[UP {update_id:>4}] "
        f"loss={logs.get('loss',0.0):.4f} | "
        f"policy={logs.get('policy_loss',0.0):.4f} | "
        f"value={logs.get('value_loss',0.0):.4f} | "
        f"ent={logs.get('entropy',0.0):.4f} | "
        f"kl={logs.get('kl',0.0):.4f} | "
        f"clip={logs.get('clip_frac', 0.0)} | "
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
        lam=agent.lam,
        lr=agent.lr
    )

    print_update_console(update_id=up, logs=logs)  

"""





