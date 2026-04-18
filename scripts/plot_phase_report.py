from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


OUTCOME_COLORS = {
    "success": "#1f9d55",
    "near_miss": "#f59e0b",
    "low_agl": "#ef4444",
    "wrong_way": "#7c3aed",
    "high_altitude": "#be185d",
    "timeout": "#64748b",
    "escaped": "#0891b2",
    "other": "#334155",
}

OUTCOME_ORDER = [
    "success",
    "near_miss",
    "low_agl",
    "wrong_way",
    "high_altitude",
    "timeout",
    "escaped",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip().lower())
    return slug.strip("_") or "phase_report"


def read_completed_episodes(
    logs_dir: Path,
    start_update: int | None,
    end_update: int | None,
) -> tuple[pd.DataFrame, int]:
    episode_path = logs_dir / "episode_log.csv"
    update_path = logs_dir / "update_log.csv"

    if not episode_path.exists():
        raise FileNotFoundError(f"Missing episode log: {episode_path}")
    if not update_path.exists():
        raise FileNotFoundError(f"Missing update log: {update_path}")

    updates = pd.read_csv(update_path)
    completed_updates = pd.to_numeric(updates["update_id"], errors="coerce").dropna()
    if completed_updates.empty:
        raise ValueError("update_log.csv has no completed update_id rows.")

    last_completed_update = int(completed_updates.max()) if end_update is None else end_update

    episodes = pd.read_csv(episode_path)
    episodes["update_id"] = pd.to_numeric(episodes["update_id"], errors="coerce")
    episodes = episodes[episodes["update_id"].notna()].copy()
    episodes["update_id"] = episodes["update_id"].astype(int)
    episodes = episodes[episodes["update_id"] <= last_completed_update]
    if start_update is not None:
        episodes = episodes[episodes["update_id"] >= start_update]

    if episodes.empty:
        raise ValueError("No completed episode rows after update filtering.")

    episodes = episodes.reset_index(drop=True)
    episodes["episode_index"] = np.arange(1, len(episodes) + 1)
    episodes["episode_segment"] = (episodes["episode_id"] < episodes["episode_id"].shift(1)).fillna(False).cumsum().astype(int)
    episodes["is_success"] = (episodes["done_reason"] == "success").astype(float)

    return episodes, last_completed_update


def add_episode_segments_to_step_chunk(
    chunk: pd.DataFrame,
    current_segment: int,
    previous_episode_id: int | None,
) -> tuple[pd.DataFrame, int, int | None]:
    episode_ids = chunk["episode_id"].astype(int)
    previous_ids = episode_ids.shift(1)
    reset_flags = episode_ids < previous_ids
    if previous_episode_id is not None and not episode_ids.empty:
        reset_flags.iloc[0] = int(episode_ids.iloc[0]) < int(previous_episode_id)

    chunk = chunk.copy()
    chunk["episode_segment"] = current_segment + reset_flags.fillna(False).cumsum().astype(int)

    next_segment = int(chunk["episode_segment"].iloc[-1]) if not chunk.empty else current_segment
    next_previous_episode_id = int(episode_ids.iloc[-1]) if not episode_ids.empty else previous_episode_id
    return chunk, next_segment, next_previous_episode_id


def load_reset_points(logs_dir: Path, episodes: pd.DataFrame, last_completed_update: int) -> pd.DataFrame | None:
    step_path = logs_dir / "step_log.csv"
    if not step_path.exists():
        return None

    usecols = [
        "update_id",
        "episode_id",
        "step_id",
        "rel_pos_world_x",
        "rel_pos_world_z",
        "target_point_pos_world_x",
        "target_point_pos_world_z",
        "rocket_point_pos_world_x",
        "rocket_point_pos_world_z",
    ]

    available_cols = pd.read_csv(step_path, nrows=0).columns
    usecols = [col for col in usecols if col in available_cols]
    required = {"update_id", "episode_id", "step_id"}
    if not required.issubset(set(usecols)):
        return None

    # update_id can drift between the first step and the terminal episode row
    # when an episode crosses an optimizer update boundary, while episode_id can
    # reset after a training-process restart. Use segment + episode_id.
    keys = set(zip(episodes["episode_segment"].astype(int), episodes["episode_id"].astype(int)))
    rows: list[pd.DataFrame] = []
    seen: set[tuple[int, int]] = set()
    step_segment = 0
    previous_episode_id: int | None = None

    for chunk in pd.read_csv(step_path, usecols=usecols, chunksize=250_000, low_memory=False):
        chunk["update_id"] = pd.to_numeric(chunk["update_id"], errors="coerce")
        chunk["episode_id"] = pd.to_numeric(chunk["episode_id"], errors="coerce")
        chunk["step_id"] = pd.to_numeric(chunk["step_id"], errors="coerce")
        chunk = chunk.dropna(subset=["update_id", "episode_id", "step_id"])
        chunk["update_id"] = chunk["update_id"].astype(int)
        chunk["episode_id"] = chunk["episode_id"].astype(int)
        chunk, step_segment, previous_episode_id = add_episode_segments_to_step_chunk(
            chunk, step_segment, previous_episode_id
        )
        chunk = chunk[chunk["update_id"] <= last_completed_update]
        chunk = chunk[chunk["step_id"] == 1]
        if chunk.empty:
            continue

        chunk["_key"] = list(zip(chunk["episode_segment"], chunk["episode_id"]))
        chunk = chunk[chunk["_key"].isin(keys)]
        chunk = chunk[~chunk["_key"].isin(seen)]
        if chunk.empty:
            continue

        seen.update(chunk["_key"].tolist())
        rows.append(chunk.drop(columns=["_key"]))

        if len(seen) >= len(keys):
            break

    if not rows:
        return None

    reset_points = pd.concat(rows, ignore_index=True)
    reset_points = reset_points.drop_duplicates(["episode_segment", "episode_id"], keep="first")
    return reset_points


