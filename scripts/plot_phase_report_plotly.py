from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from plot_phase_report import (
    OUTCOME_COLORS,
    OUTCOME_ORDER,
    CLOCK_CHANNELS,
    load_clock_alignment_report,
    load_reset_points,
    load_terminal_success_points,
    make_bins,
    phase_counts,
    read_completed_episodes,
    slugify,
)


def rolling(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=1).mean() * 100.0


def write_html(fig: go.Figure, path: Path, title: str) -> None:
    fig.update_layout(
        title=title,
        template="plotly_white",
        hovermode="closest",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0.0},
        margin={"l": 60, "r": 40, "t": 80, "b": 60},
    )
    fig.write_html(path, include_plotlyjs=True, full_html=True)


def outcome_color(reason: str) -> str:
    return OUTCOME_COLORS.get(reason, OUTCOME_COLORS["other"])


def plot_success_rate(episodes: pd.DataFrame, path: Path, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=episodes["episode_index"],
            y=rolling(episodes["is_success"], 20),
            mode="lines",
            name="R20",
            line={"color": "#38bdf8", "width": 1.4},
            hovertemplate="Episode=%{x}<br>R20=%{y:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=episodes["episode_index"],
            y=rolling(episodes["is_success"], 50),
            mode="lines",
            name="R50",
            line={"color": "#2563eb", "width": 2.0},
            hovertemplate="Episode=%{x}<br>R50=%{y:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=episodes["episode_index"],
            y=rolling(episodes["is_success"], 100),
            mode="lines",
            name="R100",
            line={"color": "#111827", "width": 2.2},
            hovertemplate="Episode=%{x}<br>R100=%{y:.1f}%<extra></extra>",
        )
    )

    for idx, reason in enumerate([item for item in OUTCOME_ORDER if item != "success"]):
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["episode_index"],
                y=np.full(len(subset), -5.0 - 3.0 * idx),
                mode="markers",
                marker={"symbol": "line-ns", "size": 12, "color": outcome_color(reason), "line": {"width": 2}},
                name=f"{reason} marks",
                customdata=np.stack([subset["update_id"], subset["episode_id"], subset["episode_return"]], axis=-1),
                hovertemplate=(
                    "Episode=%{x}<br>Update=%{customdata[0]}<br>"
                    "Episode id=%{customdata[1]}<br>Return=%{customdata[2]:.2f}<extra>"
                    + reason
                    + "</extra>"
                ),
            )
        )

    fig.add_hline(y=90, line_dash="dash", line_color="#16a34a", annotation_text="90% reference")
    fig.add_hline(y=80, line_dash="dot", line_color="#f97316", annotation_text="80% reference")
    fig.update_yaxes(title_text="Success rate (%)", range=[-20, 104])
    fig.update_xaxes(title_text="Episode")
    write_html(fig, path, title)
    return fig


def plot_success_rug(episodes: pd.DataFrame, path: Path, title: str) -> go.Figure:
    fig = go.Figure()
    reasons = [reason for reason in OUTCOME_ORDER if reason in set(episodes["done_reason"])]
    reasons += sorted(set(episodes["done_reason"]) - set(reasons))
    y_map = {reason: idx for idx, reason in enumerate(reasons)}

    for reason in reasons:
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["episode_index"],
                y=np.full(len(subset), y_map[reason]),
                mode="markers",
                marker={
                    "symbol": "circle",
                    "size": 7 if reason == "success" else 10,
                    "color": outcome_color(reason),
                    "opacity": 0.70 if reason == "success" else 0.92,
                    "line": {"width": 0.5, "color": "#0f172a"},
                },
                name=f"{reason}: n={len(subset)}",
                customdata=np.stack(
                    [
                        subset["update_id"],
                        subset["episode_id"],
                        subset["episode_return"],
                        subset["start_distance"],
                        subset["final_distance"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "Episode=%{x}<br>Update=%{customdata[0]}<br>Episode id=%{customdata[1]}"
                    "<br>Return=%{customdata[2]:.2f}<br>Start distance=%{customdata[3]:.2f}m"
                    "<br>Final distance=%{customdata[4]:.2f}m<extra>"
                    + reason
                    + "</extra>"
                ),
            )
        )

    fig.update_yaxes(
        title_text="Outcome lane (not a metric)",
        tickmode="array",
        tickvals=list(y_map.values()),
        ticktext=list(y_map.keys()),
        range=[-0.6, len(y_map) - 0.4],
    )
    fig.update_xaxes(title_text="Episode")
    fig.update_layout(
        height=max(420, 80 * max(1, len(y_map))),
        annotations=[
            {
                "text": "Y axis is categorical only; lanes separate outcomes so dense success points do not hide failures.",
                "xref": "paper",
                "yref": "paper",
                "x": 1.0,
                "y": -0.16,
                "showarrow": False,
                "xanchor": "right",
                "font": {"size": 11, "color": "#475569"},
            }
        ],
    )
    write_html(fig, path, title)
    return fig


