import argparse
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

from env import ACTIVE_PHASE_CONFIG, get_phase_config


EPISODE_COLS = [
    "update_id",
    "episode_id",
    "phase_name",
    "episode_return",
    "episode_len",
    "done_reason",
    "start_distance",
    "final_distance",
    "final_agl",
    "final_closing_speed",
    "final_theta_deg",
    "final_alignment",
]

STEP_COLS = [
    "update_id",
    "episode_id",
    "step_id",
    "phase_name",
    "reward",
    "done_reason",
    "distance",
    "theta_deg",
    "alignment",
    "closing_speed",
    "agl",
    "action_norm_0",
    "reward_terminal",
    "reward_distance",
    "reward_alignment",
    "reward_closing",
    "reward_theta_progress",
    "reward_alpha_beta",
    "reward_axis_error_penalty",
    "reward_angle_focus",
    "reward_turn_toward",
    "reward_action_alignment",
    "reward_near_success_bonus",
    "reward_reverse_penalty",
]

UPDATE_COLS = ["update_id", "loss", "policy_loss", "value_loss", "entropy", "kl", "clip_frac", "lr"]

REWARD_BASE_TERMS = {
    "distance": ("reward_distance", "distance_gain"),
    "alignment": ("reward_alignment", "alignment_gain"),
    "closing": ("reward_closing", "closing_gain"),
    "theta": ("reward_theta_progress", "theta_progress_gain"),
    "alpha_beta": ("reward_alpha_beta", "alpha_beta_gain"),
    "axis_error": ("reward_axis_error_penalty", "axis_error_penalty_gain"),
    "angle_focus": ("reward_angle_focus", "angle_focus_gain"),
    "turn_toward": ("reward_turn_toward", "turn_toward_gain"),
    "action_alignment": ("reward_action_alignment", "action_alignment_gain"),
    "near_success": ("reward_near_success_bonus", "near_success_gain"),
    "reverse": ("reward_reverse_penalty", "reverse_penalty_gain"),
}


def now_label():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def torch_device(requested):
    if torch is None:
        raise RuntimeError("Torch is not available. Prefer C:\\Python310\\python.exe for CUDA.")
    if requested == "cpu":
        return torch.device("cpu")
    if requested.startswith("cuda") and torch.cuda.is_available():
        return torch.device(requested)
    if requested == "auto" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def read_csv_safe(path, usecols):
    path = Path(path)
    header = pd.read_csv(path, nrows=0).columns.tolist()
    available = [col for col in usecols if col in header]
    last_error = None
    for attempt in range(5):
        try:
            df = pd.read_csv(path, usecols=available, on_bad_lines="skip")
            for col in df.columns:
                if col not in {"phase_name", "done_reason"}:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            return df
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 + attempt)
    raise RuntimeError(f"Could not read {path}: {last_error}")


def load_logs(log_dir, phase_name, min_update):
    log_dir = Path(log_dir)
    episodes = read_csv_safe(log_dir / "episode_log.csv", EPISODE_COLS)
    updates = read_csv_safe(log_dir / "update_log.csv", UPDATE_COLS)
    steps = read_csv_safe(log_dir / "step_log.csv", STEP_COLS)

    episodes["done_reason"] = episodes["done_reason"].fillna("")
    steps["done_reason"] = steps["done_reason"].fillna("")
    episodes["phase_name"] = episodes.get("phase_name", "").fillna("")
    steps["phase_name"] = steps.get("phase_name", "").fillna("")

    if phase_name == "latest":
        non_empty = episodes["phase_name"][episodes["phase_name"].astype(str).str.len() > 0]
        phase_name = non_empty.iloc[-1] if len(non_empty) else ""
    if phase_name:
        episodes = episodes[episodes["phase_name"] == phase_name].copy()
        steps = steps[steps["phase_name"] == phase_name].copy()
    if min_update is not None:
        episodes = episodes[episodes["update_id"] >= min_update].copy()
        steps = steps[steps["update_id"] >= min_update].copy()
        updates = updates[updates["update_id"] >= min_update].copy()

    episode_ids = set(episodes["episode_id"].dropna().astype(int).tolist())
    steps = steps[steps["episode_id"].isin(episode_ids)].copy()
    if len(episodes) == 0 or len(steps) == 0:
        raise RuntimeError("No matching logs found for curriculum reward search.")
    return episodes, updates, steps, phase_name