def load_terminal_success_points(
    logs_dir: Path,
    episodes: pd.DataFrame,
    last_completed_update: int,
) -> pd.DataFrame | None:
    step_path = logs_dir / "step_log.csv"
    if not step_path.exists():
        return None

    success_keys = set(
        zip(
            episodes.loc[episodes["done_reason"] == "success", "episode_segment"].astype(int),
            episodes.loc[episodes["done_reason"] == "success", "episode_id"].astype(int),
        )
    )
    if not success_keys:
        return None

    usecols = [
        "update_id",
        "episode_id",
        "step_id",
        "done",
        "done_reason",
        "success",
        "distance",
        "theta_deg",
        "alpha_deg",
        "beta_deg",
        "rocket_point_pos_world_x",
        "rocket_point_pos_world_y",
        "rocket_point_pos_world_z",
        "target_point_pos_world_x",
        "target_point_pos_world_y",
        "target_point_pos_world_z",
        "rel_pos_world_x",
        "rel_pos_world_y",
        "rel_pos_world_z",
    ]

    available_cols = pd.read_csv(step_path, nrows=0).columns
    usecols = [col for col in usecols if col in available_cols]
    required = {"update_id", "episode_id", "done_reason", "distance"}
    if not required.issubset(set(usecols)):
        return None

    rows: list[pd.DataFrame] = []
    seen: set[tuple[int, int]] = set()
    step_segment = 0
    previous_episode_id: int | None = None

    for chunk in pd.read_csv(step_path, usecols=usecols, chunksize=250_000, low_memory=False):
        chunk["update_id"] = pd.to_numeric(chunk["update_id"], errors="coerce")
        chunk["episode_id"] = pd.to_numeric(chunk["episode_id"], errors="coerce")
        chunk = chunk.dropna(subset=["update_id", "episode_id"])
        chunk["update_id"] = chunk["update_id"].astype(int)
        chunk["episode_id"] = chunk["episode_id"].astype(int)
        chunk, step_segment, previous_episode_id = add_episode_segments_to_step_chunk(
            chunk, step_segment, previous_episode_id
        )
        chunk = chunk[chunk["update_id"] <= last_completed_update]
        chunk["_key"] = list(zip(chunk["episode_segment"], chunk["episode_id"]))
        chunk = chunk[chunk["_key"].isin(success_keys)]
        chunk = chunk[chunk["done_reason"] == "success"]
        if "success" in chunk.columns:
            chunk = chunk[pd.to_numeric(chunk["success"], errors="coerce").fillna(0).astype(int) == 1]
        if chunk.empty:
            continue

        chunk = chunk.sort_values(["episode_segment", "episode_id", "step_id" if "step_id" in chunk.columns else "update_id"])
        chunk = chunk.drop_duplicates(["episode_segment", "episode_id"], keep="last")
        chunk = chunk[~chunk["_key"].isin(seen)]
        if chunk.empty:
            continue

        seen.update(chunk["_key"].tolist())
        rows.append(chunk.drop(columns=["_key"]))
        if len(seen) >= len(success_keys):
            break

    if not rows:
        return None

    points = pd.concat(rows, ignore_index=True)
    points = points.drop_duplicates(["episode_segment", "episode_id"], keep="last")
    return points


CLOCK_REQUIRED_COLUMNS = [
    "update_id",
    "target_clock_12",
    "target_clock_6",
    "target_clock_3",
    "target_clock_9",
    "clock_12_cmd",
    "clock_6_cmd",
    "clock_3_cmd",
    "clock_9_cmd",
]

CLOCK_OPTIONAL_COLUMNS = [
    "episode_id",
    "step_id",
    "theta_deg",
    "distance",
    "clock_validity",
    "action_clock_mag",
    "target_clock_angle_deg",
    "action_clock_angle_deg",
    "reward_clock_action_alignment",
    "reward_clock_wrong_channel",
    "reward_clock_coactivation",
]

CLOCK_CHANNELS = ["12", "6", "3", "9"]


def _numeric_column(frame: pd.DataFrame, col: str) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[col], errors="coerce")


def add_clock_alignment_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    for col in CLOCK_REQUIRED_COLUMNS + CLOCK_OPTIONAL_COLUMNS:
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors="coerce")
        else:
            work[col] = np.nan

    target_12 = work["target_clock_12"].to_numpy(dtype=float)
    target_6 = work["target_clock_6"].to_numpy(dtype=float)
    target_3 = work["target_clock_3"].to_numpy(dtype=float)
    target_9 = work["target_clock_9"].to_numpy(dtype=float)
    cmd_12 = work["clock_12_cmd"].to_numpy(dtype=float)
    cmd_6 = work["clock_6_cmd"].to_numpy(dtype=float)
    cmd_3 = work["clock_3_cmd"].to_numpy(dtype=float)
    cmd_9 = work["clock_9_cmd"].to_numpy(dtype=float)

    target_x = target_3 - target_9
    target_y = target_12 - target_6
    action_x = cmd_3 - cmd_9
    action_y = cmd_12 - cmd_6
    target_mag = np.sqrt(np.square(target_x) + np.square(target_y))
    action_mag = np.sqrt(np.square(action_x) + np.square(action_y))
    denom = target_mag * action_mag
    dot = target_x * action_x + target_y * action_y

    work["clock_vector_cosine"] = np.where(denom > 1e-6, np.clip(dot / denom, -1.0, 1.0), np.nan)
    work["clock_vector_error_deg"] = np.degrees(np.arccos(np.clip(work["clock_vector_cosine"], -1.0, 1.0)))
    work["target_clock_mag"] = target_mag
    work["net_clock_cmd_mag"] = action_mag
    work["clock_opposite_cmd"] = (
        target_12 * cmd_6
        + target_6 * cmd_12
        + target_3 * cmd_9
        + target_9 * cmd_3
    )
    work["clock_coactivation"] = np.minimum(cmd_12, cmd_6) + np.minimum(cmd_3, cmd_9)

    target_stack = np.column_stack([target_12, target_6, target_3, target_9])
    action_stack = np.column_stack([cmd_12, cmd_6, cmd_3, cmd_9])
    target_clean = np.where(np.isnan(target_stack), -np.inf, target_stack)
    action_clean = np.where(np.isnan(action_stack), -np.inf, action_stack)
    target_dom = np.argmax(target_clean, axis=1)
    action_dom = np.argmax(action_clean, axis=1)
    target_peak = np.max(target_clean, axis=1)
    action_peak = np.max(action_clean, axis=1)
    target_peak = np.where(np.isfinite(target_peak), target_peak, np.nan)
    action_peak = np.where(np.isfinite(action_peak), action_peak, np.nan)
    dominant_valid = (target_peak > 0.05) & (action_peak > 0.05)
    work["clock_dominant_match"] = np.where(dominant_valid, (target_dom == action_dom).astype(float), np.nan)
    return work