def radius_bins(episodes: pd.DataFrame, bins: np.ndarray) -> pd.DataFrame:
    rows = []
    work = episodes.copy()
    work["dist_bin"] = pd.cut(work["start_distance"], bins=bins, right=False, include_lowest=True)
    for dist_bin, group in work.groupby("dist_bin", observed=False):
        if group.empty:
            continue
        rows.append(
            {
                "left": float(dist_bin.left),
                "right": float(dist_bin.right),
                "mid": 0.5 * (float(dist_bin.left) + float(dist_bin.right)),
                "label": f"{dist_bin.left:.0f}-{dist_bin.right:.0f}",
                "n": int(len(group)),
                "success": int((group["done_reason"] == "success").sum()),
                "near_miss": int((group["done_reason"] == "near_miss").sum()),
                "low_agl": int((group["done_reason"] == "low_agl").sum()),
                "wrong_way": int((group["done_reason"] == "wrong_way").sum()),
                "success_rate": 100.0 * float(group["is_success"].mean()),
            }
        )
    return pd.DataFrame(rows)


def plot_radius_distribution(episodes: pd.DataFrame, bins: np.ndarray, path: Path, title: str) -> go.Figure:
    fig = go.Figure()
    for reason in OUTCOME_ORDER + sorted(set(episodes["done_reason"]) - set(OUTCOME_ORDER)):
        subset = episodes[episodes["done_reason"] == reason]
        if subset.empty:
            continue
        fig.add_trace(
            go.Histogram(
                x=subset["start_distance"],
                xbins={"start": float(bins[0]), "end": float(bins[-1]), "size": float(bins[1] - bins[0])},
                name=f"{reason} n={len(subset)}",
                marker_color=outcome_color(reason),
                opacity=0.88,
                hovertemplate="Start distance bin=%{x}<br>Count=%{y}<extra>" + reason + "</extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Start distance (m)")
    fig.update_yaxes(title_text="Episode count")
    write_html(fig, path, title)
    return fig


def plot_radius_phase_plan(
    bin_df: pd.DataFrame,
    path: Path,
    title: str,
    radius_min: float | None,
    radius_max: float | None,
    phase_label: str,
) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.20,
        row_heights=[0.55, 0.45],
        subplot_titles=("Success rate by start-distance bin", "Phase / radius-bin map"),
    )

    text = [
        f"{row.success_rate:.1f}%<br>n={int(row.n)}<br>S={int(row.success)} NM={int(row.near_miss)}<br>WW={int(row.wrong_way)} LA={int(row.low_agl)}"
        for row in bin_df.itertuples()
    ]
    fig.add_trace(
        go.Bar(
            x=bin_df["mid"],
            y=bin_df["success_rate"] / 100.0,
            width=(bin_df["right"].iloc[0] - bin_df["left"].iloc[0]) * 0.84 if len(bin_df) else 4.0,
            marker_color="#4f7ead",
            text=text,
            textposition="outside",
            name="Success rate",
            customdata=np.stack(
                [
                    bin_df["n"],
                    bin_df["success"],
                    bin_df["near_miss"],
                    bin_df["wrong_way"],
                    bin_df["low_agl"],
                    bin_df["success_rate"],
                ],
                axis=-1,
            )
            if len(bin_df)
            else None,
            hovertemplate=(
                "Bin center=%{x:.1f}m<br>Success rate=%{customdata[5]:.1f}%"
                "<br>n=%{customdata[0]}<br>S=%{customdata[1]} NM=%{customdata[2]}"
                "<br>WW=%{customdata[3]} LA=%{customdata[4]}<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(title_text="Success Rate", range=[0, 1.12], row=1, col=1)

    if radius_min is not None and radius_max is not None:
        configured_left = float(min(radius_min, radius_max))
        configured_right = float(max(radius_min, radius_max))
        fig.add_shape(
            type="rect",
            x0=configured_left,
            x1=configured_right,
            y0=2.76,
            y1=3.34,
            fillcolor="#f9c58d",
            opacity=0.78,
            line={"color": "#d97706", "width": 1},
            row=2,
            col=1,
        )
        fig.add_annotation(
            x=0.5 * (configured_left + configured_right),
            y=3.05,
            xref="x2",
            yref="y2",
            text=f"{phase_label}<br>configured {configured_left:.0f}-{configured_right:.0f}m",
            showarrow=False,
            font={"color": "#92400e", "size": 12},
        )
        fig.add_vline(x=configured_left, line_dash="dash", line_color="#0f172a")
        fig.add_vline(x=configured_right, line_dash="dash", line_color="#0f172a")

    if len(bin_df):
        observed_left = float(bin_df["left"].min())
        observed_right = float(bin_df["right"].max())
        for idx, row in enumerate(bin_df.itertuples()):
            fig.add_shape(
                type="rect",
                x0=float(row.left),
                x1=float(row.right),
                y0=1.55,
                y1=2.15,
                fillcolor="#dbeafe" if idx % 2 == 0 else "#bfdbfe",
                opacity=0.78,
                line={"color": "#3b82f6", "width": 1},
                row=2,
                col=1,
            )
            fig.add_annotation(
                x=float(row.mid),
                y=1.85,
                xref="x2",
                yref="y2",
                text=f"{row.left:.0f}-{row.right:.0f}m<br>n={int(row.n)} S={int(row.success)}",
                showarrow=False,
                font={"color": "#1e3a8a", "size": 11},
            )
        fig.add_trace(
            go.Scatter(
                x=bin_df["mid"],
                y=np.full(len(bin_df), 0.55),
                mode="lines+markers+text",
                line={"color": "#111827", "width": 2},
                marker={"size": 9, "color": "#111827"},
                text=[f"SR={row.success_rate:.1f}%" for row in bin_df.itertuples()],
                textposition="top center",
                name="observed start_distance bins",
                customdata=np.stack(
                    [
                        bin_df["left"],
                        bin_df["right"],
                        bin_df["n"],
                        bin_df["success"],
                        bin_df["success_rate"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "Observed bin=%{customdata[0]:.0f}-%{customdata[1]:.0f}m"
                    "<br>Success rate=%{customdata[4]:.1f}%"
                    "<br>n=%{customdata[2]}<br>S=%{customdata[3]}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )

    fig.update_yaxes(
        visible=True,
        range=[-0.15, 3.65],
        tickmode="array",
        tickvals=[3.05, 1.85, 0.55],
        ticktext=["configured phase", "observed bins", "bin SR"],
        row=2,
        col=1,
    )
    fig.update_xaxes(title_text="Reset Radius / start_distance (m)", row=2, col=1)
    write_html(fig, path, title)
    return fig


def plot_reset_outcome_polar(
    episodes: pd.DataFrame,
    reset_points: pd.DataFrame | None,
    path: Path,
    title: str,
) -> go.Figure:
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
        source_note = "reset relative target vector"
    else:
        x = np.cos(np.linspace(0.0, 2.0 * np.pi, len(plot_df), endpoint=False)) * plot_df["start_distance"]
        z = np.sin(np.linspace(0.0, 2.0 * np.pi, len(plot_df), endpoint=False)) * plot_df["start_distance"]
        source_note = "synthetic angle fallback"

    plot_df["_theta_deg"] = np.degrees(np.arctan2(z, x))
    plot_df["_radius"] = np.sqrt(np.square(x) + np.square(z))

    fig = go.Figure()
    for reason in OUTCOME_ORDER + sorted(set(plot_df["done_reason"]) - set(OUTCOME_ORDER)):
        subset = plot_df[plot_df["done_reason"] == reason].dropna(subset=["_theta_deg", "_radius"])
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatterpolar(
                theta=subset["_theta_deg"],
                r=subset["_radius"],
                mode="markers",
                marker={"size": 7, "color": outcome_color(reason), "opacity": 0.72},
                name=f"{reason} n={len(subset)}",
                customdata=np.stack([subset["episode_id"], subset["update_id"], subset["start_distance"]], axis=-1),
                hovertemplate=(
                    "Episode id=%{customdata[0]}<br>Update=%{customdata[1]}"
                    "<br>Start distance=%{customdata[2]:.2f}m<br>Angle=%{theta:.1f} deg<extra>"
                    + reason
                    + "</extra>"
                ),
            )
        )
    fig.update_layout(polar={"radialaxis": {"title": "Start distance (m"}})
    write_html(fig, path, f"{title} | reset outcome polar ({source_note})")
    return fig


def plot_hit_location_polar(
    episodes: pd.DataFrame,
    terminal_points: pd.DataFrame | None,
    path: Path,
    title: str,
) -> go.Figure:
    if terminal_points is None or terminal_points.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No success hits in this phase window.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 14},
        )
        fig.update_layout(
            polar={
                "radialaxis": {"range": [0, 16], "title": "Hit distance from target (m)"},
                "angularaxis": {"direction": "clockwise", "rotation": 0},
            }
        )
        write_html(fig, path, title)
        return fig

    success_meta = episodes.loc[
        episodes["done_reason"] == "success",
        ["episode_segment", "episode_id", "episode_index", "update_id", "final_distance", "final_theta_deg"],
    ]
    hit_df = terminal_points.merge(success_meta, on=["episode_segment", "episode_id"], how="left", suffixes=("", "_episode"))

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
    else:
        x = -pd.to_numeric(hit_df["rel_pos_world_x"], errors="coerce")
        z = -pd.to_numeric(hit_df["rel_pos_world_z"], errors="coerce")

    hit_df["_theta_deg"] = np.degrees(np.arctan2(z, x))
    hit_df["_radius"] = np.sqrt(np.square(x) + np.square(z))
    hit_df = hit_df.dropna(subset=["_theta_deg", "_radius"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            theta=hit_df["_theta_deg"],
            r=hit_df["_radius"],
            mode="markers",
            marker={"size": 7, "color": "#2563eb", "opacity": 0.72},
            name=f"success hits n={len(hit_df)}",
            customdata=np.stack(
                [
                    hit_df["episode_id"],
                    hit_df["update_id"],
                    hit_df["_radius"],
                    hit_df["distance"],
                    hit_df["episode_index"],
                ],
                axis=-1,
            ),
            hovertemplate=(
                "Episode=%{customdata[4]}<br>Episode id=%{customdata[0]}<br>Update=%{customdata[1]}"
                "<br>Hit distance=%{customdata[2]:.2f}m<br>Logged distance=%{customdata[3]:.2f}m"
                "<br>Angle=%{theta:.1f} deg<extra></extra>"
            ),
        )
    )
    max_radius = max(16.0, float(hit_df["_radius"].max()) + 1.0)
    fig.update_layout(
        polar={
            "radialaxis": {"range": [0, max_radius], "title": "Hit distance from target (m)"},
            "angularaxis": {"direction": "clockwise", "rotation": 0},
        }
    )
    write_html(fig, path, title)
    return fig


def plot_clock_action_alignment(clock_report: pd.DataFrame | None, path: Path, title: str) -> go.Figure:
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.09,
        subplot_titles=(
            "Target/action clock-vector alignment",
            "Mean action output by clock channel",
            "Mean target direction by clock channel",
            "Clock reward terms and anti-pattern signals",
        ),
    )

    if clock_report is None or clock_report.empty:
        fig.add_annotation(
            text=(
                "No V9 clock columns were found in step_log.csv.<br>"
                "This graph will populate after V9 training writes clock state/action logs."
            ),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font={"size": 14},
        )
        write_html(fig, path, title)
        return fig

    x = clock_report["update_id"]
    fig.add_trace(
        go.Scatter(
            x=x,
            y=clock_report["clock_vector_cosine"],
            mode="lines",
            name="target/action vector cosine",
            line={"color": "#111827", "width": 2.2},
            hovertemplate="up=%{x}<br>cosine=%{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=clock_report["clock_dominant_match"],
            mode="lines",
            name="dominant channel match",
            line={"color": "#2563eb", "width": 2.0, "dash": "dot"},
            hovertemplate="up=%{x}<br>match=%{y:.3f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    fig.add_hline(y=0.0, line_color="#64748b", line_width=1, opacity=0.55, row=1, col=1)
    fig.add_hline(y=0.75, line_color="#16a34a", line_width=1, line_dash="dash", opacity=0.75, row=1, col=1)

    action_colors = {"12": "#16a34a", "6": "#ef4444", "3": "#2563eb", "9": "#f59e0b"}
    for channel in CLOCK_CHANNELS:
        col_name = f"clock_{channel}_cmd"
        fig.add_trace(
            go.Scatter(
                x=x,
                y=clock_report[col_name],
                mode="lines",
                name=col_name,
                line={"color": action_colors[channel], "width": 1.8},
                hovertemplate=f"up=%{{x}}<br>{col_name}=%{{y:.3f}}<extra></extra>",
            ),
            row=2,
            col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=clock_report["net_clock_cmd_mag"],
            mode="lines",
            name="net command magnitude",
            line={"color": "#0f172a", "width": 2.0, "dash": "dash"},
            hovertemplate="up=%{x}<br>net_cmd=%{y:.3f}<extra></extra>",
        ),
        row=2,
        col=1,
    )

    for channel in CLOCK_CHANNELS:
        col_name = f"target_clock_{channel}"
        fig.add_trace(
            go.Scatter(
                x=x,
                y=clock_report[col_name],
                mode="lines",
                name=col_name,
                line={"color": action_colors[channel], "width": 1.8},
                hovertemplate=f"up=%{{x}}<br>{col_name}=%{{y:.3f}}<extra></extra>",
            ),
            row=3,
            col=1,
        )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=clock_report["target_clock_mag"],
            mode="lines",
            name="target clock magnitude",
            line={"color": "#0f172a", "width": 2.0, "dash": "dash"},
            hovertemplate="up=%{x}<br>target_mag=%{y:.3f}<extra></extra>",
        ),
        row=3,
        col=1,
    )

    reward_specs = [
        ("reward_clock_action_alignment", "#16a34a", "solid"),
        ("reward_clock_wrong_channel", "#ef4444", "solid"),
        ("reward_clock_coactivation", "#f59e0b", "solid"),
        ("clock_opposite_cmd", "#7c3aed", "dash"),
        ("clock_coactivation", "#64748b", "dash"),
    ]
    for col_name, color, dash in reward_specs:
        if col_name not in clock_report.columns or clock_report[col_name].isna().all():
            continue
        fig.add_trace(
            go.Scatter(
                x=x,
                y=clock_report[col_name],
                mode="lines",
                name=col_name,
                line={"color": color, "width": 1.9, "dash": dash},
                hovertemplate=f"up=%{{x}}<br>{col_name}=%{{y:.4f}}<extra></extra>",
            ),
            row=4,
            col=1,
        )

    fig.update_yaxes(title_text="alignment", range=[-1.05, 1.05], row=1, col=1)
    fig.update_yaxes(title_text="command", row=2, col=1)
    fig.update_yaxes(title_text="target", row=3, col=1)
    fig.update_yaxes(title_text="reward", row=4, col=1)
    fig.update_xaxes(title_text="Update", row=4, col=1)
    fig.update_layout(
        height=980,
        annotations=list(fig.layout.annotations)
        + [
            {
                "text": (
                    "Cosine near +1 means the net action points toward the target clock channel; "
                    "below 0 means the action points away."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 1.0,
                "y": -0.06,
                "showarrow": False,
                "xanchor": "right",
                "font": {"size": 11, "color": "#475569"},
            }
        ],
    )
    write_html(fig, path, title)
    return fig


def write_dashboard(figs: list[tuple[str, go.Figure]], path: Path, title: str) -> None:
    body = [f"<html><head><meta charset='utf-8'><title>{title}</title></head><body>"]
    body.append(f"<h1>{title}</h1>")
    for idx, (name, fig) in enumerate(figs):
        body.append(f"<h2>{name}</h2>")
        body.append(pio.to_html(fig, include_plotlyjs=True if idx == 0 else False, full_html=False))
    body.append("</body></html>")
    path.write_text("\n".join(body), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate interactive Plotly phase report graphs.")
    parser.add_argument("--logs-dir", default="logs")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--phase-slug", required=True)
    parser.add_argument("--phase-label", required=True)
    parser.add_argument("--start-update", type=int, default=None)
    parser.add_argument("--end-update", type=int, default=None)
    parser.add_argument("--radius-min", type=float, default=None)
    parser.add_argument("--radius-max", type=float, default=None)
    parser.add_argument("--bin-width", type=float, default=5.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logs_dir = Path(args.logs_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    episodes, last_completed_update = read_completed_episodes(logs_dir, args.start_update, args.end_update)
    bins = make_bins(episodes, args.radius_min, args.radius_max, args.bin_width)
    bin_df = radius_bins(episodes, bins)
    reset_points = load_reset_points(logs_dir, episodes, last_completed_update)
    terminal_points = load_terminal_success_points(logs_dir, episodes, last_completed_update)
    clock_report = load_clock_alignment_report(logs_dir, args.start_update, last_completed_update)

    prefix = slugify(args.phase_slug)
    title = f"{args.phase_label} | up {int(episodes['update_id'].min())}-{last_completed_update}"
    outputs = {
        "success_rate": out_dir / f"{prefix}_plotly_success_rate.html",
        "success_rug": out_dir / f"{prefix}_plotly_success_rug.html",
        "reset_outcome_polar": out_dir / f"{prefix}_plotly_reset_outcome_polar.html",
        "hit_location_polar": out_dir / f"{prefix}_plotly_hit_location_polar.html",
        "reset_radius_distribution": out_dir / f"{prefix}_plotly_reset_radius_distribution.html",
        "reset_radius_phase_plan": out_dir / f"{prefix}_plotly_reset_radius_phase_plan.html",
        "clock_action_alignment": out_dir / f"{prefix}_plotly_clock_action_alignment.html",
        "dashboard": out_dir / f"{prefix}_plotly_dashboard.html",
    }

    figs = [
        ("Success Rate", plot_success_rate(episodes, outputs["success_rate"], f"{title} | success rate")),
        ("Success Rug", plot_success_rug(episodes, outputs["success_rug"], f"{title} | outcome density")),
        (
            "Reset Radius Distribution",
            plot_radius_distribution(episodes, bins, outputs["reset_radius_distribution"], f"{title} | radius distribution"),
        ),
        (
            "Reset Radius Phase Plan",
            plot_radius_phase_plan(
                bin_df,
                outputs["reset_radius_phase_plan"],
                f"{title} | reset radius phase plan",
                args.radius_min,
                args.radius_max,
                args.phase_label,
            ),
        ),
        (
            "Reset Outcome Polar",
            plot_reset_outcome_polar(episodes, reset_points, outputs["reset_outcome_polar"], f"{title} | reset outcome polar"),
        ),
        (
            "Hit Location Polar",
            plot_hit_location_polar(episodes, terminal_points, outputs["hit_location_polar"], f"{title} | hit location polar"),
        ),
        (
            "Clock Action Alignment",
            plot_clock_action_alignment(
                clock_report,
                outputs["clock_action_alignment"],
                f"{title} | clock action alignment",
            ),
        ),
    ]
    write_dashboard(figs, outputs["dashboard"], f"{title} | Plotly dashboard")

    print(f"updates={int(episodes['update_id'].min())}-{last_completed_update}")
    print(f"episodes={len(episodes)}")
    print(f"success_rate={100.0 * episodes['is_success'].mean():.3f}%")
    print(f"done_counts={phase_counts(episodes)}")
    print(f"output_dir={out_dir}")
    for path in outputs.values():
        print(path)


if __name__ == "__main__":
    main()