def make_phase_plan(current_min, current_max, current_step, max_radius):
    increments = [15, 20, 25, 30, 35, 40, 45, 50, 60, 75, 90, 110]
    rows = []
    start = float(current_max)
    phase = 1
    inc_index = 0
    while start < max_radius - 1e-6:
        increment = increments[min(inc_index, len(increments) - 1)]
        end = min(float(max_radius), start + increment)
        radius_mid = 0.5 * (start + end)
        step = current_step + max(0.0, radius_mid - current_max) * 0.85
        step = min(900.0, float(np.ceil(step / 20.0) * 20.0))
        rows.append(
            {
                "planned_phase": phase,
                "radius_min": round(start, 3),
                "radius_max": round(end, 3),
                "radius_mid": round(radius_mid, 3),
                "max_step": step,
            }
        )
        start = end
        phase += 1
        inc_index += 1
    return pd.DataFrame(rows)


def rolling_rate(series, window):
    return series.rolling(window, min_periods=max(5, window // 5)).mean() * 100.0


def tensor(values, device):
    return torch.as_tensor(np.asarray(values, dtype=np.float32), device=device)


def centered_corr(rows, target):
    rows_centered = rows - rows.mean(dim=1, keepdim=True)
    target_centered = target - target.mean()
    denom = torch.sqrt(torch.sum(rows_centered * rows_centered, dim=1) * torch.sum(target_centered * target_centered))
    return torch.sum(rows_centered * target_centered[None, :], dim=1) / torch.clamp(denom, min=1e-6)


def masked_mean(values, mask):
    return (values * mask).sum(dim=1) / torch.clamp(mask.sum(), min=1.0)


def build_episode_diagnostics(episodes, steps, phase):
    work = steps.copy()
    work["done_reason"] = work["episode_id"].map(episodes.set_index("episode_id")["done_reason"]).fillna("")
    idx_min = work.groupby("episode_id")["distance"].idxmin()
    min_rows = work.loc[idx_min, ["episode_id", "distance", "theta_deg", "alignment", "closing_speed", "agl"]].rename(
        columns={
            "distance": "min_distance",
            "theta_deg": "theta_at_min_distance",
            "alignment": "alignment_at_min_distance",
            "closing_speed": "closing_at_min_distance",
            "agl": "agl_at_min_distance",
        }
    )

    named_aggs = {
        "step_count": ("step_id", "count"),
        "mean_theta": ("theta_deg", "mean"),
        "mean_a0": ("action_norm_0", "mean"),
        "high_a0_frac": ("action_norm_0", lambda x: (x > 0.0).mean()),
        "sum_reward": ("reward", "sum"),
    }
    for term, (col, gain_key) in REWARD_BASE_TERMS.items():
        gain = float(phase.get(gain_key, 0.0))
        base_col = f"base_{term}"
        work[base_col] = work[col].fillna(0.0) / gain if abs(gain) > 1e-12 else 0.0
        named_aggs[base_col] = (base_col, "sum")

    diag = episodes.merge(work.groupby("episode_id").agg(**named_aggs).reset_index(), on="episode_id", how="left")
    diag = diag.merge(min_rows, on="episode_id", how="left").fillna(0.0)
    progress_den = diag["start_distance"].replace(0.0, np.nan)
    diag["best_progress_ratio"] = ((diag["start_distance"] - diag["min_distance"]) / progress_den).clip(-1.0, 1.0).fillna(0.0)
    diag["final_progress_ratio"] = ((diag["start_distance"] - diag["final_distance"]) / progress_den).clip(-1.0, 1.0).fillna(0.0)
    diag["theta_score"] = (1.0 - diag["theta_at_min_distance"].fillna(180.0) / 90.0).clip(0.0, 1.0)
    diag["closing_score"] = (diag["closing_at_min_distance"].fillna(-30.0).clip(-30.0, 30.0) + 30.0) / 60.0
    diag["safety_score"] = 1.0 - diag["done_reason"].isin(["low_agl", "high_altitude", "wrong_way"]).astype(float)
    return diag


def update_metrics(episodes, updates, steps):
    per_update = (
        episodes.assign(success_flag=(episodes["done_reason"] == "success").astype(float))
        .groupby("update_id")
        .agg(
            episodes=("episode_id", "count"),
            success_rate=("success_flag", lambda x: 100.0 * x.mean()),
            mean_return=("episode_return", "mean"),
        )
        .reset_index()
    )
    step_update = (
        steps.groupby("update_id")
        .agg(
            mean_theta=("theta_deg", "mean"),
            mean_a0=("action_norm_0", "mean"),
            high_a0_frac=("action_norm_0", lambda x: 100.0 * (x > 0.0).mean()),
        )
        .reset_index()
    )
    return per_update.merge(updates, on="update_id", how="left").merge(step_update, on="update_id", how="left")


def sample_candidates(rng, n, phase, phase_row, radius_norm):
    theta_base = float(phase.get("theta_progress_gain", 0.90))
    alpha_beta_base = float(phase.get("alpha_beta_gain", 0.30))
    angle_base = float(phase.get("angle_focus_gain", 1.10))
    turn_base = float(phase.get("turn_toward_gain", 0.24))
    action_base = float(phase.get("action_alignment_gain", 0.04))
    reverse_base = float(phase.get("reverse_penalty_gain", 0.45))
    near_base = float(phase.get("near_success_gain", 0.25))
    axis_base = float(phase.get("axis_error_penalty_gain", 0.35))

    theta_mult = np.array([0.90, 1.00, 1.10, 1.25, 1.40, 1.60, 1.85], dtype=np.float32)
    if radius_norm > 0.65:
        theta_mult = np.array([1.10, 1.25, 1.40, 1.60, 1.85, 2.10], dtype=np.float32)

    return {
        "theta_progress_gain": theta_base * rng.choice(theta_mult, size=n),
        "alpha_beta_gain": alpha_beta_base * rng.choice(np.array([0.90, 1.00, 1.10, 1.20, 1.35, 1.55], dtype=np.float32), size=n),
        "axis_error_penalty_gain": axis_base * rng.choice(np.array([0.80, 0.95, 1.00, 1.15, 1.30, 1.50], dtype=np.float32), size=n),
        "angle_focus_gain": angle_base * rng.choice(np.array([0.95, 1.05, 1.15, 1.30, 1.45, 1.70], dtype=np.float32), size=n),
        "turn_toward_gain": turn_base * rng.choice(np.array([0.85, 1.00, 1.15, 1.35, 1.60], dtype=np.float32), size=n),
        "action_alignment_gain": action_base * rng.choice(np.array([0.60, 0.80, 1.00, 1.20, 1.50], dtype=np.float32), size=n),
        "reverse_penalty_gain": reverse_base * rng.choice(np.array([0.90, 1.00, 1.15, 1.35, 1.60, 1.90], dtype=np.float32), size=n),
        "near_success_gain": near_base * rng.choice(np.array([0.60, 0.80, 1.00, 1.15, 1.35], dtype=np.float32), size=n),
        "thrust_gate_gain": rng.choice(np.array([0.60, 0.75, 0.90, 1.05, 1.20, 1.40, 1.65], dtype=np.float32), size=n),
        "thrust_gate_target_norm": rng.choice(np.array([-0.45, -0.40, -0.35, -0.30, -0.25, -0.20], dtype=np.float32), size=n),
        "thrust_gate_theta_start_deg": rng.choice(np.array([35.0, 40.0, 45.0, 50.0, 55.0, 60.0], dtype=np.float32), size=n),
        "thrust_gate_theta_span_deg": rng.choice(np.array([12.0, 15.0, 20.0, 25.0, 30.0, 40.0], dtype=np.float32), size=n),
        "thrust_gate_distance_scale": rng.choice(np.array([30.0, 35.0, 40.0, 50.0, 60.0, 75.0], dtype=np.float32), size=n),
        "thrust_gate_distance_floor": rng.choice(np.array([0.35, 0.50, 0.65, 0.80], dtype=np.float32), size=n),
        "min_thrust": rng.choice(np.array([690.0, 700.0, 710.0, 720.0, 730.0], dtype=np.float32), size=n),
        "max_thrust": rng.choice(np.array([820.0, 840.0, 850.0, 870.0, 900.0], dtype=np.float32), size=n),
        "max_step": np.full(n, float(phase_row["max_step"]), dtype=np.float32),
    }


def phase_objective(diag, radius_norm):
    success = (diag["done_reason"] == "success").astype(float)
    near = (diag["done_reason"] == "near_miss").astype(float)
    wrong = diag["done_reason"].isin(["wrong_way", "low_agl", "high_altitude"]).astype(float)
    best_progress = diag["best_progress_ratio"].clip(0.0, 1.0)
    final_progress = ((diag["final_progress_ratio"].clip(-1.0, 1.0) + 1.0) * 0.5)
    theta = diag["theta_score"].clip(0.0, 1.0)
    closing = diag["closing_score"].clip(0.0, 1.0)
    safety = diag["safety_score"].clip(0.0, 1.0)

    theta_w = 0.28 + 0.22 * radius_norm
    progress_w = 0.32 - 0.08 * radius_norm
    closing_w = 0.10 + 0.10 * radius_norm
    return (
        1.00 * success
        + 0.16 * near
        - 0.14 * wrong
        + progress_w * best_progress
        + 0.16 * final_progress
        + theta_w * theta
        + closing_w * closing
        + 0.08 * safety
    )


def run_phase_search(diag, steps, phase, phase_row, radius_norm, device, rng, args, log):
    objective = tensor(phase_objective(diag, radius_norm), device)
    success = tensor((diag["done_reason"] == "success").astype(float), device)
    fail = 1.0 - success
    near = tensor((diag["done_reason"] == "near_miss").astype(float), device)
    bad_terminal = tensor(diag["done_reason"].isin(["wrong_way", "low_agl", "high_altitude"]).astype(float), device)
    step_count = tensor(diag["step_count"], device)
    base = {term: tensor(diag.get(f"base_{term}", 0.0), device) for term in REWARD_BASE_TERMS}

    step_work = steps.copy()
    reason_map = diag.set_index("episode_id")["done_reason"]
    step_work["done_reason"] = step_work["episode_id"].map(reason_map).fillna("")
    step_work = step_work[step_work["reward_terminal"].fillna(0.0).abs() < 1e-9].copy()
    a0 = tensor(step_work["action_norm_0"].fillna(0.0), device)[None, :]
    theta = tensor(step_work["theta_deg"].fillna(0.0), device)[None, :]
    distance = tensor(step_work["distance"].fillna(0.0), device)[None, :]
    step_success = tensor((step_work["done_reason"] == "success").astype(float), device)[None, :]
    step_fail = 1.0 - step_success
    step_near = tensor((step_work["done_reason"] == "near_miss").astype(float), device)[None, :]
    step_bad_high = tensor(((step_work["theta_deg"] > 45.0) & (step_work["action_norm_0"] > 0.0)).astype(float), device)[None, :]
    step_good_low = tensor(((step_work["theta_deg"] <= 45.0) & (step_work["done_reason"] == "success")).astype(float), device)[None, :]

    start_time = time.time()
    total_candidates = 0
    phase_top = []
    phase_id = int(phase_row["planned_phase"])
    while True:
        if time.time() - start_time >= args.seconds_per_phase and total_candidates > 0:
            break
        candidates = sample_candidates(rng, args.candidates_per_round, phase, phase_row, radius_norm)
        for start_idx in range(0, args.candidates_per_round, args.batch_size):
            end_idx = min(args.candidates_per_round, start_idx + args.batch_size)

            def c(name):
                return torch.as_tensor(candidates[name][start_idx:end_idx], device=device)

            theta_gain = c("theta_progress_gain")
            alpha_beta_gain = c("alpha_beta_gain")
            axis_gain = c("axis_error_penalty_gain")
            angle_gain = c("angle_focus_gain")
            turn_gain = c("turn_toward_gain")
            action_gain = c("action_alignment_gain")
            reverse_gain = c("reverse_penalty_gain")
            near_gain = c("near_success_gain")
            thrust_gain = c("thrust_gate_gain")
            thrust_target = c("thrust_gate_target_norm")
            thrust_theta_start = c("thrust_gate_theta_start_deg")
            thrust_theta_span = c("thrust_gate_theta_span_deg")
            thrust_dist_scale = c("thrust_gate_distance_scale")
            thrust_dist_floor = c("thrust_gate_distance_floor")
            min_thrust = c("min_thrust")
            max_thrust = c("max_thrust")

            dense_reward = (
                float(phase.get("step_penalty", -0.04)) * step_count[None, :]
                + float(phase.get("distance_gain", 0.0)) * base["distance"][None, :]
                + float(phase.get("alignment_gain", 0.0)) * base["alignment"][None, :]
                + float(phase.get("closing_gain", 0.0)) * base["closing"][None, :]
                + theta_gain[:, None] * base["theta"][None, :]
                + alpha_beta_gain[:, None] * base["alpha_beta"][None, :]
                + axis_gain[:, None] * base["axis_error"][None, :]
                + angle_gain[:, None] * base["angle_focus"][None, :]
                + turn_gain[:, None] * base["turn_toward"][None, :]
                + action_gain[:, None] * base["action_alignment"][None, :]
                + near_gain[:, None] * base["near_success"][None, :]
                + reverse_gain[:, None] * base["reverse"][None, :]
            )
            reward_corr = centered_corr(dense_reward, objective)
            reward_sep = masked_mean(dense_reward, success) - masked_mean(dense_reward, fail)
            failure_order = masked_mean(dense_reward, near) - masked_mean(dense_reward, bad_terminal)

            thrust_excess = torch.clamp(a0 - thrust_target[:, None], min=0.0)
            theta_gate = torch.clamp((theta - thrust_theta_start[:, None]) / torch.clamp(thrust_theta_span[:, None], min=1.0), 0.0, 1.0)
            dist_gate = thrust_dist_floor[:, None] + (1.0 - thrust_dist_floor[:, None]) * torch.clamp(
                distance / torch.clamp(thrust_dist_scale[:, None], min=1.0), 0.0, 1.0
            )
            thrust_penalty = thrust_gain[:, None] * thrust_excess * theta_gate * dist_gate
            succ_pen = masked_mean(thrust_penalty, step_success)
            fail_pen = masked_mean(thrust_penalty, step_fail)
            near_pen = masked_mean(thrust_penalty, step_near)
            bad_high_pen = masked_mean(thrust_penalty, step_bad_high)
            good_low_pen = masked_mean(thrust_penalty, step_good_low)
            thrust_score = 4.0 * fail_pen + 1.5 * near_pen + 3.0 * bad_high_pen - 10.0 * succ_pen - 7.0 * good_low_pen
            thrust_score = thrust_score - torch.relu(succ_pen - 0.040) * 28.0

            radius_reward = radius_norm * (12.0 * reward_corr + 0.04 * reward_sep + 0.04 * failure_order)
            thrust_width = max_thrust - min_thrust
            thrust_band_score = -torch.relu(thrust_width - 180.0) * 0.02 - torch.relu(95.0 - thrust_width) * 0.04
            thrust_band_score = thrust_band_score - torch.relu(max_thrust - 880.0) * 0.03
            invalid = max_thrust <= min_thrust
            score = 55.0 * reward_corr + 0.05 * reward_sep + 0.05 * failure_order + thrust_score + radius_reward + thrust_band_score
            score = torch.where(invalid, torch.full_like(score, -1e9), score)

            k = min(64, score.numel())
            vals, idx = torch.topk(score, k=k)
            vals = vals.detach().cpu().numpy()
            idx = idx.detach().cpu().numpy() + start_idx
            corr_cpu = reward_corr.detach().cpu().numpy()
            sep_cpu = reward_sep.detach().cpu().numpy()
            failure_cpu = failure_order.detach().cpu().numpy()
            thrust_cpu = thrust_score.detach().cpu().numpy()
            for val, cand_idx in zip(vals, idx):
                local_idx = cand_idx - start_idx
                row = {
                    "planned_phase": phase_id,
                    "radius_min": float(phase_row["radius_min"]),
                    "radius_max": float(phase_row["radius_max"]),
                    "radius_mid": float(phase_row["radius_mid"]),
                    "max_step": float(phase_row["max_step"]),
                    "score": float(val),
                    "reward_corr": float(corr_cpu[local_idx]),
                    "reward_sep": float(sep_cpu[local_idx]),
                    "failure_order": float(failure_cpu[local_idx]),
                    "thrust_score": float(thrust_cpu[local_idx]),
                }
                for name in candidates:
                    row[name] = float(candidates[name][cand_idx])
                phase_top.append(row)

        total_candidates += args.candidates_per_round
        phase_top = sorted(phase_top, key=lambda row: row["score"], reverse=True)[:args.keep_top_per_phase]

    best = phase_top[0]
    log(
        "phase={} radius={:.0f}-{:.0f} candidates={} best_score={:.4f} "
        "theta={:.3f} angle={:.3f} gate={:.2f}/{:.2f}".format(
            phase_id,
            float(phase_row["radius_min"]),
            float(phase_row["radius_max"]),
            total_candidates,
            best["score"],
            best["theta_progress_gain"],
            best["angle_focus_gain"],
            best["thrust_gate_gain"],
            best["thrust_gate_target_norm"],
        )
    )
    return phase_top, total_candidates, time.time() - start_time


def write_summary(path, phase_name, phase_plan, best_df, total_candidates, elapsed_seconds, device, diag):
    counts = diag["done_reason"].value_counts().to_dict()
    success_rate = 100.0 * counts.get("success", 0) / max(1, len(diag))
    lines = [
        "# Curriculum Reward Grid Search",
        "",
        f"generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"phase_name_source_logs: {phase_name}",
        f"device: {device}",
        f"elapsed_seconds: {elapsed_seconds:.1f}",
        f"total_candidates: {total_candidates}",
        "",
        "## Source Log Snapshot",
        f"episodes: {len(diag)}",
        f"done_counts: {counts}",
        f"success_rate: {success_rate:.3f}%",
        "",
        "## Important Limitation",
        "Future radius bands do not have real Unity logs yet. These reward values are an offline extrapolation from the current log distribution plus radius-conditioned weighting. They must be validated phase-by-phase after each run.",
        "",
        "## Phase Radius Plan",
        phase_plan.to_string(index=False),
        "",
        "## Best Reward Per Phase",
    ]
    view_cols = [
        "planned_phase",
        "radius_min",
        "radius_max",
        "max_step",
        "score",
        "theta_progress_gain",
        "alpha_beta_gain",
        "axis_error_penalty_gain",
        "angle_focus_gain",
        "turn_toward_gain",
        "action_alignment_gain",
        "reverse_penalty_gain",
        "near_success_gain",
        "min_thrust",
        "max_thrust",
        "thrust_gate_gain",
        "thrust_gate_target_norm",
        "thrust_gate_theta_start_deg",
        "thrust_gate_theta_span_deg",
        "thrust_gate_distance_scale",
        "thrust_gate_distance_floor",
    ]
    lines.append(best_df[view_cols].to_string(index=False))
    lines.append("")
    lines.append("## Usage Rule")
    lines.append("Use only the next phase row first. Do not jump directly to later rows without fresh logs from the previous phase.")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--out-dir", default="docs/phase_planning")
    parser.add_argument("--phase-name", default="latest")
    parser.add_argument("--min-update", type=int, default=None)
    parser.add_argument("--max-radius", type=float, default=500.0)
    parser.add_argument("--seconds-per-phase", type=float, default=600.0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--candidates-per-round", type=int, default=32768)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--keep-top-per-phase", type=int, default=128)
    parser.add_argument("--seed", type=int, default=1177)
    parser.add_argument("--label", default=None)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    label = args.label or now_label()
    progress_path = out_dir / f"curriculum_reward_progress_{label}.log"

    def log(text):
        print(text, flush=True)
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(text + "\n")

    start_time = time.time()
    device = torch_device(args.device)
    rng = np.random.default_rng(args.seed)
    phase = get_phase_config()
    current_min = float(phase.get("spawn_radius_min", ACTIVE_PHASE_CONFIG.get("spawn_radius_min", 95.0)))
    current_max = float(phase.get("spawn_radius_max", ACTIVE_PHASE_CONFIG.get("spawn_radius_max", 105.0)))
    current_step = float(phase.get("max_step", ACTIVE_PHASE_CONFIG.get("max_step", 500.0)))
    phase_plan = make_phase_plan(current_min, current_max, current_step, args.max_radius)

    episodes, updates, steps, phase_name = load_logs(args.log_dir, args.phase_name, args.min_update)
    diag = build_episode_diagnostics(episodes, steps, phase)
    metrics = update_metrics(episodes, updates, steps)

    phase_plan_path = out_dir / f"curriculum_phase_plan_{label}.csv"
    diag_path = out_dir / f"curriculum_source_episode_diagnostics_{label}.csv"
    metrics_path = out_dir / f"curriculum_source_update_metrics_{label}.csv"
    phase_plan.to_csv(phase_plan_path, index=False)
    diag.to_csv(diag_path, index=False)
    metrics.to_csv(metrics_path, index=False)

    log(f"device={device} source_phase={phase_name} episodes={len(diag)} planned_phases={len(phase_plan)}")
    all_rows = []
    total_candidates = 0
    radius_span = max(1.0, args.max_radius - current_max)
    for _, phase_row in phase_plan.iterrows():
        radius_norm = float(np.clip((float(phase_row["radius_mid"]) - current_max) / radius_span, 0.0, 1.0))
        phase_rows, phase_candidates, phase_elapsed = run_phase_search(diag, steps, phase, phase_row, radius_norm, device, rng, args, log)
        total_candidates += phase_candidates
        for row in phase_rows:
            row["phase_candidates"] = phase_candidates
            row["phase_elapsed_seconds"] = phase_elapsed
            all_rows.append(row)

    all_df = pd.DataFrame(all_rows).sort_values(["planned_phase", "score"], ascending=[True, False]).reset_index(drop=True)
    best_df = all_df.groupby("planned_phase", as_index=False).head(1).reset_index(drop=True)

    candidates_path = out_dir / f"curriculum_reward_candidates_{label}.csv"
    best_path = out_dir / f"curriculum_reward_best_per_phase_{label}.csv"
    summary_path = out_dir / f"curriculum_reward_summary_{label}.txt"
    all_df.to_csv(candidates_path, index=False)
    best_df.to_csv(best_path, index=False)
    elapsed = time.time() - start_time
    write_summary(summary_path, phase_name, phase_plan, best_df, total_candidates, elapsed, str(device), diag)

    print(f"summary={summary_path}", flush=True)
    print(f"phase_plan={phase_plan_path}", flush=True)
    print(f"best_per_phase={best_path}", flush=True)
    print(f"candidates={candidates_path}", flush=True)


if __name__ == "__main__":
    main()