def load_clock_alignment_report(
    logs_dir: Path,
    start_update: int | None,
    end_update: int | None,
) -> pd.DataFrame | None:
    step_path = logs_dir / "step_log.csv"
    if not step_path.exists():
        return None

    try:
        available_cols = pd.read_csv(step_path, nrows=0).columns
    except pd.errors.EmptyDataError:
        return None

    if not set(CLOCK_REQUIRED_COLUMNS).issubset(set(available_cols)):
        return None

    usecols = [col for col in CLOCK_REQUIRED_COLUMNS + CLOCK_OPTIONAL_COLUMNS if col in available_cols]
    metric_cols = [
        "clock_vector_cosine",
        "clock_vector_error_deg",
        "clock_dominant_match",
        "target_clock_mag",
        "net_clock_cmd_mag",
        "clock_opposite_cmd",
        "clock_coactivation",
        "target_clock_12",
        "target_clock_6",
        "target_clock_3",
        "target_clock_9",
        "clock_12_cmd",
        "clock_6_cmd",
        "clock_3_cmd",
        "clock_9_cmd",
        "theta_deg",
        "distance",
        "clock_validity",
        "action_clock_mag",
        "reward_clock_action_alignment",
        "reward_clock_wrong_channel",
        "reward_clock_coactivation",
    ]

    parts: list[pd.DataFrame] = []
    for chunk in pd.read_csv(step_path, usecols=usecols, chunksize=250_000, low_memory=False):
        chunk["update_id"] = pd.to_numeric(chunk["update_id"], errors="coerce")
        chunk = chunk[chunk["update_id"].notna()].copy()
        chunk["update_id"] = chunk["update_id"].astype(int)
        if start_update is not None:
            chunk = chunk[chunk["update_id"] >= int(start_update)]
        if end_update is not None:
            chunk = chunk[chunk["update_id"] <= int(end_update)]
        if chunk.empty:
            continue

        metrics = add_clock_alignment_metrics(chunk)
        grouped = metrics.groupby("update_id")[metric_cols].agg(["sum", "count"])
        grouped.columns = [f"{metric}_{stat}" for metric, stat in grouped.columns]
        parts.append(grouped)

    if not parts:
        return None

    combined = pd.concat(parts).groupby(level=0).sum().sort_index()
    report = pd.DataFrame({"update_id": combined.index.astype(int)})
    for metric in metric_cols:
        count = combined[f"{metric}_count"].replace(0, np.nan)
        report[metric] = combined[f"{metric}_sum"] / count
    report["sample_count"] = combined["clock_vector_cosine_count"].astype(int)
    return report.reset_index(drop=True)


def apply_plot_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 170,
            "savefig.dpi": 170,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#0f172a",
            "xtick.color": "#0f172a",
            "ytick.color": "#0f172a",
            "font.size": 9,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "legend.fontsize": 8,
            "axes.grid": True,
            "grid.alpha": 0.22,
        }
    )


def save_fig(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, bbox_inches="tight", facecolor="white", transparent=False)
    plt.close(fig)
    try:
        from PIL import Image

        image = Image.open(path)
        if image.mode == "RGBA":
            white = Image.new("RGBA", image.size, (255, 255, 255, 255))
            white.alpha_composite(image)
            white.convert("RGB").save(path)
    except Exception as exc:  # pragma: no cover - plotting should not fail if post-processing is unavailable.
        print(f"warning: could not flatten image background for {path}: {exc}")


def phase_counts(episodes: pd.DataFrame) -> dict[str, int]:
    return {str(k): int(v) for k, v in episodes["done_reason"].value_counts().items()}


def rolling(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=1).mean() * 100.0


def plot_success_rate(episodes: pd.DataFrame, out_path: Path, title: str) -> None:
    x = episodes["episode_index"]
    r20 = rolling(episodes["is_success"], 20)
    r50 = rolling(episodes["is_success"], 50)
    r100 = rolling(episodes["is_success"], 100)
    success_rate = 100.0 * episodes["is_success"].mean()
    counts = phase_counts(episodes)

    fig, ax = plt.subplots(figsize=(12.0, 6.0))
    ax.plot(x, r20, color="#38bdf8", linewidth=1.2, label=f"R20 last {r20.iloc[-1]:.1f}%")
    ax.plot(x, r50, color="#2563eb", linewidth=1.8, label=f"R50 last {r50.iloc[-1]:.1f}%")
    ax.plot(x, r100, color="#111827", linewidth=2.1, label=f"R100 last {r100.iloc[-1]:.1f}%")
    ax.axhline(90.0, color="#16a34a", linestyle="--", linewidth=1.0, label="90% reference")
    ax.axhline(80.0, color="#f97316", linestyle=":", linewidth=1.0, label="80% reference")

    fail_order = [r for r in OUTCOME_ORDER if r != "success"]
    for offset, reason in enumerate(fail_order):
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        y = np.full(len(subset), -4.0 - 2.8 * offset)
        ax.scatter(
            subset["episode_index"],
            y,
            marker="|",
            s=28,
            linewidths=2.0,
            color=OUTCOME_COLORS.get(reason, OUTCOME_COLORS["other"]),
            label=f"{reason} marks n={len(subset)}",
        )

    ax.set_xlim(1, len(episodes))
    ax.set_ylim(-20, 104)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Success rate (%)")
    ax.set_title(f"{title} | n={len(episodes)} | overall SR={success_rate:.1f}%")
    ax.text(
        0.01,
        0.02,
        "Bottom marks show failure density; y position is not a metric.",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.9},
    )
    ax.legend(loc="lower right", ncol=2, frameon=True, framealpha=0.94)

    text = "Counts: " + ", ".join(f"{k}={v}" for k, v in counts.items())
    ax.text(
        0.99,
        0.98,
        text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.9},
    )
    save_fig(fig, out_path)


