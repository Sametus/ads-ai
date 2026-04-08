import argparse
import csv
import itertools
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from env import get_phase_config


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
STEP_LOG = LOG_DIR / "step_log.csv"
EPISODE_LOG = LOG_DIR / "episode_log.csv"
DEFAULT_OUT = LOG_DIR / "reward_search_v8_results.csv"


@dataclass
class EpisodeData:
    episode_id: int
    done_reason: str
    actual_return: float
    objective_score: float
    bases: np.ndarray


def safe_float(row, key, default=math.nan):
    value = row.get(key, "")
    if value in ("", None):
        return default
    try:
        return float(value)
    except Exception:
        return default


def rankdata(values):
    values = np.asarray(values, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)

    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = 0.5 * (i + j) + 1.0
        ranks[order[i : j + 1]] = rank
        i = j + 1

    return ranks


def spearman_corr(x, y):
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    if len(x) < 2:
        return 0.0

    xr = rankdata(x)
    yr = rankdata(y)
    x_centered = xr - xr.mean()
    y_centered = yr - yr.mean()
    denom = math.sqrt(np.sum(x_centered ** 2) * np.sum(y_centered ** 2))
    if denom <= 1e-12:
        return 0.0
    return float(np.sum(x_centered * y_centered) / denom)


def pairwise_accuracy(returns, objective):
    returns = np.asarray(returns, dtype=np.float64)
    objective = np.asarray(objective, dtype=np.float64)
    correct = 0
    total = 0

    for i in range(len(returns)):
        for j in range(i + 1, len(returns)):
            objective_diff = objective[i] - objective[j]
            if abs(objective_diff) <= 1e-9:
                continue
            return_diff = returns[i] - returns[j]
            if abs(return_diff) <= 1e-9:
                continue
            total += 1
            if objective_diff * return_diff > 0:
                correct += 1

    if total == 0:
        return 0.5
    return correct / total


def read_logs():
    with EPISODE_LOG.open("r", encoding="utf-8", newline="") as f:
        episode_rows = [row for row in csv.DictReader(f) if row.get("phase_name") == "manual_active_config"]
    with STEP_LOG.open("r", encoding="utf-8", newline="") as f:
        step_rows = [row for row in csv.DictReader(f) if row.get("phase_name") == "manual_active_config"]

    steps_by_episode = {}
    for row in step_rows:
        steps_by_episode.setdefault(int(row["episode_id"]), []).append(row)

    episodes = []
    for row in episode_rows:
        episode_id = int(row["episode_id"])
        if episode_id not in steps_by_episode:
            continue
        episodes.append((row, steps_by_episode[episode_id]))

    return episodes


def build_objective(row, steps):
    start_distance = safe_float(row, "start_distance", 0.0)
    final_distance = safe_float(row, "final_distance", start_distance)
    done_reason = row.get("done_reason", "")

    dist = np.array([safe_float(s, "distance", 0.0) for s in steps], dtype=np.float64)
    theta = np.array([safe_float(s, "theta_deg", 180.0) for s in steps], dtype=np.float64)
    closing = np.array([safe_float(s, "closing_speed", 0.0) for s in steps], dtype=np.float64)
    agl = np.array([safe_float(s, "agl", 0.0) for s in steps], dtype=np.float64)

    min_distance = float(np.min(dist))
    min_theta = float(np.min(theta))
    good_geom_fraction = float(np.mean((theta < 25.0) & (closing > 0.0)))
    positive_closing_fraction = float(np.mean(closing > 0.0))
    altitude_safety = 1.0 - float(np.mean((agl < 5.0) | (agl > 140.0)))

    distance_scale = max(start_distance, 1e-6)
    best_distance_score = float(np.clip((start_distance - min_distance) / distance_scale, 0.0, 1.0))
    final_distance_score = float(np.clip((start_distance - final_distance) / distance_scale, -1.0, 1.0))
    final_distance_score = 0.5 * (final_distance_score + 1.0)
    best_theta_score = float(np.clip(1.0 - (min_theta / 90.0), 0.0, 1.0))

    objective = (
        0.34 * best_distance_score
        + 0.20 * final_distance_score
        + 0.20 * best_theta_score
        + 0.16 * positive_closing_fraction
        + 0.10 * good_geom_fraction
        + 0.05 * altitude_safety
    )

    if done_reason == "success":
        objective += 1.0
    elif done_reason == "wrong_way":
        objective -= 0.12
    elif done_reason == "high_altitude":
        objective -= 0.06
    elif done_reason == "low_agl":
        objective -= 0.08
    elif done_reason == "timeout":
        objective -= 0.05

    return float(objective)


