import argparse
import csv
import itertools
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from env import REWARD_CONFIG, get_phase_config


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
STEP_LOG = LOG_DIR / "step_log.csv"
EPISODE_LOG = LOG_DIR / "episode_log.csv"


def unique_headers(header):
    counts = {}
    unique = []

    for name in header:
        index = counts.get(name, 0)
        counts[name] = index + 1
        if index == 0:
            unique.append(name)
        else:
            unique.append(f"{name}__dup{index}")

    return unique


def read_csv_rows(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        raw_header = next(reader)
        header = unique_headers(raw_header)
        rows = [dict(zip(header, row)) for row in reader]
    return raw_header, rows


def safe_float(row, key, default=0.0):
    value = row.get(key, "")
    if value in ("", None):
        return float(default)
    return float(value)


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
        ranks[order[i:j + 1]] = rank
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


def load_phase_dataset(phase_id):
    _, step_rows = read_csv_rows(STEP_LOG)
    _, episode_rows = read_csv_rows(EPISODE_LOG)

    step_rows = [row for row in step_rows if row.get("phase_id") == str(phase_id)]
    episode_rows = [row for row in episode_rows if row.get("phase_id") == str(phase_id)]

    if not step_rows or not episode_rows:
        raise FileNotFoundError(f"Phase {phase_id} icin yeterli log bulunamadi.")

    steps_by_episode = defaultdict(list)
    for row in step_rows:
        steps_by_episode[row["episode_id"]].append(row)

    episode_rows = [row for row in episode_rows if row["episode_id"] in steps_by_episode]
    episode_rows.sort(key=lambda row: int(row["episode_id"]))

    episode_ids = [row["episode_id"] for row in episode_rows]
    episode_index_map = {episode_id: index for index, episode_id in enumerate(episode_ids)}

    distance = []
    delta_distance = []
    look_angle_rad = []
    alignment = []
    closing_speed = []
    agl = []
    alt_error = []
    ang_vel_mag = []
    grounded_flag = []
    terminal_reason = []
    episode_indices = []

    episode_features = []

    for row in episode_rows:
        episode_id = row["episode_id"]
        steps = steps_by_episode[episode_id]

        dists = np.array([safe_float(s, "distance") for s in steps], dtype=np.float64)
        closes = np.array([safe_float(s, "closing_speed") for s in steps], dtype=np.float64)
        looks = np.array([safe_float(s, "look_angle_deg") for s in steps], dtype=np.float64)
        agls = np.array([safe_float(s, "agl") for s in steps], dtype=np.float64)
        aligns = np.array([safe_float(s, "alignment") for s in steps], dtype=np.float64)

        start_distance = safe_float(row, "start_distance")
        final_distance = safe_float(row, "final_distance")
        min_distance = float(np.min(dists))

        progress_ratio = (start_distance - final_distance) / max(start_distance, 1e-6)
        best_progress_ratio = (start_distance - min_distance) / max(start_distance, 1e-6)
        positive_closing_fraction = float(np.mean(closes > 0.0))
        aligned_fraction_45 = float(np.mean(looks < 45.0))
        safety_score = 1.0 - float(np.mean(agls < 5.0))
        mean_alignment = float(np.mean(aligns))

        final_progress_score = 0.5 * (np.clip(progress_ratio, -1.0, 1.0) + 1.0)
        best_progress_score = float(np.clip(best_progress_ratio, 0.0, 1.0))
        closing_score = positive_closing_fraction
        alignment_score = aligned_fraction_45
        stability_score = float(np.clip((mean_alignment + 1.0) / 2.0, 0.0, 1.0))

        objective_score = (
            0.30 * best_progress_score
            + 0.25 * final_progress_score
            + 0.20 * closing_score
            + 0.15 * alignment_score
            + 0.10 * safety_score
            + 0.05 * stability_score
        )

        episode_features.append({
            "episode_id": int(episode_id),
            "done_reason": row["done_reason"],
            "start_distance": start_distance,
            "final_distance": final_distance,
            "min_distance": min_distance,
            "progress_ratio": progress_ratio,
            "best_progress_ratio": best_progress_ratio,
            "positive_closing_fraction": positive_closing_fraction,
            "aligned_fraction_45": aligned_fraction_45,
            "safety_score": safety_score,
            "mean_alignment": mean_alignment,
            "objective_score": objective_score,
        })

        for step in steps:
            distance.append(safe_float(step, "distance"))
            delta_distance.append(safe_float(step, "delta_distance"))
            look_angle_rad.append(safe_float(step, "look_angle_rad"))
            alignment.append(safe_float(step, "alignment"))
            closing_speed.append(safe_float(step, "closing_speed"))
            agl.append(safe_float(step, "agl"))
            alt_error.append(safe_float(step, "alt_error"))
            ang_vel_mag.append(safe_float(step, "ang_vel_mag"))
            grounded_flag.append(safe_float(step, "grounded_flag"))
            terminal_reason.append(step.get("done_reason", ""))
            episode_indices.append(episode_index_map[episode_id])

    dataset = {
        "episode_ids": np.array([int(e["episode_id"]) for e in episode_features], dtype=np.int32),
        "episode_features": episode_features,
        "objective_scores": np.array([e["objective_score"] for e in episode_features], dtype=np.float64),
        "progress_ratios": np.array([e["progress_ratio"] for e in episode_features], dtype=np.float64),
        "best_progress_ratios": np.array([e["best_progress_ratio"] for e in episode_features], dtype=np.float64),
        "positive_closing_fractions": np.array([e["positive_closing_fraction"] for e in episode_features], dtype=np.float64),
        "aligned_fraction_45": np.array([e["aligned_fraction_45"] for e in episode_features], dtype=np.float64),
        "distance": np.array(distance, dtype=np.float64),
        "delta_distance": np.array(delta_distance, dtype=np.float64),
        "look_angle_rad": np.array(look_angle_rad, dtype=np.float64),
        "alignment": np.array(alignment, dtype=np.float64),
        "closing_speed": np.array(closing_speed, dtype=np.float64),
        "agl": np.array(agl, dtype=np.float64),
        "alt_error": np.array(alt_error, dtype=np.float64),
        "ang_vel_mag": np.array(ang_vel_mag, dtype=np.float64),
        "grounded_flag": np.array(grounded_flag, dtype=np.float64),
        "terminal_reason": np.array(terminal_reason, dtype=object),
        "episode_indices": np.array(episode_indices, dtype=np.int32),
        "episode_count": len(episode_features),
        "step_count": len(distance),
    }

    return dataset


def build_reward_bases(dataset, phase):
    alignment_positive = np.maximum(dataset["alignment"], 0.0)
    positive_closing = np.clip(
        dataset["closing_speed"] / phase["closing_speed_clip"],
        0.0,
        1.0,
    )

    bases = {
        "distance": np.clip(
            dataset["delta_distance"],
            -phase["distance_delta_clip"],
            phase["distance_delta_clip"],
        ) * (0.20 + 0.80 * alignment_positive),
        "alignment": dataset["alignment"] * (0.30 + 0.70 * positive_closing),
        "closing": positive_closing * (0.20 + 0.80 * alignment_positive),
        "angular_penalty": np.minimum(dataset["ang_vel_mag"], phase["ang_vel_clip"]),
        "altitude": np.clip(1.0 - np.abs(dataset["alt_error"]) / 50.0, 0.0, 1.0),
        "soft_floor": np.maximum(0.0, phase["soft_floor"] - dataset["agl"]),
        "success_mask": (dataset["terminal_reason"] == "success").astype(np.float64),
        "collision_mask": (dataset["terminal_reason"] == "collision").astype(np.float64),
        "low_agl_mask": (dataset["terminal_reason"] == "low_agl").astype(np.float64),
        "high_altitude_mask": (dataset["terminal_reason"] == "high_altitude").astype(np.float64),
        "timeout_mask": (dataset["terminal_reason"] == "timeout").astype(np.float64),
    }
    return bases


def iter_param_grid(current):
    grid = {
        "step_penalty": [-0.12, -0.08],
        "distance_gain": [0.12, 0.20, 0.28],
        "alignment_gain": [0.16, 0.32, 0.48],
        "closing_gain": [0.10, 0.20, 0.30],
        "ang_vel_penalty": [0.02, 0.04, 0.06],
        "height_align_gain": [0.012, 0.03, 0.06],
        "soft_floor_gain": [0.12, 0.24, 0.36],
        "low_altitude_penalty": [-150.0, -110.0],
        "timeout_penalty": [-80.0, -40.0],
    }

    keys = list(grid.keys())
    values = [grid[key] for key in keys]

    current_tuple = tuple(current[key] for key in keys)
    yielded_current = False

    for combo in itertools.product(*values):
        if combo == current_tuple:
            yielded_current = True
        yield dict(zip(keys, combo))

    if not yielded_current:
        yield {key: current[key] for key in keys}


def evaluate_combo(params, phase, dataset, bases):
    rewards = (
        params["step_penalty"]
        + params["distance_gain"] * bases["distance"]
        + params["alignment_gain"] * bases["alignment"]
        + params["closing_gain"] * bases["closing"]
        - params["ang_vel_penalty"] * bases["angular_penalty"]
        + params["height_align_gain"] * bases["altitude"]
        - params["soft_floor_gain"] * bases["soft_floor"]
        + phase["success_reward"] * bases["success_mask"]
        + phase["collision_penalty"] * bases["collision_mask"]
        + params["low_altitude_penalty"] * bases["low_agl_mask"]
        + phase["high_altitude_penalty"] * bases["high_altitude_mask"]
        + params["timeout_penalty"] * bases["timeout_mask"]
    )

    episode_returns = np.bincount(
        dataset["episode_indices"],
        weights=rewards,
        minlength=dataset["episode_count"],
    )

    objective_scores = dataset["objective_scores"]

    spearman_objective = spearman_corr(episode_returns, objective_scores)
    spearman_best_progress = spearman_corr(episode_returns, dataset["best_progress_ratios"])
    spearman_progress = spearman_corr(episode_returns, dataset["progress_ratios"])
    pair_acc = pairwise_accuracy(episode_returns, objective_scores)
    pair_score = 2.0 * pair_acc - 1.0

    top_n = max(3, dataset["episode_count"] // 4)
    order = np.argsort(objective_scores)
    bottom_indices = order[:top_n]
    top_indices = order[-top_n:]

    returns_std = float(np.std(episode_returns))
    effect_size = (
        float(np.mean(episode_returns[top_indices]) - np.mean(episode_returns[bottom_indices]))
        / max(returns_std, 1e-6)
    )
    effect_score = math.tanh(effect_size / 3.0)

    fitness = (
        0.55 * spearman_objective
        + 0.20 * pair_score
        + 0.10 * effect_score
        + 0.10 * spearman_best_progress
        + 0.05 * spearman_progress
    )

    return {
        **params,
        "fitness": fitness,
        "spearman_objective": spearman_objective,
        "spearman_best_progress": spearman_best_progress,
        "spearman_progress": spearman_progress,
        "pairwise_accuracy": pair_acc,
        "effect_size": effect_size,
        "top_quartile_return": float(np.mean(episode_returns[top_indices])),
        "bottom_quartile_return": float(np.mean(episode_returns[bottom_indices])),
        "mean_episode_return": float(np.mean(episode_returns)),
    }


def write_results(path, results):
    if not results:
        return

    fieldnames = list(results[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def summarize_parameter_preferences(results, top_k=50):
    summary = {}
    top_results = results[: min(top_k, len(results))]

    for key in [
        "step_penalty",
        "distance_gain",
        "alignment_gain",
        "closing_gain",
        "ang_vel_penalty",
        "height_align_gain",
        "soft_floor_gain",
        "low_altitude_penalty",
        "timeout_penalty",
    ]:
        value_to_scores = defaultdict(list)
        for row in top_results:
            value_to_scores[row[key]].append(row["fitness"])

        ranked_values = sorted(
            (
                {
                    "value": value,
                    "mean_top_fitness": float(np.mean(scores)),
                    "count_in_top": len(scores),
                }
                for value, scores in value_to_scores.items()
            ),
            key=lambda item: item["mean_top_fitness"],
            reverse=True,
        )
        summary[key] = ranked_values

    return summary


def print_dataset_summary(dataset):
    features = dataset["episode_features"]
    print(f"[DATA] phase episodes={dataset['episode_count']} | steps={dataset['step_count']}")

    done_counts = defaultdict(int)
    for item in features:
        done_counts[item["done_reason"]] += 1
    print(f"[DATA] done_reasons={dict(done_counts)}")

    print(
        "[DATA] objective mean="
        f"{np.mean(dataset['objective_scores']):.4f} | "
        f"progress mean={np.mean(dataset['progress_ratios']):.4f} | "
        f"best_progress mean={np.mean(dataset['best_progress_ratios']):.4f} | "
        f"positive_closing mean={np.mean(dataset['positive_closing_fractions']):.4f} | "
        f"aligned45 mean={np.mean(dataset['aligned_fraction_45']):.4f}"
    )


def print_combo_block(title, rows):
    print(f"\n[{title}]")
    for index, row in enumerate(rows, start=1):
        print(
            f"{index:>2}. fit={row['fitness']:.4f} | "
            f"rho_obj={row['spearman_objective']:.4f} | "
            f"pair={row['pairwise_accuracy']:.4f} | "
            f"step={row['step_penalty']:.3f} | "
            f"dist={row['distance_gain']:.3f} | "
            f"align={row['alignment_gain']:.3f} | "
            f"close={row['closing_gain']:.3f} | "
            f"ang={row['ang_vel_penalty']:.3f} | "
            f"alt={row['height_align_gain']:.3f} | "
            f"floor={row['soft_floor_gain']:.3f} | "
            f"low={row['low_altitude_penalty']:.1f} | "
            f"timeout={row['timeout_penalty']:.1f}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Offline reward grid search from V7 step/episode CSV logs.")
    parser.add_argument("--phase", type=int, default=1, help="Curriculum phase id to evaluate.")
    parser.add_argument("--top-k", type=int, default=10, help="How many best/worst combinations to print.")
    parser.add_argument(
        "--out",
        type=Path,
        default=LOG_DIR / "reward_grid_search_phase1.csv",
        help="CSV output path for ranked combinations.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    phase = get_phase_config(args.phase)
    dataset = load_phase_dataset(args.phase)
    bases = build_reward_bases(dataset, phase)

    print_dataset_summary(dataset)
    print(
        "[GRID] searching over shaping/terminal weights only; "
        "termination thresholds, clips, and phase geometry are held fixed."
    )

    current = {
        "step_penalty": phase["step_penalty"],
        "distance_gain": phase["distance_gain"],
        "alignment_gain": phase["alignment_gain"],
        "closing_gain": phase["closing_gain"],
        "ang_vel_penalty": phase["ang_vel_penalty"],
        "height_align_gain": phase["height_align_gain"],
        "soft_floor_gain": phase["soft_floor_gain"],
        "low_altitude_penalty": phase["low_altitude_penalty"],
        "timeout_penalty": phase["timeout_penalty"],
    }

    results = []
    for params in iter_param_grid(current):
        row = evaluate_combo(params, phase, dataset, bases)
        row["is_current"] = int(all(abs(row[k] - current[k]) <= 1e-12 for k in current))
        results.append(row)

    results.sort(key=lambda row: row["fitness"], reverse=True)

    for rank, row in enumerate(results, start=1):
        row["rank"] = rank

    current_row = next(row for row in results if row["is_current"] == 1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_results(args.out, results)

    print(
        f"[CURRENT] rank={current_row['rank']}/{len(results)} | "
        f"fitness={current_row['fitness']:.4f} | "
        f"rho_obj={current_row['spearman_objective']:.4f} | "
        f"pair={current_row['pairwise_accuracy']:.4f}"
    )

    print_combo_block("TOP COMBOS", results[: args.top_k])
    print_combo_block("BOTTOM COMBOS", list(reversed(results[-args.top_k:])))

    preferences = summarize_parameter_preferences(results, top_k=max(20, args.top_k * 3))
    print("\n[TOP PARAMETER PREFERENCES]")
    for key, rows in preferences.items():
        best = rows[0]
        print(
            f"{key}: preferred={best['value']} | "
            f"mean_top_fitness={best['mean_top_fitness']:.4f} | "
            f"count_in_top={best['count_in_top']}"
        )

    print(f"\n[OUTPUT] ranked grid written to: {args.out}")


if __name__ == "__main__":
    main()