def plot_success_rug(episodes: pd.DataFrame, out_path: Path, title: str) -> None:
    counts = phase_counts(episodes)
    fig, ax = plt.subplots(figsize=(12.0, 2.6))

    for reason in OUTCOME_ORDER + sorted(set(counts) - set(OUTCOME_ORDER)):
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        ax.scatter(
            subset["episode_index"],
            np.zeros(len(subset)),
            marker="|",
            s=180,
            linewidths=1.8,
            color=OUTCOME_COLORS.get(reason, OUTCOME_COLORS["other"]),
            label=f"{reason}: n={len(subset)} ({100.0 * len(subset) / len(episodes):.1f}%)",
        )

    ax.set_xlim(1, len(episodes))
    ax.set_ylim(-1, 1)
    ax.set_yticks([])
    ax.set_xlabel("Episode")
    ax.set_title(f"{title} | per-episode outcome density")
    ax.grid(axis="x", alpha=0.2)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=min(5, len(counts)), frameon=True)
    save_fig(fig, out_path)


def plot_radius_distribution(episodes: pd.DataFrame, out_path: Path, title: str, bins: np.ndarray) -> None:
    fig, ax = plt.subplots(figsize=(12.0, 5.5))

    data = []
    labels = []
    colors = []
    for reason in OUTCOME_ORDER + sorted(set(episodes["done_reason"]) - set(OUTCOME_ORDER)):
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        data.append(subset["start_distance"].to_numpy())
        labels.append(f"{reason} n={len(subset)}")
        colors.append(OUTCOME_COLORS.get(reason, OUTCOME_COLORS["other"]))

    ax.hist(data, bins=bins, stacked=True, label=labels, color=colors, edgecolor="white", linewidth=0.8)
    ax.set_xlabel("Start distance (m)")
    ax.set_ylabel("Episode count")
    ax.set_title(f"{title} | start-distance distribution by outcome")
    ax.legend(loc="upper right", frameon=True, framealpha=0.94)
    save_fig(fig, out_path)


