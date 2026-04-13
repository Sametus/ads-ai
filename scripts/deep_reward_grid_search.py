import argparse
import math
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import torch
except Exception:  # pragma: no cover - fallback for environments without torch
    torch = None


STEP_COLS = [
    "update_id",
    "episode_id",
    "step_id",
    "reward",
    "done",
    "done_reason",
    "success",
    "distance",
    "delta_distance",
    "theta_deg",
    "alpha_deg",
    "beta_deg",
    "alignment",
    "closing_speed",
    "agl",
    "alt_error",
    "thrust",
    "vertical_cmd",
    "horizontal_cmd",
    "action_norm_0",
    "action_norm_1",
    "action_norm_2",
    "turn_rate_vertical",
    "turn_rate_horizontal",
    "reward_action_alignment",
    "reward_turn_toward",
    "reward_terminal",
    "reward_thrust_gate_penalty",
]

EPISODE_NUMERIC_COLS = [
    "update_id",
    "episode_id",
    "episode_return",
    "episode_len",
    "start_distance",
    "final_distance",
    "final_agl",
    "final_closing_speed",
    "final_theta_deg",
    "final_alpha_deg",
    "final_beta_deg",
    "final_alignment",
    "final_ang_vel_mag",
]

UPDATE_NUMERIC_COLS = [
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
]


def now_label():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_numeric(df, columns):
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def read_csvs(log_dir):
    log_dir = Path(log_dir)
    episodes = pd.read_csv(log_dir / "episode_log.csv")
    updates = pd.read_csv(log_dir / "update_log.csv")

    header = pd.read_csv(log_dir / "step_log.csv", nrows=0).columns.tolist()
    usecols = [col for col in STEP_COLS if col in header]
    steps = pd.read_csv(log_dir / "step_log.csv", usecols=usecols)

    episodes = safe_numeric(episodes, EPISODE_NUMERIC_COLS)
    updates = safe_numeric(updates, UPDATE_NUMERIC_COLS)
    steps = safe_numeric(steps, [col for col in STEP_COLS if col in steps.columns])

    if "reward_thrust_gate_penalty" not in steps.columns:
        steps["reward_thrust_gate_penalty"] = 0.0

    steps["done_reason"] = steps.get("done_reason", "").fillna("")
    episodes["done_reason"] = episodes["done_reason"].fillna("")
    return episodes, updates, steps