def build_episode_bases(episodes, phase):
    current = {
        "step_penalty": phase["step_penalty"],
        "distance_gain": phase["distance_gain"],
        "alignment_gain": phase["alignment_gain"],
        "closing_gain": phase["closing_gain"],
        "theta_progress_gain": phase["theta_progress_gain"],
        "alpha_beta_gain": phase["alpha_beta_gain"],
        "axis_error_penalty_gain": phase["axis_error_penalty_gain"],
        "direction_bonus_gain": phase["direction_bonus_gain"],
        "near_success_gain": phase["near_success_gain"],
        "reverse_penalty_gain": phase["reverse_penalty_gain"],
        "ang_vel_penalty": phase["ang_vel_penalty"],
        "height_align_gain": phase["height_align_gain"],
        "soft_floor_gain": phase["soft_floor_gain"],
        "soft_ceiling_gain": phase["soft_ceiling_gain"],
    }

    episode_data = []
    for row, steps in episodes:
        step_count = float(len(steps))
        sums = {
            "distance": 0.0,
            "alignment": 0.0,
            "closing": 0.0,
            "theta_progress": 0.0,
            "alpha_beta": 0.0,
            "axis_error": 0.0,
            "direction": 0.0,
            "near_success": 0.0,
            "reverse": 0.0,
            "ang_only": 0.0,
            "roll": 0.0,
            "altitude": 0.0,
            "soft_floor": 0.0,
            "soft_ceiling": 0.0,
        }

        for step in steps:
            sums["distance"] += safe_float(step, "reward_distance", 0.0) / current["distance_gain"]
            sums["alignment"] += safe_float(step, "reward_alignment", 0.0) / current["alignment_gain"]
            sums["closing"] += safe_float(step, "reward_closing", 0.0) / current["closing_gain"]
            sums["theta_progress"] += safe_float(step, "reward_theta_progress", 0.0) / current["theta_progress_gain"]
            sums["alpha_beta"] += safe_float(step, "reward_alpha_beta", 0.0) / current["alpha_beta_gain"]
            sums["axis_error"] += safe_float(step, "reward_axis_error_penalty", 0.0) / current["axis_error_penalty_gain"]
            sums["direction"] += safe_float(step, "reward_direction_bonus", 0.0) / current["direction_bonus_gain"]
            sums["near_success"] += safe_float(step, "reward_near_success_bonus", 0.0) / current["near_success_gain"]
            sums["reverse"] += safe_float(step, "reward_reverse_penalty", 0.0) / current["reverse_penalty_gain"]
            reward_ang = safe_float(step, "reward_angular_penalty", 0.0)
            reward_roll = safe_float(step, "reward_roll_penalty", 0.0)
            sums["roll"] += reward_roll
            sums["ang_only"] += max(reward_ang - reward_roll, 0.0) / current["ang_vel_penalty"]
            sums["altitude"] += safe_float(step, "reward_altitude", 0.0) / current["height_align_gain"]
            sums["soft_floor"] += safe_float(step, "reward_soft_floor_penalty", 0.0) / current["soft_floor_gain"]
            sums["soft_ceiling"] += safe_float(step, "reward_soft_ceiling_penalty", 0.0) / current["soft_ceiling_gain"]

        done_reason = row.get("done_reason", "")
        reason_one_hot = {
            "success": 1.0 if done_reason == "success" else 0.0,
            "collision": 1.0 if done_reason == "collision" else 0.0,
            "low_agl": 1.0 if done_reason == "low_agl" else 0.0,
            "high_altitude": 1.0 if done_reason == "high_altitude" else 0.0,
            "wrong_way": 1.0 if done_reason == "wrong_way" else 0.0,
            "timeout": 1.0 if done_reason == "timeout" else 0.0,
        }

        bases = np.array([
            step_count,
            sums["distance"],
            sums["alignment"],
            sums["closing"],
            sums["theta_progress"],
            sums["alpha_beta"],
            sums["axis_error"],
            sums["direction"],
            sums["near_success"],
            sums["reverse"],
            sums["ang_only"],
            sums["roll"],
            sums["altitude"],
            sums["soft_floor"],
            sums["soft_ceiling"],
            reason_one_hot["success"],
            reason_one_hot["collision"],
            reason_one_hot["low_agl"],
            reason_one_hot["high_altitude"],
            reason_one_hot["wrong_way"],
            reason_one_hot["timeout"],
        ], dtype=np.float64)

        episode_data.append(EpisodeData(
            episode_id=int(row["episode_id"]),
            done_reason=done_reason,
            actual_return=safe_float(row, "episode_return", 0.0),
            objective_score=build_objective(row, steps),
            bases=bases,
        ))

    return episode_data