def plot_radius_phase_plan(
    episodes: pd.DataFrame,
    out_path: Path,
    title: str,
    bins: np.ndarray,
    current_min: float | None,
    current_max: float | None,
    current_phase_label: str,
    phase_plan: pd.DataFrame | None,
) -> pd.DataFrame:
    episodes = episodes.copy()
    episodes["dist_bin"] = pd.cut(episodes["start_distance"], bins=bins, right=False, include_lowest=True)
    rows = []
    for dist_bin, group in episodes.groupby("dist_bin", observed=False):
        if group.empty:
            continue
        rows.append(
            {
                "left": float(dist_bin.left),
                "right": float(dist_bin.right),
                "mid": 0.5 * (float(dist_bin.left) + float(dist_bin.right)),
                "n": int(len(group)),
                "success": int((group["done_reason"] == "success").sum()),
                "near_miss": int((group["done_reason"] == "near_miss").sum()),
                "low_agl": int((group["done_reason"] == "low_agl").sum()),
                "wrong_way": int((group["done_reason"] == "wrong_way").sum()),
                "success_rate": 100.0 * float(group["is_success"].mean()),
            }
        )
    bin_df = pd.DataFrame(rows)

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(14.5, 9.2),
        sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1.05]},
    )
    fig.subplots_adjust(left=0.10, right=0.80, top=0.88, bottom=0.11, hspace=0.42)
    fig.suptitle(f"{title}\nReset Radius Phase Plan", fontsize=13, fontweight="bold")

    if bin_df.empty:
        ax_top.text(0.5, 0.5, "No radius-bin data", transform=ax_top.transAxes, ha="center", va="center")
        ax_bottom.set_axis_off()
        save_fig(fig, out_path)
        return bin_df

    bin_df = bin_df.sort_values("mid").reset_index(drop=True)
    bin_width = float(bin_df["right"].iloc[0] - bin_df["left"].iloc[0])
    bar_width = max(0.9, bin_width * 0.84)

    ax_top.bar(
        bin_df["mid"],
        bin_df["success_rate"],
        width=bar_width,
        color="#4f7ead",
        edgecolor="white",
        linewidth=0.9,
        label="Success rate by reset-radius bin",
    )
    ax_top.axhline(90.0, color="#16a34a", linestyle="--", linewidth=1.0, alpha=0.85, label="90% reference")
    ax_top.axhline(80.0, color="#f97316", linestyle=":", linewidth=1.0, alpha=0.95, label="80% reference")

    for _, row in bin_df.iterrows():
        ax_top.text(
            row["mid"],
            min(106.0, row["success_rate"] + 3.0),
            f"{row['success_rate']:.1f}%\nn={int(row['n'])}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
        )
        ax_top.text(
            row["mid"],
            5.0,
            f"S={int(row['success'])}\nNM={int(row['near_miss'])}\nWW={int(row['wrong_way'])} LA={int(row['low_agl'])}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#0f172a",
            bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.88},
        )

    configured_left = configured_right = None
    if current_min is not None and current_max is not None:
        configured_left = float(min(current_min, current_max))
        configured_right = float(max(current_min, current_max))
        for x in [configured_left, configured_right]:
            ax_top.axvline(x, color="#0f172a", linestyle="--", linewidth=1.0, alpha=0.70)
            ax_bottom.axvline(x, color="#0f172a", linestyle="--", linewidth=1.0, alpha=0.70)

    ax_top.set_ylim(0.0, 112.0)
    ax_top.set_ylabel("Success Rate (%)")
    ax_top.set_title("1) Success by observed start-distance bin")
    ax_top.legend(loc="upper left", frameon=True, framealpha=0.94)

    observed_left = float(bin_df["left"].min())
    observed_right = float(bin_df["right"].max())
    x_values = [observed_left, observed_right]
    if configured_left is not None and configured_right is not None:
        x_values.extend([configured_left, configured_right])
    x_pad = max(2.0, bin_width * 0.5)
    ax_top.set_xlim(min(x_values) - x_pad, max(x_values) + x_pad)

    ax_bottom.set_ylim(-0.15, 3.65)
    ax_bottom.set_yticks([3.05, 1.85, 0.55])
    ax_bottom.set_yticklabels(["configured phase", "observed bins", "bin SR"])
    ax_bottom.tick_params(axis="y", length=0)
    ax_bottom.set_xlabel("Reset Radius / start_distance (m)")
    ax_bottom.set_title("2) Phase / radius-bin map", pad=10)

    if configured_left is not None and configured_right is not None:
        y0 = 2.76
        height = 0.58
        ax_bottom.add_patch(
            plt.Rectangle(
                (configured_left, y0),
                configured_right - configured_left,
                height,
                facecolor="#f9c58d",
                edgecolor="#d97706",
                alpha=0.78,
                label="Configured phase radius",
            )
        )
        ax_bottom.text(
            0.5 * (configured_left + configured_right),
            y0 + 0.5 * height,
            f"{current_phase_label}\nconfigured {configured_left:.0f}-{configured_right:.0f}m",
            ha="center",
            va="center",
            fontsize=9.5,
            fontweight="bold",
            color="#92400e",
        )

    observed_y0 = 1.55
    observed_height = 0.60
    for idx, row in bin_df.iterrows():
        ax_bottom.add_patch(
            plt.Rectangle(
                (row["left"], observed_y0),
                row["right"] - row["left"],
                observed_height,
                facecolor="#dbeafe" if idx % 2 == 0 else "#bfdbfe",
                edgecolor="#3b82f6",
                alpha=0.78,
                label="Observed start_distance bins" if idx == 0 else "_nolegend_",
            )
        )
        ax_bottom.text(
            row["mid"],
            observed_y0 + 0.5 * observed_height,
            f"{row['left']:.0f}-{row['right']:.0f}m\nn={int(row['n'])} S={int(row['success'])}",
            ha="center",
            va="center",
            fontsize=8.5,
            color="#1e3a8a",
            fontweight="bold",
        )

    line_y = 0.55
    ax_bottom.plot(
        bin_df["mid"],
        np.full(len(bin_df), line_y),
        color="#111827",
        marker="o",
        linewidth=1.8,
        label="Observed-bin success labels",
    )
    for _, row in bin_df.iterrows():
        ax_bottom.text(
            row["mid"],
            line_y + 0.18,
            f"SR={row['success_rate']:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8.5,
            fontweight="bold",
        )

    ax_bottom.legend(loc="lower left", frameon=True, framealpha=0.94)
    fig.text(
        0.825,
        0.72,
        "Standard legend\n"
        "n = total episodes\n"
        "S = success\n"
        "NM = near_miss\n"
        "WW = wrong_way\n"
        "LA = low_agl\n"
        "HA = high_altitude\n"
        "TO = timeout",
        ha="left",
        va="top",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.96},
    )
    fig.text(
        0.825,
        0.34,
        "Reading order\n"
        "Top: SR per radius bin.\n"
        "Bottom orange: configured phase.\n"
        "Bottom blue: observed start_distance bins, not phases.\n"
        "Black dashed lines: configured min/max.",
        ha="left",
        va="top",
        fontsize=8.5,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f8fafc", "edgecolor": "#cbd5e1", "alpha": 0.96},
    )

    save_fig(fig, out_path)
    return bin_df


def plot_reset_outcome_polar(
    episodes: pd.DataFrame,
    reset_points: pd.DataFrame | None,
    out_path: Path,
    title: str,
) -> None:
    fig = plt.figure(figsize=(9.0, 8.0))
    ax = fig.add_subplot(111, projection="polar")

    plot_df = episodes.copy()
    if reset_points is not None:
        plot_df = plot_df.merge(
            reset_points.drop(columns=["update_id"], errors="ignore"),
            on=["episode_segment", "episode_id"],
            how="left",
        )

    if {"rel_pos_world_x", "rel_pos_world_z"}.issubset(plot_df.columns) and plot_df["rel_pos_world_x"].notna().any():
        x = pd.to_numeric(plot_df["rel_pos_world_x"], errors="coerce")
        z = pd.to_numeric(plot_df["rel_pos_world_z"], errors="coerce")
        theta = np.arctan2(z, x)
        radius = np.sqrt(np.square(x) + np.square(z))
        subtitle = "angle from first logged relative target vector"
    elif {
        "target_point_pos_world_x",
        "target_point_pos_world_z",
        "rocket_point_pos_world_x",
        "rocket_point_pos_world_z",
    }.issubset(plot_df.columns):
        x = pd.to_numeric(plot_df["target_point_pos_world_x"], errors="coerce") - pd.to_numeric(
            plot_df["rocket_point_pos_world_x"], errors="coerce"
        )
        z = pd.to_numeric(plot_df["target_point_pos_world_z"], errors="coerce") - pd.to_numeric(
            plot_df["rocket_point_pos_world_z"], errors="coerce"
        )
        theta = np.arctan2(z, x)
        radius = np.sqrt(np.square(x) + np.square(z))
        subtitle = "angle from first logged target-rocket vector"
    else:
        # Episode logs do not store reset bearing; spread points deterministically so radius can still be read.
        theta = np.linspace(0.0, 2.0 * np.pi, len(plot_df), endpoint=False)
        radius = pd.to_numeric(plot_df["start_distance"], errors="coerce")
        subtitle = "synthetic angle; episode log has no reset bearing"

    missing = pd.isna(theta) | pd.isna(radius)
    if np.any(missing):
        fallback_theta = np.linspace(0.0, 2.0 * np.pi, len(plot_df), endpoint=False)
        fallback_radius = pd.to_numeric(plot_df["start_distance"], errors="coerce")
        theta = pd.Series(theta).mask(missing, fallback_theta).to_numpy()
        radius = pd.Series(radius).mask(missing, fallback_radius).to_numpy()
        subtitle = f"{subtitle}; missing bearings use synthetic fallback"

    plot_df["_theta"] = theta
    plot_df["_radius"] = radius
    plot_df = plot_df.dropna(subset=["_theta", "_radius"])

    for reason in OUTCOME_ORDER + sorted(set(plot_df["done_reason"]) - set(OUTCOME_ORDER)):
        subset = plot_df[plot_df["done_reason"] == reason]
        if subset.empty:
            continue
        ax.scatter(
            subset["_theta"],
            subset["_radius"],
            s=20 if reason == "success" else 34,
            alpha=0.72,
            color=OUTCOME_COLORS.get(reason, OUTCOME_COLORS["other"]),
            label=f"{reason} n={len(subset)}",
        )

    ax.set_theta_zero_location("E")
    ax.set_theta_direction(-1)
    ax.set_title(f"{title}\nreset outcome polar ({subtitle})", va="bottom")
    ax.legend(loc="upper right", bbox_to_anchor=(1.24, 1.12), frameon=True, framealpha=0.94)
    save_fig(fig, out_path)


