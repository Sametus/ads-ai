import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_OFFSET_SEQUENCE = "-1,1,-2,2,-3,3,-4,4,-5,5"

TERMINAL_COLORS = {
    "success": "#1f9d55",
    "missed_intercept": "#f59e0b",
    "timeout": "#64748b",
    "low_agl": "#ef4444",
    "bad_angle": "#8b5cf6",
    "wrong_way": "#dc2626",
    "high_altitude": "#06b6d4",
    "collision": "#111827",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Plot success scatter and rolling success rate by episode order."
    )
    parser.add_argument(
        "--episode-log",
        default="logs/episode_log.csv",
        help="Episode CSV path. Default: logs/episode_log.csv",
    )
    parser.add_argument(
        "--phase",
        default=None,
        help="Phase name to plot. If omitted, the last phase in the log is used.",
    )
    parser.add_argument(
        "--output-dir",
        default="logs/analysis",
        help="Directory for PNG and CSV outputs.",
    )
    parser.add_argument(
        "--rolling",
        default="50,100",
        help="Comma-separated rolling windows to draw. Default: 50,100",
    )
    parser.add_argument(
        "--offset-sequence",
        default=DEFAULT_OFFSET_SEQUENCE,
        help=(
            "Comma-separated scheduled offsets by episode order. "
            "Default matches balanced heading offsets: -1,1,-2,2,-3,3,-4,4,-5,5"
        ),
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=170,
        help="Output image DPI. Default: 170",
    )
    return parser.parse_args()


def parse_int_list(value):
    items = []
    for raw in str(value).split(","):
        raw = raw.strip()
        if raw:
            items.append(int(raw))
    if not items:
        raise ValueError("List argument cannot be empty.")
    return items


def slugify(value):
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_")
    return slug or "phase"


def load_phase_rows(path, phase_name):
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"No rows in {path}")

    if phase_name is None:
        phases = df["phase_name"].dropna()
        if phases.empty:
            raise ValueError("episode_log.csv has no phase_name values.")
        phase_name = str(phases.iloc[-1])

    df = df[df["phase_name"].eq(phase_name)].copy()
    if df.empty:
        raise ValueError(f"No rows found for phase: {phase_name}")

    df["episode_id"] = pd.to_numeric(df["episode_id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["episode_id"]).copy()
    df["episode_id"] = df["episode_id"].astype(int)
    df = df.sort_values("episode_id").reset_index(drop=True)
    return phase_name, df


def add_success_metrics(df, rolling_windows, offset_sequence):
    df = df.copy()
    df["is_success"] = (df["done_reason"] == "success").astype(int)

    for window in rolling_windows:
        df[f"rolling_success_{window}"] = (
            df["is_success"].rolling(window, min_periods=1).mean()
        )

    df["offset_est"] = [
        offset_sequence[(int(ep_id) - 1) % len(offset_sequence)]
        for ep_id in df["episode_id"]
    ]
    return df


def plot(df, phase_name, rolling_windows, out_path, dpi):
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(15, 8.5),
        sharex=True,
        gridspec_kw={"height_ratios": [2.1, 1.35]},
    )

    rng = np.random.default_rng(7)
    ax = axes[0]
    for reason, part in df.groupby("done_reason"):
        y = part["is_success"].astype(float).to_numpy() + rng.normal(0, 0.025, len(part))
        ax.scatter(
            part["episode_id"],
            y,
            s=30 if reason == "success" else 18,
            c=TERMINAL_COLORS.get(reason, "#94a3b8"),
            alpha=0.90 if reason == "success" else 0.35,
            label=reason,
            edgecolors="none",
        )

    ax2 = ax.twinx()
    rolling_colors = ["#0f766e", "#134e4a", "#2563eb", "#7c3aed"]
    rolling_styles = ["-", "--", "-.", ":"]
    for i, window in enumerate(rolling_windows):
        ax2.plot(
            df["episode_id"],
            df[f"rolling_success_{window}"],
            color=rolling_colors[i % len(rolling_colors)],
            linestyle=rolling_styles[i % len(rolling_styles)],
            linewidth=2.2 if i == 0 else 1.6,
            label=f"rolling success {window}",
        )

    ax.set_yticks([0, 1])
    ax.set_yticklabels(["not success", "success"])
    ax.set_ylim(-0.17, 1.17)
    ax.set_ylabel("Terminal result")
    ax.set_title(f"{phase_name} - Success Scatter by Episode Order")
    ax.grid(True, axis="both", alpha=0.22)

    ax2.set_ylim(-0.02, 1.02)
    ax2.set_ylabel("Moving success rate")

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", ncol=4, fontsize=9, frameon=True)

    axb = axes[1]
    non = df[df["done_reason"] != "success"]
    suc = df[df["done_reason"] == "success"]
    axb.scatter(
        non["episode_id"],
        non["offset_est"],
        s=16,
        c="#94a3b8",
        alpha=0.35,
        label="not success",
    )
    axb.scatter(
        suc["episode_id"],
        suc["offset_est"],
        s=30,
        c="#1f9d55",
        alpha=0.9,
        label="success",
    )
    axb.axhline(0, color="#111827", linewidth=0.8, alpha=0.4)
    axb.set_yticks(sorted(df["offset_est"].unique()))
    axb.set_ylabel("Estimated offset")
    axb.set_xlabel("Episode ID")
    axb.grid(True, axis="both", alpha=0.22)
    axb.legend(loc="upper left", fontsize=9)

    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def main():
    args = parse_args()
    episode_log = Path(args.episode_log)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rolling_windows = parse_int_list(args.rolling)
    offset_sequence = parse_int_list(args.offset_sequence)
    phase_name, df = load_phase_rows(episode_log, args.phase)
    df = add_success_metrics(df, rolling_windows, offset_sequence)

    slug = slugify(phase_name)
    png_path = output_dir / f"{slug}_success_scatter_by_episode.png"
    csv_path = output_dir / f"{slug}_success_scatter_by_episode.csv"

    plot(df, phase_name, rolling_windows, png_path, args.dpi)

    columns = [
        "timestamp",
        "episode_id",
        "phase_name",
        "done_reason",
        "is_success",
        "offset_est",
        "episode_return",
        "episode_len",
        "final_target_distance",
        "final_target_hit_trigger",
        "final_agl",
        "final_theta_deg",
        "final_beta_deg",
    ] + [f"rolling_success_{window}" for window in rolling_windows]
    existing_columns = [column for column in columns if column in df.columns]
    df[existing_columns].to_csv(csv_path, index=False)

    print(f"phase={phase_name}")
    print(f"episodes={len(df)}")
    print(f"successes={int(df['is_success'].sum())}")
    print(f"success_rate={float(df['is_success'].mean()):.3f}")
    for window in rolling_windows:
        tail = df.tail(window)
        print(f"last_{window}_success_rate={float(tail['is_success'].mean()):.3f}")
    print(f"wrote_png={png_path.resolve()}")
    print(f"wrote_csv={csv_path.resolve()}")


if __name__ == "__main__":
    main()