def rolling_success(episodes, window):
    success = (episodes["done_reason"] == "success").astype(float)
    return success.rolling(window, min_periods=max(3, window // 4)).mean() * 100.0


def summarize_windows(episodes):
    lines = []
    max_ep = int(episodes["episode_id"].max())
    for start in range(1, max_ep + 1, 40):
        end = min(max_ep, start + 39)
        window = episodes[(episodes["episode_id"] >= start) & (episodes["episode_id"] <= end)]
        counts = window["done_reason"].value_counts().to_dict()
        sr = 100.0 * counts.get("success", 0) / max(1, len(window))
        lines.append(
            {
                "episode_start": start,
                "episode_end": end,
                "n": len(window),
                "success_rate": sr,
                "mean_return": window["episode_return"].mean(),
                "mean_len": window["episode_len"].mean(),
                "counts": counts,
            }
        )
    return pd.DataFrame(lines)


def update_metrics(episodes, updates, steps):
    per_update = (
        episodes.assign(success_flag=(episodes["done_reason"] == "success").astype(float))
        .groupby("update_id")
        .agg(
            episodes=("episode_id", "count"),
            success_rate=("success_flag", lambda x: 100.0 * x.mean()),
            mean_return=("episode_return", "mean"),
            mean_len=("episode_len", "mean"),
        )
        .reset_index()
    )

    step_per_update = (
        steps.groupby("update_id")
        .agg(
            mean_theta=("theta_deg", "mean"),
            bad_theta_frac=("theta_deg", lambda x: 100.0 * (x >= 75.0).mean()),
            mean_a0=("action_norm_0", "mean"),
            high_a0_frac=("action_norm_0", lambda x: 100.0 * (x > 0.0).mean()),
            mean_agl=("agl", "mean"),
            mean_reward=("reward", "mean"),
            mean_thrust_gate=("reward_thrust_gate_penalty", "mean"),
        )
        .reset_index()
    )

    merged = per_update.merge(updates, on="update_id", how="left").merge(step_per_update, on="update_id", how="left")
    return merged


def episode_step_diagnostics(episodes, steps):
    step_copy = steps.copy()
    step_copy["success_outcome"] = step_copy["episode_id"].map(
        episodes.set_index("episode_id")["done_reason"].eq("success").to_dict()
    )
    step_copy["near_bad"] = ((step_copy["distance"] <= 18.0) & (step_copy["theta_deg"] >= 75.0)).astype(float)
    step_copy["bad_theta"] = (step_copy["theta_deg"] >= 75.0).astype(float)
    step_copy["high_a0_bad_theta"] = ((step_copy["action_norm_0"] > 0.0) & (step_copy["theta_deg"] > 45.0)).astype(float)

    idx_min_dist = step_copy.groupby("episode_id")["distance"].idxmin()
    min_rows = step_copy.loc[idx_min_dist, ["episode_id", "distance", "theta_deg", "alignment", "agl", "closing_speed"]]
    min_rows = min_rows.rename(
        columns={
            "distance": "min_distance",
            "theta_deg": "theta_at_min_distance",
            "alignment": "alignment_at_min_distance",
            "agl": "agl_at_min_distance",
            "closing_speed": "closing_at_min_distance",
        }
    )

    agg = (
        step_copy.groupby("episode_id")
        .agg(
            step_count=("step_id", "count"),
            mean_theta=("theta_deg", "mean"),
            bad_theta_frac=("bad_theta", "mean"),
            near_bad_steps=("near_bad", "sum"),
            mean_a0=("action_norm_0", "mean"),
            high_a0_frac=("action_norm_0", lambda x: (x > 0.0).mean()),
            high_a0_bad_theta_frac=("high_a0_bad_theta", "mean"),
            mean_reward=("reward", "mean"),
            sum_reward=("reward", "sum"),
            sum_thrust_gate=("reward_thrust_gate_penalty", "sum"),
            mean_thrust_gate=("reward_thrust_gate_penalty", "mean"),
        )
        .reset_index()
        .merge(min_rows, on="episode_id", how="left")
    )
    return episodes.merge(agg, on="episode_id", how="left")


def action_lag_correlations(steps):
    work = steps.sort_values(["episode_id", "step_id"]).copy()
    turn_need = np.clip(work["theta_deg"].to_numpy(dtype=np.float64) / 75.0, 0.0, 1.0)
    alpha_cmd = np.clip(work["alpha_deg"].to_numpy(dtype=np.float64) / 90.0, -1.0, 1.0)
    beta_cmd = np.clip(work["beta_deg"].to_numpy(dtype=np.float64) / 90.0, -1.0, 1.0)
    neg_alpha_cmd = -alpha_cmd
    neg_beta_cmd = -beta_cmd
    action_v = np.clip(work["action_norm_1"].to_numpy(dtype=np.float64), -1.0, 1.0)
    action_h = np.clip(work["action_norm_2"].to_numpy(dtype=np.float64), -1.0, 1.0)
    turn_v = np.clip(work["turn_rate_vertical"].to_numpy(dtype=np.float64) / 4.0, -1.0, 1.0)
    turn_h = np.clip(work["turn_rate_horizontal"].to_numpy(dtype=np.float64) / 4.0, -1.0, 1.0)

    work["score_pos"] = ((alpha_cmd * action_v + beta_cmd * action_h) * turn_need) / 2.0
    work["score_neg"] = ((neg_alpha_cmd * action_v + neg_beta_cmd * action_h) * turn_need) / 2.0
    work["turn_pos"] = ((alpha_cmd * turn_v + beta_cmd * turn_h) * turn_need) / 2.0
    work["turn_neg"] = ((neg_alpha_cmd * turn_v + neg_beta_cmd * turn_h) * turn_need) / 2.0
    work["axis_abs"] = work["alpha_deg"].abs() + work["beta_deg"].abs()

    rows = []
    for lag in [1, 2, 3, 5, 8, 10, 15, 20]:
        next_theta = work.groupby("episode_id")["theta_deg"].shift(-lag)
        next_axis = work.groupby("episode_id")["axis_abs"].shift(-lag)
        theta_improve = work["theta_deg"] - next_theta
        axis_improve = work["axis_abs"] - next_axis
        valid = theta_improve.notna() & axis_improve.notna()
        for score_col in ["score_pos", "score_neg", "turn_pos", "turn_neg"]:
            rows.append(
                {
                    "lag": lag,
                    "score": score_col,
                    "theta_improve_corr": work.loc[valid, score_col].corr(theta_improve[valid]),
                    "axis_improve_corr": work.loc[valid, score_col].corr(axis_improve[valid]),
                    "n": int(valid.sum()),
                }
            )
    return pd.DataFrame(rows)


def torch_device(requested):
    if torch is None:
        return None
    if requested == "cpu":
        return torch.device("cpu")
    if requested.startswith("cuda") and torch.cuda.is_available():
        return torch.device(requested)
    if requested == "auto" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def prepare_tensors(episodes, steps, device):
    reason_by_ep = episodes.set_index("episode_id")["done_reason"].to_dict()
    steps = steps.copy()
    steps["outcome"] = steps["episode_id"].map(reason_by_ep).fillna("")
    steps["episode_id_int"] = steps["episode_id"].astype(int)
    steps["post120"] = steps["episode_id"] > 120

    # Non-terminal rows are better for dense reward comparison.
    non_terminal = steps["reward_terminal"].fillna(0.0).abs() < 1e-9
    data = steps[non_terminal].copy()
    if len(data) == 0:
        data = steps.copy()

    arrays = {
        "a0": data["action_norm_0"].fillna(0.0).to_numpy(np.float32),
        "theta": data["theta_deg"].fillna(0.0).to_numpy(np.float32),
        "distance": data["distance"].fillna(0.0).to_numpy(np.float32),
        "success": (data["outcome"] == "success").to_numpy(np.float32),
        "near_miss": (data["outcome"] == "near_miss").to_numpy(np.float32),
        "post_fail": ((data["post120"]) & (data["outcome"] != "success")).to_numpy(np.float32),
        "fail": (data["outcome"] != "success").to_numpy(np.float32),
        "bad_high": ((data["theta_deg"] > 45.0) & (data["action_norm_0"] > 0.0)).to_numpy(np.float32),
        "good_low": ((data["theta_deg"] < 45.0) & (data["outcome"] == "success")).to_numpy(np.float32),
    }
    tensors = {name: torch.as_tensor(values, device=device) for name, values in arrays.items()}
    return data, tensors


def masked_mean(values, mask):
    denom = torch.clamp(mask.sum(dim=1), min=1.0)
    return (values * mask).sum(dim=1) / denom


def run_gpu_grid(episodes, steps, out_dir, min_seconds, requested_device, candidates_per_round, batch_size, seed):
    if torch is None:
        raise RuntimeError("Torch is not available in this Python environment.")

    device = torch_device(requested_device)
    rng = np.random.default_rng(seed)
    _, tensors = prepare_tensors(episodes, steps, device)
    a0 = tensors["a0"][None, :]
    theta = tensors["theta"][None, :]
    distance = tensors["distance"][None, :]

    masks = {
        name: tensor[None, :]
        for name, tensor in tensors.items()
        if name not in {"a0", "theta", "distance"}
    }

    top_records = []
    start = time.time()
    last_progress = start
    rounds = 0
    total_candidates = 0
    progress_path = out_dir / "reward_grid_progress.log"

    def log_progress(text):
        with open(progress_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text, flush=True)

    log_progress(f"device={device} rows={a0.shape[1]} min_seconds={min_seconds}")

    while True:
        rounds += 1
        elapsed = time.time() - start
        if elapsed >= min_seconds and rounds > 1:
            break

        gains = rng.choice(np.array([0.0, 0.05, 0.08, 0.12, 0.18, 0.24, 0.30, 0.40, 0.55, 0.75], dtype=np.float32), size=candidates_per_round)
        targets = rng.choice(np.array([-0.50, -0.40, -0.32, -0.25, -0.20, -0.15, -0.10, 0.0], dtype=np.float32), size=candidates_per_round)
        theta_starts = rng.choice(np.array([20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 55.0, 60.0], dtype=np.float32), size=candidates_per_round)
        theta_spans = rng.choice(np.array([20.0, 30.0, 40.0, 45.0, 60.0, 75.0], dtype=np.float32), size=candidates_per_round)
        dist_scales = rng.choice(np.array([40.0, 55.0, 70.0, 80.0, 100.0, 120.0], dtype=np.float32), size=candidates_per_round)
        dist_floors = rng.choice(np.array([0.15, 0.25, 0.35, 0.50], dtype=np.float32), size=candidates_per_round)

        best_round = []
        for start_idx in range(0, candidates_per_round, batch_size):
            end_idx = min(candidates_per_round, start_idx + batch_size)
            gain = torch.as_tensor(gains[start_idx:end_idx], device=device)[:, None]
            target = torch.as_tensor(targets[start_idx:end_idx], device=device)[:, None]
            theta_start = torch.as_tensor(theta_starts[start_idx:end_idx], device=device)[:, None]
            theta_span = torch.as_tensor(theta_spans[start_idx:end_idx], device=device)[:, None]
            dist_scale = torch.as_tensor(dist_scales[start_idx:end_idx], device=device)[:, None]
            dist_floor = torch.as_tensor(dist_floors[start_idx:end_idx], device=device)[:, None]

            thrust_excess = torch.clamp(a0 - target, min=0.0)
            theta_gate = torch.clamp((theta - theta_start) / torch.clamp(theta_span, min=1e-6), 0.0, 1.0)
            dist_gate = dist_floor + (1.0 - dist_floor) * torch.clamp(distance / torch.clamp(dist_scale, min=1e-6), 0.0, 1.0)
            penalty = gain * thrust_excess * theta_gate * dist_gate

            succ_pen = masked_mean(penalty, masks["success"])
            fail_pen = masked_mean(penalty, masks["fail"])
            post_fail_pen = masked_mean(penalty, masks["post_fail"])
            near_pen = masked_mean(penalty, masks["near_miss"])
            bad_high_pen = masked_mean(penalty, masks["bad_high"])
            good_low_pen = masked_mean(penalty, masks["good_low"])

            # Dense reward objective: punish collapse-like high-thrust/bad-angle rows,
            # keep successful good-angle rows almost untouched.
            score = (
                6.0 * post_fail_pen
                + 2.5 * fail_pen
                + 1.5 * near_pen
                + 3.0 * bad_high_pen
                - 12.0 * succ_pen
                - 8.0 * good_low_pen
            )
            score = score - torch.relu(succ_pen - 0.035) * 30.0
            score = score - torch.relu(good_low_pen - 0.015) * 40.0

            k = min(64, score.numel())
            vals, idx = torch.topk(score, k=k)
            vals = vals.detach().cpu().numpy()
            idx = idx.detach().cpu().numpy() + start_idx
            for val, cand_idx in zip(vals, idx):
                best_round.append(
                    {
                        "score": float(val),
                        "gain": float(gains[cand_idx]),
                        "target": float(targets[cand_idx]),
                        "theta_start": float(theta_starts[cand_idx]),
                        "theta_span": float(theta_spans[cand_idx]),
                        "dist_scale": float(dist_scales[cand_idx]),
                        "dist_floor": float(dist_floors[cand_idx]),
                    }
                )

        total_candidates += candidates_per_round
        top_records.extend(best_round)
        top_records = sorted(top_records, key=lambda r: r["score"], reverse=True)[:1000]

        if time.time() - last_progress >= 30.0:
            best = top_records[0]
            log_progress(
                "elapsed={:.1f}s rounds={} candidates={} best_score={:.5f} "
                "gain={gain:.3f} target={target:.2f} theta_start={theta_start:.1f} "
                "theta_span={theta_span:.1f} dist_scale={dist_scale:.1f} floor={dist_floor:.2f}".format(
                    time.time() - start,
                    rounds,
                    total_candidates,
                    best["score"],
                    **best,
                )
            )
            last_progress = time.time()

    top_df = pd.DataFrame(top_records).drop_duplicates(
        subset=["gain", "target", "theta_start", "theta_span", "dist_scale", "dist_floor"]
    )
    top_df = top_df.sort_values("score", ascending=False).reset_index(drop=True)
    return top_df, str(device), total_candidates, time.time() - start


def exact_episode_penalty(episodes_diag, steps, candidates):
    rows = []
    for _, cand in candidates.head(100).iterrows():
        a0 = steps["action_norm_0"].fillna(0.0).to_numpy(np.float64)
        theta = steps["theta_deg"].fillna(0.0).to_numpy(np.float64)
        distance = steps["distance"].fillna(0.0).to_numpy(np.float64)
        thrust_excess = np.maximum(0.0, a0 - cand["target"])
        theta_gate = np.clip((theta - cand["theta_start"]) / max(cand["theta_span"], 1e-6), 0.0, 1.0)
        dist_gate = cand["dist_floor"] + (1.0 - cand["dist_floor"]) * np.clip(distance / max(cand["dist_scale"], 1e-6), 0.0, 1.0)
        penalty = cand["gain"] * thrust_excess * theta_gate * dist_gate
        tmp = pd.DataFrame({"episode_id": steps["episode_id"].to_numpy(), "penalty": penalty})
        ep_pen = tmp.groupby("episode_id")["penalty"].sum().reset_index()
        merged = episodes_diag[["episode_id", "done_reason"]].merge(ep_pen, on="episode_id", how="left").fillna({"penalty": 0.0})
        success_pen = merged.loc[merged["done_reason"] == "success", "penalty"].mean()
        fail_pen = merged.loc[merged["done_reason"] != "success", "penalty"].mean()
        post_fail_pen = merged.loc[(merged["episode_id"] > 120) & (merged["done_reason"] != "success"), "penalty"].mean()
        near_pen = merged.loc[merged["done_reason"] == "near_miss", "penalty"].mean()
        exact_score = post_fail_pen + 0.5 * fail_pen + 0.4 * near_pen - 2.0 * success_pen
        row = cand.to_dict()
        row.update(
            {
                "episode_success_penalty": success_pen,
                "episode_fail_penalty": fail_pen,
                "episode_post_fail_penalty": post_fail_pen,
                "episode_near_miss_penalty": near_pen,
                "exact_score": exact_score,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values("exact_score", ascending=False).reset_index(drop=True)


def write_summary(path, episodes, updates, steps, windows, update_df, diag, lag_corr, top_exact, device, total_candidates, elapsed):
    counts = episodes["done_reason"].value_counts().to_dict()
    success_rate = 100.0 * counts.get("success", 0) / max(1, len(episodes))
    first_update = int(episodes["update_id"].min())
    last_update = int(episodes["update_id"].max())
    first_ep = int(episodes["episode_id"].min())
    last_ep = int(episodes["episode_id"].max())

    pre = episodes[episodes["episode_id"] <= 120]
    post = episodes[episodes["episode_id"] > 120]
    pre_sr = 100.0 * (pre["done_reason"] == "success").mean() if len(pre) else float("nan")
    post_sr = 100.0 * (post["done_reason"] == "success").mean() if len(post) else float("nan")

    diag_pre = diag[diag["episode_id"] <= 120]
    diag_post_fail = diag[(diag["episode_id"] > 120) & (diag["done_reason"] != "success")]
    diag_success = diag[diag["done_reason"] == "success"]

    best = top_exact.iloc[0].to_dict() if len(top_exact) else {}
    corr_cols = ["success_rate", "mean_theta", "mean_a0", "high_a0_frac", "kl", "clip_frac", "value_loss"]
    corr = update_df[corr_cols].corr(numeric_only=True) if set(corr_cols).issubset(update_df.columns) else pd.DataFrame()

    lines = []
    lines.append("# Deep Reward Grid Search Summary")
    lines.append("")
    lines.append(f"generated_at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"device: {device}")
    lines.append(f"elapsed_seconds: {elapsed:.1f}")
    lines.append(f"total_candidates: {total_candidates}")
    lines.append("")
    lines.append("## Run")
    lines.append(f"episodes: {len(episodes)} ({first_ep}-{last_ep})")
    lines.append(f"updates: {first_update}-{last_update}")
    lines.append(f"phase: {episodes['phase_name'].iloc[-1] if 'phase_name' in episodes.columns else ''}")
    lines.append(f"done_counts: {counts}")
    lines.append(f"success_rate: {success_rate:.3f}%")
    lines.append(f"pre120_success_rate: {pre_sr:.3f}%")
    lines.append(f"post120_success_rate: {post_sr:.3f}%")
    lines.append("")
    lines.append("## Key Diagnostics")
    if len(diag_success):
        lines.append(f"success_mean_a0: {diag_success['mean_a0'].mean():.4f}")
        lines.append(f"success_high_a0_frac: {100.0 * diag_success['high_a0_frac'].mean():.3f}%")
        lines.append(f"success_theta_at_min_distance: {diag_success['theta_at_min_distance'].mean():.3f}")
    if len(diag_post_fail):
        lines.append(f"post_fail_mean_a0: {diag_post_fail['mean_a0'].mean():.4f}")
        lines.append(f"post_fail_high_a0_frac: {100.0 * diag_post_fail['high_a0_frac'].mean():.3f}%")
        lines.append(f"post_fail_theta_at_min_distance: {diag_post_fail['theta_at_min_distance'].mean():.3f}")
    if len(diag_pre):
        lines.append(f"pre120_mean_a0: {diag_pre['mean_a0'].mean():.4f}")
    lines.append("")
    lines.append("## Update Correlations")
    if not corr.empty and "success_rate" in corr.index:
        for col in ["mean_theta", "mean_a0", "high_a0_frac", "kl", "clip_frac", "value_loss"]:
            lines.append(f"corr(success_rate,{col}): {corr.loc['success_rate', col]:.4f}")
    lines.append("")
    lines.append("## Action Lag Correlations")
    for _, row in lag_corr.iterrows():
        if row["lag"] in [1, 5, 10, 20]:
            lines.append(
                f"lag={int(row['lag']):02d} {row['score']}: "
                f"theta_corr={row['theta_improve_corr']:.5f}, axis_corr={row['axis_improve_corr']:.5f}, n={int(row['n'])}"
            )
    lines.append("")
    lines.append("## Best Thrust-Gate Candidate")
    for key in [
        "gain",
        "target",
        "theta_start",
        "theta_span",
        "dist_scale",
        "dist_floor",
        "episode_success_penalty",
        "episode_fail_penalty",
        "episode_post_fail_penalty",
        "episode_near_miss_penalty",
        "exact_score",
    ]:
        if key in best:
            lines.append(f"{key}: {best[key]}")
    lines.append("")
    lines.append("## Episode Windows")
    lines.append(windows.to_string(index=False))
    lines.append("")
    lines.append("## Update Tail")
    tail_cols = [
        "update_id",
        "episodes",
        "success_rate",
        "mean_return",
        "mean_theta",
        "mean_a0",
        "high_a0_frac",
        "kl",
        "clip_frac",
        "value_loss",
    ]
    available_tail_cols = [col for col in tail_cols if col in update_df.columns]
    lines.append(update_df[available_tail_cols].tail(15).to_string(index=False))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--out-dir", default="docs/reward_research")
    parser.add_argument("--min-seconds", type=float, default=1200.0)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--candidates-per-round", type=int, default=32768)
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=873)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    label = now_label()

    episodes, updates, steps = read_csvs(args.log_dir)
    windows = summarize_windows(episodes)
    update_df = update_metrics(episodes, updates, steps)
    diag = episode_step_diagnostics(episodes, steps)
    lag_corr = action_lag_correlations(steps)

    windows.to_csv(out_dir / f"episode_windows_{label}.csv", index=False)
    update_df.to_csv(out_dir / f"update_metrics_{label}.csv", index=False)
    diag.to_csv(out_dir / f"episode_diagnostics_{label}.csv", index=False)
    lag_corr.to_csv(out_dir / f"action_lag_correlations_{label}.csv", index=False)

    top_df, device, total_candidates, elapsed = run_gpu_grid(
        episodes,
        steps,
        out_dir,
        min_seconds=args.min_seconds,
        requested_device=args.device,
        candidates_per_round=args.candidates_per_round,
        batch_size=args.batch_size,
        seed=args.seed,
    )
    top_df.to_csv(out_dir / f"reward_grid_top_gpu_{label}.csv", index=False)
    top_exact = exact_episode_penalty(diag, steps, top_df)
    top_exact.to_csv(out_dir / f"reward_grid_top_exact_{label}.csv", index=False)

    summary_path = out_dir / f"summary_{label}.txt"
    write_summary(summary_path, episodes, updates, steps, windows, update_df, diag, lag_corr, top_exact, device, total_candidates, elapsed)
    print(f"summary_path={summary_path}", flush=True)


if __name__ == "__main__":
    main()