def plot_hit_location_polar(
    episodes: pd.DataFrame,
    terminal_points: pd.DataFrame | None,
    out_path: Path,
    title: str,
) -> None:
    if terminal_points is None or terminal_points.empty:
        fig = plt.figure(figsize=(9.4, 8.2))
        ax = fig.add_subplot(111, projection="polar")
        ax.set_title(f"{title}\nTarget-centered success hit locations", va="bottom")
        ax.text(
            0.5,
            0.5,
            "No success hits in this phase window.",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.96},
        )
        save_fig(fig, out_path)
        return

    hit_df = terminal_points.copy()
    success_meta = episodes.loc[
        episodes["done_reason"] == "success",
        ["episode_segment", "episode_id", "episode_index", "update_id", "final_distance", "final_theta_deg"],
    ].copy()
    hit_df = hit_df.merge(success_meta, on=["episode_segment", "episode_id"], how="left", suffixes=("", "_episode"))

    if {
        "rocket_point_pos_world_x",
        "rocket_point_pos_world_z",
        "target_point_pos_world_x",
        "target_point_pos_world_z",
    }.issubset(hit_df.columns):
        x = pd.to_numeric(hit_df["rocket_point_pos_world_x"], errors="coerce") - pd.to_numeric(
            hit_df["target_point_pos_world_x"], errors="coerce"
        )
        z = pd.to_numeric(hit_df["rocket_point_pos_world_z"], errors="coerce") - pd.to_numeric(
            hit_df["target_point_pos_world_z"], errors="coerce"
        )
        source_note = "rocket-target terminal point"
    elif {"rel_pos_world_x", "rel_pos_world_z"}.issubset(hit_df.columns):
        x = -pd.to_numeric(hit_df["rel_pos_world_x"], errors="coerce")
        z = -pd.to_numeric(hit_df["rel_pos_world_z"], errors="coerce")
        source_note = "-rel_pos_world terminal point"
    else:
        raise ValueError("Terminal log has no world/relative position fields for hit-location polar plot.")

    radius = np.sqrt(np.square(x) + np.square(z))
    theta = np.arctan2(z, x)
    hit_df["_hit_theta"] = theta
    hit_df["_hit_radius"] = radius
    hit_df = hit_df.dropna(subset=["_hit_theta", "_hit_radius"])

    fig = plt.figure(figsize=(9.4, 8.2))
    ax = fig.add_subplot(111, projection="polar")

    ax.scatter(
        hit_df["_hit_theta"],
        hit_df["_hit_radius"],
        color="#2563eb",
        s=18,
        alpha=0.74,
        edgecolors="none",
    )

    max_radius = max(16.0, float(np.nanmax(hit_df["_hit_radius"])) + 1.0)
    ax.set_rlim(0.0, max_radius)
    for ring in [5.0, 10.0, 15.0]:
        if ring <= max_radius:
            ax.plot(np.linspace(0, 2 * np.pi, 240), np.full(240, ring), color="#94a3b8", linewidth=0.8, alpha=0.45)
            ax.text(np.deg2rad(42), ring, f"{ring:.0f}m", fontsize=8, color="#475569")

    ax.set_theta_zero_location("E")
    ax.set_theta_direction(-1)
    ax.set_title(f"{title}\nTarget-centered success hit locations ({source_note})", va="bottom")

    stats = (
        f"success hits n={len(hit_df)}\n"
        f"mean hit distance={hit_df['_hit_radius'].mean():.2f}m\n"
        f"median={hit_df['_hit_radius'].median():.2f}m\n"
        f"p90={hit_df['_hit_radius'].quantile(0.90):.2f}m"
    )
    ax.text(
        1.18,
        0.08,
        stats,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.94},
    )
    save_fig(fig, out_path)


def _plot_line_if_available(
    ax: plt.Axes,
    x: pd.Series,
    y: pd.Series,
    label: str,
    color: str,
    linestyle: str = "-",
    linewidth: float = 1.8,
) -> bool:
    if y.isna().all():
        return False
    ax.plot(x, y, color=color, linestyle=linestyle, linewidth=linewidth, label=label)
    return True