def replay_returns(episode_matrix, params):
    weights = np.array([
        params["step_penalty"],
        params["distance_gain"],
        params["alignment_gain"],
        params["closing_gain"],
        params["theta_progress_gain"],
        params["alpha_beta_gain"],
        -params["axis_error_penalty_gain"],
        params["direction_bonus_gain"],
        params["near_success_gain"],
        -params["reverse_penalty_gain"],
        -params["ang_vel_penalty"],
        -1.0,  # roll penalty stays fixed from log magnitude
        params["height_align_gain"],
        -params["soft_floor_gain"],
        -params["soft_ceiling_gain"],
        params["success_reward"],
        params["collision_penalty"],
        params["low_altitude_penalty"],
        params["high_altitude_penalty"],
        params["wrong_way_penalty"],
        params["timeout_penalty"],
    ], dtype=np.float64)
    return episode_matrix @ weights


def evaluate_returns(returns, objective_scores, done_reasons):
    returns = np.asarray(returns, dtype=np.float64)
    objective_scores = np.asarray(objective_scores, dtype=np.float64)
    done_reasons = np.asarray(done_reasons, dtype=object)

    corr = spearman_corr(returns, objective_scores)
    pair = pairwise_accuracy(returns, objective_scores)

    top_k = max(1, int(math.ceil(len(returns) * 0.15)))
    top_indices = np.argsort(returns)[-top_k:]
    success_top = float(np.mean(done_reasons[top_indices] == "success"))

    success_returns = returns[done_reasons == "success"]
    fail_returns = returns[done_reasons != "success"]
    if len(success_returns) and len(fail_returns):
        success_margin = float(np.mean(success_returns) - np.percentile(fail_returns, 95))
    else:
        success_margin = 0.0

    fitness = (
        0.45 * corr
        + 0.35 * pair
        + 0.10 * success_top
        + 0.10 * np.tanh(success_margin / 100.0)
    )

    return {
        "fitness": float(fitness),
        "spearman_corr": float(corr),
        "pairwise_accuracy": float(pair),
        "success_top15": float(success_top),
        "success_margin95": float(success_margin),
    }


def generate_stage1_grid():
    return {
        "step_penalty": [-0.12, -0.10, -0.08],
        "distance_gain": [0.24, 0.30, 0.36],
        "alignment_gain": [0.45, 0.60, 0.80],
        "closing_gain": [0.14, 0.22, 0.30],
        "theta_progress_gain": [0.22, 0.32, 0.42],
        "alpha_beta_gain": [0.12, 0.20, 0.28],
        "axis_error_penalty_gain": [0.10, 0.16, 0.24],
        "direction_bonus_gain": [0.14, 0.22, 0.30],
        "near_success_gain": [0.24, 0.38, 0.52],
        "reverse_penalty_gain": [0.24, 0.36, 0.48],
        "soft_ceiling_gain": [0.016, 0.028, 0.040],
    }


def generate_stage2_grid():
    return {
        "high_altitude_penalty": [-100.0, -120.0, -140.0],
        "wrong_way_penalty": [-105.0, -125.0, -145.0],
        "timeout_penalty": [-70.0, -90.0, -110.0],
    }


def iterate_chunks(iterable, chunk_size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def run_search(episode_data, top_k=25):
    phase = get_phase_config()
    episode_matrix = np.vstack([e.bases for e in episode_data])
    objective_scores = np.array([e.objective_score for e in episode_data], dtype=np.float64)
    done_reasons = np.array([e.done_reason for e in episode_data], dtype=object)
    actual_returns = np.array([e.actual_return for e in episode_data], dtype=np.float64)

    baseline_returns = replay_returns(episode_matrix, phase)
    baseline_mae = float(np.mean(np.abs(baseline_returns - actual_returns)))
    baseline_eval = evaluate_returns(baseline_returns, objective_scores, done_reasons)

    stage1 = generate_stage1_grid()
    stage1_keys = list(stage1.keys())
    fixed_terminal = {
        "success_reward": phase["success_reward"],
        "collision_penalty": phase["collision_penalty"],
        "low_altitude_penalty": phase["low_altitude_penalty"],
        "high_altitude_penalty": phase["high_altitude_penalty"],
        "wrong_way_penalty": phase["wrong_way_penalty"],
        "timeout_penalty": phase["timeout_penalty"],
        "height_align_gain": phase["height_align_gain"],
        "soft_floor_gain": phase["soft_floor_gain"],
        "ang_vel_penalty": phase["ang_vel_penalty"],
    }

    stage1_results = []
    combos = itertools.product(*(stage1[key] for key in stage1_keys))
    for chunk in iterate_chunks(combos, 2048):
        for values in chunk:
            params = dict(fixed_terminal)
            params.update(zip(stage1_keys, values))
            returns = replay_returns(episode_matrix, params)
            metrics = evaluate_returns(returns, objective_scores, done_reasons)
            stage1_results.append((metrics["fitness"], params, metrics))

    stage1_results.sort(key=lambda item: item[0], reverse=True)
    stage1_results = stage1_results[: max(top_k, 50)]

    stage2 = generate_stage2_grid()
    stage2_keys = list(stage2.keys())
    final_results = []
    for _, base_params, _ in stage1_results:
        for values in itertools.product(*(stage2[key] for key in stage2_keys)):
            params = dict(base_params)
            params.update(zip(stage2_keys, values))
            returns = replay_returns(episode_matrix, params)
            metrics = evaluate_returns(returns, objective_scores, done_reasons)
            final_results.append({
                **params,
                **metrics,
                "mean_return": float(np.mean(returns)),
                "mean_success_return": float(np.mean(returns[done_reasons == "success"])) if np.any(done_reasons == "success") else 0.0,
                "mean_fail_return": float(np.mean(returns[done_reasons != "success"])) if np.any(done_reasons != "success") else 0.0,
            })

    final_results.sort(key=lambda row: row["fitness"], reverse=True)
    return final_results, baseline_mae, baseline_eval


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=25)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    episodes = read_logs()
    episode_data = build_episode_bases(episodes, get_phase_config())
    results, baseline_mae, baseline_eval = run_search(episode_data, top_k=args.top_k)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    if results:
        fieldnames = list(results[0].keys())
        with args.out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    print(f"episodes={len(episode_data)}")
    print(f"baseline_replay_mae={baseline_mae:.6f}")
    print(
        "baseline_metrics",
        {
            "fitness": round(baseline_eval["fitness"], 6),
            "spearman_corr": round(baseline_eval["spearman_corr"], 6),
            "pairwise_accuracy": round(baseline_eval["pairwise_accuracy"], 6),
            "success_top15": round(baseline_eval["success_top15"], 6),
            "success_margin95": round(baseline_eval["success_margin95"], 6),
        },
    )
    if results:
        best = results[0]
        print("best_result", {k: round(v, 6) if isinstance(v, float) else v for k, v in best.items()})
        print(f"wrote={args.out}")


if __name__ == "__main__":
    main()