def plot_clock_action_alignment(clock_report: pd.DataFrame | None, out_path: Path, title: str) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(13.5, 11.0), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.82, top=0.90, bottom=0.08, hspace=0.34)
    fig.suptitle(f"{title}\nV9 Clock Action Alignment", fontsize=13, fontweight="bold")

    if clock_report is None or clock_report.empty:
        for ax in axes:
            ax.set_axis_off()
        axes[0].text(
            0.5,
            0.5,
            "No V9 clock columns were found in step_log.csv.\nThis plot will populate after V9 training writes clock state/action logs.",
            transform=axes[0].transAxes,
            ha="center",
            va="center",
            fontsize=11,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.96},
        )
        save_fig(fig, out_path)
        return

    x = clock_report["update_id"]
    axes[0].axhline(0.0, color="#64748b", linewidth=0.8, alpha=0.7)
    axes[0].axhline(0.75, color="#16a34a", linestyle="--", linewidth=0.9, alpha=0.75)
    _plot_line_if_available(
        axes[0],
        x,
        clock_report["clock_vector_cosine"],
        "target/action vector cosine",
        "#111827",
        linewidth=2.0,
    )
    _plot_line_if_available(
        axes[0],
        x,
        clock_report["clock_dominant_match"],
        "dominant channel match ratio",
        "#2563eb",
        linestyle=":",
        linewidth=2.0,
    )
    axes[0].set_ylim(-1.05, 1.05)
    axes[0].set_ylabel("Alignment")
    axes[0].set_title("1) Does the selected action channel point toward the target clock channel?")
    axes[0].legend(loc="lower right", frameon=True, framealpha=0.94)

    command_colors = {
        "clock_12_cmd": "#16a34a",
        "clock_6_cmd": "#ef4444",
        "clock_3_cmd": "#2563eb",
        "clock_9_cmd": "#f59e0b",
    }
    for col, color in command_colors.items():
        _plot_line_if_available(axes[1], x, clock_report[col], col, color)
    _plot_line_if_available(
        axes[1],
        x,
        clock_report["net_clock_cmd_mag"],
        "net command magnitude",
        "#0f172a",
        linestyle="--",
        linewidth=2.1,
    )
    axes[1].set_ylabel("Command")
    axes[1].set_title("2) Mean action output by clock channel")
    axes[1].legend(loc="upper right", ncol=3, frameon=True, framealpha=0.94)

    target_colors = {
        "target_clock_12": "#16a34a",
        "target_clock_6": "#ef4444",
        "target_clock_3": "#2563eb",
        "target_clock_9": "#f59e0b",
    }
    for col, color in target_colors.items():
        _plot_line_if_available(axes[2], x, clock_report[col], col, color)
    _plot_line_if_available(
        axes[2],
        x,
        clock_report["target_clock_mag"],
        "target clock magnitude",
        "#0f172a",
        linestyle="--",
        linewidth=2.1,
    )
    axes[2].set_ylabel("Target channel")
    axes[2].set_title("3) Mean target direction encoded in clock channels")
    axes[2].legend(loc="upper right", ncol=3, frameon=True, framealpha=0.94)

    reward_lines = [
        ("reward_clock_action_alignment", "#16a34a", "-"),
        ("reward_clock_wrong_channel", "#ef4444", "-"),
        ("reward_clock_coactivation", "#f59e0b", "-"),
        ("clock_opposite_cmd", "#7c3aed", "--"),
        ("clock_coactivation", "#64748b", "--"),
    ]
    any_reward = False
    for col, color, linestyle in reward_lines:
        any_reward |= _plot_line_if_available(axes[3], x, clock_report[col], col, color, linestyle=linestyle)
    if not any_reward:
        axes[3].text(0.5, 0.5, "No clock reward terms found.", transform=axes[3].transAxes, ha="center", va="center")
    axes[3].set_ylabel("Reward / penalty")
    axes[3].set_xlabel("Update")
    axes[3].set_title("4) Clock-specific reward terms and anti-pattern signals")
    axes[3].legend(loc="upper right", ncol=2, frameon=True, framealpha=0.94)

    last = clock_report.iloc[-1]
    fig.text(
        0.835,
        0.70,
        "How to read\n"
        "Cosine near +1: action points at target.\n"
        "Cosine near 0: sideways/no useful steering.\n"
        "Cosine below 0: action points away.\n"
        "Dominant match: strongest action channel\n"
        "equals strongest target channel.",
        ha="left",
        va="top",
        fontsize=8.8,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.96},
    )
    fig.text(
        0.835,
        0.33,
        "Last update\n"
        f"up={int(last['update_id'])}\n"
        f"cos={last['clock_vector_cosine']:.3f}\n"
        f"match={100.0 * last['clock_dominant_match']:.1f}%\n"
        f"net_cmd={last['net_clock_cmd_mag']:.3f}\n"
        f"samples/update={int(last['sample_count'])}",
        ha="left",
        va="top",
        fontsize=8.8,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f8fafc", "edgecolor": "#cbd5e1", "alpha": 0.96},
    )
    save_fig(fig, out_path)


def read_phase_plan(path: Path | None, current_min: float | None, current_max: float | None) -> pd.DataFrame | None:
    if path is None or not path.exists():
        return None
    phase_plan = pd.read_csv(path)
    required = {"radius_min", "radius_max"}
    if not required.issubset(phase_plan.columns):
        return None

    if current_min is not None and current_max is not None:
        lower = min(current_min, current_max)
        upper = max(current_min, current_max)
        phase_plan = phase_plan[
            (pd.to_numeric(phase_plan["radius_max"], errors="coerce") >= lower)
            & (pd.to_numeric(phase_plan["radius_min"], errors="coerce") <= upper)
        ].copy()

    return phase_plan


def make_bins(episodes: pd.DataFrame, current_min: float | None, current_max: float | None, bin_width: float) -> np.ndarray:
    observed_min = float(pd.to_numeric(episodes["start_distance"], errors="coerce").min())
    observed_max = float(pd.to_numeric(episodes["start_distance"], errors="coerce").max())
    mins = [observed_min]
    maxs = [observed_max]
    if current_min is not None:
        mins.append(current_min)
        maxs.append(current_min)
    if current_max is not None:
        mins.append(current_max)
        maxs.append(current_max)

    lo = math.floor(min(mins) / bin_width) * bin_width
    hi = math.ceil(max(maxs) / bin_width) * bin_width
    if hi <= lo:
        hi = lo + bin_width
    return np.arange(lo, hi + bin_width, bin_width)


def write_summary(
    out_path: Path,
    title: str,
    phase_name: str,
    episodes: pd.DataFrame,
    last_completed_update: int,
    bin_df: pd.DataFrame,
    output_names: list[str],
) -> None:
    r20 = rolling(episodes["is_success"], 20).iloc[-1]
    r50 = rolling(episodes["is_success"], 50).iloc[-1]
    r100 = rolling(episodes["is_success"], 100).iloc[-1]
    success_rate = 100.0 * episodes["is_success"].mean()
    counts = phase_counts(episodes)

    lines = [
        title,
        "",
        "Generated from completed updates only.",
        f"phase_name: {phase_name}",
        f"update_range: {int(episodes['update_id'].min())}-{last_completed_update}",
        f"episodes: {len(episodes)}",
        f"success_rate: {success_rate:.3f}%",
        f"rolling_tail: R20={r20:.3f}% R50={r50:.3f}% R100={r100:.3f}%",
        f"done_counts: {counts}",
        f"start_distance_range: {episodes['start_distance'].min():.3f}-{episodes['start_distance'].max():.3f} m",
        "",
        "Radius bins:",
    ]
    if not bin_df.empty:
        for _, row in bin_df.iterrows():
            lines.append(
                f"- {row['left']:.0f}-{row['right']:.0f}m: n={int(row['n'])}, "
                f"success={int(row['success'])}, SR={row['success_rate']:.2f}%"
            )
    else:
        lines.append("- no bins")

    lines += ["", "Outputs:"]
    lines += [f"- {name}" for name in output_names]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate standard per-phase training analysis graphs.")
    parser.add_argument("--logs-dir", default="logs", help="Directory containing episode_log.csv/update_log.csv/step_log.csv.")
    parser.add_argument("--output-dir", required=True, help="Directory where graphs will be written.")
    parser.add_argument("--phase-slug", required=True, help="File prefix, for example phase_2_2_live_up2320.")
    parser.add_argument("--phase-label", required=True, help="Human label, for example v8.7.6 - Phase 2.2.")
    parser.add_argument("--start-update", type=int, default=None, help="Optional inclusive lower update filter.")
    parser.add_argument("--end-update", type=int, default=None, help="Optional inclusive upper update filter.")
    parser.add_argument("--radius-min", type=float, default=None, help="Current configured radius minimum.")
    parser.add_argument("--radius-max", type=float, default=None, help="Current configured radius maximum.")
    parser.add_argument("--bin-width", type=float, default=5.0, help="Radius bin width in meters.")
    parser.add_argument("--phase-plan-csv", default=None, help="Optional curriculum phase plan CSV.")
    parser.add_argument("--skip-polar-step-log", action="store_true", help="Skip heavy step_log read for polar bearing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    apply_plot_style()

    logs_dir = Path(args.logs_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    episodes, last_completed_update = read_completed_episodes(logs_dir, args.start_update, args.end_update)
    phase_name = str(episodes["phase_name"].dropna().iloc[-1]) if "phase_name" in episodes else "unknown_phase"
    title = f"{args.phase_label} | up {int(episodes['update_id'].min())}-{last_completed_update}"

    bins = make_bins(episodes, args.radius_min, args.radius_max, args.bin_width)
    phase_plan = read_phase_plan(Path(args.phase_plan_csv) if args.phase_plan_csv else None, args.radius_min, args.radius_max)

    reset_points = None if args.skip_polar_step_log else load_reset_points(logs_dir, episodes, last_completed_update)
    terminal_success_points = load_terminal_success_points(logs_dir, episodes, last_completed_update)
    clock_report = load_clock_alignment_report(logs_dir, args.start_update, last_completed_update)

    prefix = slugify(args.phase_slug)
    outputs = {
        "success_rate": out_dir / f"{prefix}_success_rate.png",
        "success_rug": out_dir / f"{prefix}_success_rug.png",
        "reset_outcome_polar": out_dir / f"{prefix}_reset_outcome_polar.png",
        "hit_location_polar": out_dir / f"{prefix}_hit_location_polar.png",
        "reset_radius_distribution": out_dir / f"{prefix}_reset_radius_distribution.png",
        "reset_radius_phase_plan": out_dir / f"{prefix}_reset_radius_phase_plan.png",
        "clock_action_alignment": out_dir / f"{prefix}_clock_action_alignment.png",
        "episode_diagnostics": out_dir / f"{prefix}_episode_diagnostics.csv",
        "radius_bins": out_dir / f"{prefix}_reset_radius_bins.csv",
        "summary": out_dir / f"{prefix}_summary.txt",
    }

    plot_success_rate(episodes, outputs["success_rate"], title)
    plot_success_rug(episodes, outputs["success_rug"], title)
    plot_radius_distribution(episodes, outputs["reset_radius_distribution"], title, bins)
    bin_df = plot_radius_phase_plan(
        episodes,
        outputs["reset_radius_phase_plan"],
        title,
        bins,
        args.radius_min,
        args.radius_max,
        args.phase_label,
        phase_plan,
    )
    plot_reset_outcome_polar(episodes, reset_points, outputs["reset_outcome_polar"], title)
    plot_hit_location_polar(episodes, terminal_success_points, outputs["hit_location_polar"], title)
    plot_clock_action_alignment(clock_report, outputs["clock_action_alignment"], title)

    episodes.to_csv(outputs["episode_diagnostics"], index=False)
    bin_df.to_csv(outputs["radius_bins"], index=False)
    write_summary(
        outputs["summary"],
        title,
        phase_name,
        episodes,
        last_completed_update,
        bin_df,
        [path.name for path in outputs.values()],
    )

    print(f"phase_name={phase_name}")
    print(f"updates={int(episodes['update_id'].min())}-{last_completed_update}")
    print(f"episodes={len(episodes)}")
    print(f"success_rate={100.0 * episodes['is_success'].mean():.3f}%")
    print(f"output_dir={out_dir}")
    for path in outputs.values():
        print(path)


if __name__ == "__main__":
    main()
