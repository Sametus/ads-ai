"""SAC/V15 canlı training logları için sade grafik raporu üretir.

Bu script PPO dönemindeki faz grafiklerinin SAC loglarına uyarlanmış halidir.
Training devam ederken de çalışabilmesi için CSV okuma tarafında hatalı/yarım
satırları atlar ve step logunu örnekleyerek belleği korur.
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Terminal sebepleri için sabit renkler: aynı reason her grafikte aynı renkte görünür.
OUTCOME_COLORS = {
    "success": "#1f9d55",
    "low_agl": "#d97706",
    "high_altitude": "#7c3aed",
    "wrong_way": "#dc2626",
    "collision": "#111827",
    "timeout": "#2563eb",
    "near_miss": "#0891b2",
    "unknown": "#6b7280",
}

OUTCOME_ORDER = [
    "success",
    "low_agl",
    "high_altitude",
    "wrong_way",
    "collision",
    "timeout",
    "near_miss",
    "unknown",
]

OUTCOME_SHORT = {
    "success": "S",
    "low_agl": "LA",
    "high_altitude": "HA",
    "wrong_way": "WW",
    "collision": "C",
    "timeout": "TO",
    "near_miss": "NM",
    "unknown": "?",
}


def slugify(text: str) -> str:
    """Dosya adı için güvenli kısa isim üretir."""
    text = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(text).strip())
    return text.strip("_") or "sac_report"


def color_for(reason: str) -> str:
    """Bilinmeyen terminal sebepleri için nötr renk döndürür."""
    return OUTCOME_COLORS.get(str(reason), OUTCOME_COLORS["unknown"])


def read_csv_safe(path: Path, usecols: Iterable[str] | None = None) -> pd.DataFrame:
    """Training yazarken oluşan yarım CSV satırlarını atlayarak okur."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()

    if usecols is None:
        usecols_arg = None
    else:
        wanted = set(usecols)
        usecols_arg = lambda col: col in wanted

    try:
        return pd.read_csv(path, usecols=usecols_arg, on_bad_lines="skip", low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def ensure_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Sayısal olması gereken kolonları güvenli şekilde numeric tipe çevirir."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def filter_phase(df: pd.DataFrame, phase_contains: str) -> pd.DataFrame:
    """İstenen faz/sürüm metnini içeren satırları seçer."""
    if df.empty or not phase_contains or "phase_name" not in df.columns:
        return df
    mask = df["phase_name"].astype(str).str.contains(phase_contains, na=False)
    return df.loc[mask].copy()


def load_episodes(logs_dir: Path, phase_contains: str) -> pd.DataFrame:
    """Episode özet logunu okur ve grafik için temel kolonları hazırlar."""
    episode_path = logs_dir / "episode_log.csv"
    episodes = read_csv_safe(episode_path)
    episodes = filter_phase(episodes, phase_contains)

    numeric_cols = [
        "episode_id",
        "update_id",
        "max_step",
        "episode_return",
        "episode_len",
        "start_distance",
        "final_distance",
        "start_agl",
        "final_agl",
        "final_closing_speed",
        "final_theta_deg",
        "final_alpha_deg",
        "final_beta_deg",
        "final_alignment",
        "final_forward_up_dot",
        "final_grounded_flag",
        "final_ang_vel_mag",
    ]
    episodes = ensure_numeric(episodes, numeric_cols)

    if "done_reason" not in episodes.columns:
        episodes["done_reason"] = "unknown"
    episodes["done_reason"] = episodes["done_reason"].fillna("unknown").astype(str)
    episodes["success_flag"] = episodes["done_reason"].eq("success")
    episodes = episodes.sort_values("episode_id").reset_index(drop=True)
    return episodes


def load_updates(logs_dir: Path) -> pd.DataFrame:
    """SAC optimizer logunu okur; eski loglarda alpha icin clip_frac fallback kullanir."""
    update_path = logs_dir / "update_log.csv"
    updates = read_csv_safe(update_path)
    numeric_cols = [
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
    updates = ensure_numeric(updates, numeric_cols)

    if "alpha" not in updates.columns and "clip_frac" in updates.columns:
        updates["alpha"] = updates["clip_frac"]
    elif "alpha" in updates.columns and "clip_frac" in updates.columns:
        updates["alpha"] = updates["alpha"].fillna(updates["clip_frac"])

    if "update_id" in updates.columns:
        updates = updates.sort_values("update_id").reset_index(drop=True)
    return updates


def iter_step_chunks(logs_dir: Path, phase_contains: str, wanted_cols: Iterable[str], chunksize: int):
    """Büyük step logunu parça parça okur; canlı training sırasında RAM'i korur."""
    step_path = logs_dir / "step_log.csv"
    if not step_path.exists() or step_path.stat().st_size == 0:
        return

    wanted = set(wanted_cols)
    usecols_arg = lambda col: col in wanted

    try:
        reader = pd.read_csv(
            step_path,
            usecols=usecols_arg,
            chunksize=chunksize,
            on_bad_lines="skip",
            low_memory=False,
        )
        for chunk in reader:
            chunk = filter_phase(chunk, phase_contains)
            if not chunk.empty:
                yield chunk
    except pd.errors.EmptyDataError:
        return


def load_step_rows(
    logs_dir: Path,
    phase_contains: str,
    sample_stride: int,
    chunksize: int,
) -> pd.DataFrame:
    """Reset, terminal ve örneklenmiş step satırlarını tek tabloda toplar."""
    wanted_cols = [
        "episode_id",
        "step_id",
        "phase_name",
        "done",
        "done_reason",
        "success",
        "distance",
        "delta_distance",
        "closing_speed",
        "theta_deg",
        "agl",
        "grounded_flag",
        "action_norm_0",
        "action_norm_1",
        "action_norm_2",
        "direct_accel_cmd_right",
        "direct_accel_cmd_up",
        "direct_accel_cmd_forward",
        "rocket_pos_world_x",
        "rocket_pos_world_z",
        "rocket_point_pos_world_x",
        "rocket_point_pos_world_z",
        "target_pos_world_x",
        "target_pos_world_z",
        "target_point_pos_world_x",
        "target_point_pos_world_z",
    ]

    pieces: list[pd.DataFrame] = []
    sample_stride = max(1, int(sample_stride))

    for chunk in iter_step_chunks(logs_dir, phase_contains, wanted_cols, chunksize):
        numeric_cols = [
            "episode_id",
            "step_id",
            "done",
            "success",
            "distance",
            "delta_distance",
            "closing_speed",
            "theta_deg",
            "agl",
            "grounded_flag",
            "action_norm_0",
            "action_norm_1",
            "action_norm_2",
            "direct_accel_cmd_right",
            "direct_accel_cmd_up",
            "direct_accel_cmd_forward",
            "rocket_pos_world_x",
            "rocket_pos_world_z",
            "rocket_point_pos_world_x",
            "rocket_point_pos_world_z",
            "target_pos_world_x",
            "target_pos_world_z",
            "target_point_pos_world_x",
            "target_point_pos_world_z",
        ]
        chunk = ensure_numeric(chunk, numeric_cols)

        reset_mask = chunk.get("step_id", pd.Series(False, index=chunk.index)).eq(1)
        done_mask = chunk.get("done", pd.Series(0, index=chunk.index)).fillna(0).astype(float).gt(0)
        success_mask = chunk.get("success", pd.Series(0, index=chunk.index)).fillna(0).astype(float).gt(0)
        sample = chunk.iloc[::sample_stride].copy()
        important = chunk.loc[reset_mask | done_mask | success_mask].copy()
        pieces.extend([sample, important])

    if not pieces:
        return pd.DataFrame()

    steps = pd.concat(pieces, ignore_index=True)
    if {"episode_id", "step_id"}.issubset(steps.columns):
        steps = steps.drop_duplicates(["episode_id", "step_id"], keep="last")
    steps = steps.sort_values(["episode_id", "step_id"], na_position="last").reset_index(drop=True)
    return steps


def save_empty(path: Path, title: str, message: str) -> None:
    """Veri yokken boş ama açıklayıcı bir grafik üretir."""
    fig, ax = plt.subplots(figsize=(11, 5), dpi=140)
    ax.set_title(title)
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_summary(episodes: pd.DataFrame, out_path: Path) -> None:
    """Genel gidişatı hızlı okumak için dört küçük özet panel çizer."""
    if episodes.empty:
        save_empty(out_path, "SAC Summary", "episode_log.csv içinde okunabilir veri yok.")
        return

    x = episodes["episode_id"].to_numpy()
    window = min(100, max(5, len(episodes) // 5))
    rolling_success = episodes["success_flag"].rolling(window, min_periods=1).mean() * 100.0
    rolling_return = episodes["episode_return"].rolling(window, min_periods=1).mean()

    fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=140)
    fig.suptitle("SAC Live Training Summary", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(x, rolling_success, color="#1f9d55", linewidth=2)
    ax.set_title(f"Rolling Success Rate ({window} episode)")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Success %")
    ax.grid(alpha=0.25)

    ax = axes[0, 1]
    counts = episodes["done_reason"].value_counts()
    order = [r for r in OUTCOME_ORDER if r in counts.index] + [r for r in counts.index if r not in OUTCOME_ORDER]
    ax.bar(order, counts.loc[order], color=[color_for(r) for r in order])
    ax.set_title("Terminal Reason Distribution")
    ax.set_ylabel("Episode count")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)

    ax = axes[1, 0]
    ax.plot(x, rolling_return, color="#2563eb", linewidth=1.8)
    ax.set_title(f"Rolling Episode Return ({window} episode)")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Return")
    ax.grid(alpha=0.25)

    ax = axes[1, 1]
    ax.scatter(
        episodes["start_distance"],
        episodes["final_distance"],
        s=20,
        alpha=0.75,
        c=[color_for(r) for r in episodes["done_reason"]],
        edgecolors="none",
    )
    ax.axhline(10.0, color="#1f9d55", linestyle="--", linewidth=1, label="10 m success band")
    ax.set_title("Start Distance -> Final Distance")
    ax.set_xlabel("Start distance (m)")
    ax.set_ylabel("Final distance (m)")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path)
    plt.close(fig)


def plot_success_rug(episodes: pd.DataFrame, out_path: Path) -> None:
    """Success episode yoğunluğunu y ekseni bilgisi olmadan gösterir."""
    if episodes.empty:
        save_empty(out_path, "Success Rug", "Episode verisi yok.")
        return

    success_rows = episodes.loc[episodes["success_flag"]].copy()
    fig, ax = plt.subplots(figsize=(14, 3.2), dpi=140)
    ax.set_title("Success Episode Density")
    ax.set_xlabel("Episode")
    ax.set_yticks([])
    ax.set_ylim(-1, 1)
    ax.grid(axis="x", alpha=0.2)

    if success_rows.empty:
        ax.text(0.5, 0.5, "Bu aralıkta success yok.", ha="center", va="center", transform=ax.transAxes)
    else:
        ax.scatter(
            success_rows["episode_id"],
            np.zeros(len(success_rows)),
            marker="|",
            s=420,
            color=OUTCOME_COLORS["success"],
            linewidths=1.8,
        )
        ax.text(
            0.01,
            0.88,
            f"success={len(success_rows)} / episodes={len(episodes)}",
            transform=ax.transAxes,
            fontsize=9,
            color="#1f2937",
        )

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_radius_plan(episodes: pd.DataFrame, out_path: Path, bin_size: float) -> None:
    """Radius bazlı outcome dağılımını ve faz bandını standart formatta çizer."""
    if episodes.empty or "start_distance" not in episodes.columns:
        save_empty(out_path, "Radius Phase Plan", "start_distance episode verisi yok.")
        return

    data = episodes.dropna(subset=["start_distance"]).copy()
    if data.empty:
        save_empty(out_path, "Radius Phase Plan", "start_distance değerleri boş.")
        return

    min_dist = math.floor(data["start_distance"].min() / bin_size) * bin_size
    max_dist = math.ceil(data["start_distance"].max() / bin_size) * bin_size
    if min_dist == max_dist:
        max_dist = min_dist + bin_size
    bins = np.arange(min_dist, max_dist + bin_size, bin_size)
    labels = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
    data["radius_bin"] = pd.cut(data["start_distance"], bins=bins, labels=labels, include_lowest=True)

    counts = data.groupby(["radius_bin", "done_reason"], observed=False).size().unstack(fill_value=0)
    counts = counts.reindex(labels, fill_value=0)
    ordered_reasons = [r for r in OUTCOME_ORDER if r in counts.columns] + [
        r for r in counts.columns if r not in OUTCOME_ORDER
    ]

    success_rate = data.groupby("radius_bin", observed=False)["success_flag"].mean().reindex(labels).fillna(0) * 100.0
    bin_totals = counts.sum(axis=1)

    phase_stats = []
    if "phase_name" in data.columns:
        for phase_name, group in data.groupby("phase_name", sort=False):
            phase_stats.append(
                {
                    "phase_name": str(phase_name),
                    "min_radius": float(group["start_distance"].min()),
                    "max_radius": float(group["start_distance"].max()),
                    "n": int(len(group)),
                    "success_rate": float(group["success_flag"].mean() * 100.0),
                }
            )
    else:
        phase_stats.append(
            {
                "phase_name": "current_phase",
                "min_radius": float(data["start_distance"].min()),
                "max_radius": float(data["start_distance"].max()),
                "n": int(len(data)),
                "success_rate": float(data["success_flag"].mean() * 100.0),
            }
        )

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(15, 8),
        dpi=140,
        gridspec_kw={"height_ratios": [3.0, max(1.2, 0.55 * len(phase_stats))]},
    )
    fig.suptitle("Reset Radius Outcome + Phase Band", fontsize=14, fontweight="bold")

    x = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    for reason in ordered_reasons:
        values = counts[reason].to_numpy() if reason in counts.columns else np.zeros(len(labels))
        ax_top.bar(x, values, bottom=bottom, color=color_for(reason), label=reason, width=0.82)
        bottom += values

    ax_top.set_ylabel("Episode count")
    ax_top.set_xticks(x)
    ax_top.set_xticklabels(labels, rotation=30, ha="right")
    ax_top.grid(axis="y", alpha=0.25)

    ax_rate = ax_top.twinx()
    ax_rate.plot(x, success_rate.to_numpy(), color="#0f172a", marker="o", linewidth=2, label="Success %")
    ax_rate.set_ylabel("Success %")
    ax_rate.set_ylim(0, max(100, float(success_rate.max()) + 10))

    for idx, (rate, total) in enumerate(zip(success_rate.to_numpy(), bin_totals.to_numpy())):
        if total > 0:
            ax_rate.text(idx, rate + 2, f"{rate:.1f}%", ha="center", va="bottom", fontsize=8, color="#0f172a")

    legend_note = "n=episode sayısı, S=success, LA=low_agl, HA=high_altitude, WW=wrong_way, C=collision, TO=timeout"
    ax_top.text(0.01, 0.96, legend_note, transform=ax_top.transAxes, va="top", fontsize=8, color="#374151")
    ax_top.legend(loc="upper right", fontsize=8, ncol=2)

    ax_bottom.set_title("Observed Version/Phase Radius Bands")
    ax_bottom.set_xlabel("Start distance (m)")
    ax_bottom.set_yticks(range(len(phase_stats)))
    ax_bottom.set_yticklabels([p["phase_name"] for p in phase_stats], fontsize=8)
    ax_bottom.set_xlim(min_dist, max_dist)
    ax_bottom.grid(axis="x", alpha=0.25)

    for row, stat in enumerate(phase_stats):
        width = max(0.01, stat["max_radius"] - stat["min_radius"])
        ax_bottom.barh(
            row,
            width,
            left=stat["min_radius"],
            height=0.45,
            color="#bfdbfe",
            edgecolor="#1d4ed8",
        )
        text = f"n={stat['n']} | S={stat['success_rate']:.1f}%"
        ax_bottom.text(
            stat["min_radius"] + width / 2,
            row,
            text,
            ha="center",
            va="center",
            fontsize=8,
            color="#0f172a",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.75},
        )

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def choose_position_columns(df: pd.DataFrame, prefix: str) -> tuple[str | None, str | None]:
    """Point transform varsa onu, yoksa ana transform pozisyonunu seçer."""
    point_x = f"{prefix}_point_pos_world_x"
    point_z = f"{prefix}_point_pos_world_z"
    main_x = f"{prefix}_pos_world_x"
    main_z = f"{prefix}_pos_world_z"
    if point_x in df.columns and point_z in df.columns:
        return point_x, point_z
    if main_x in df.columns and main_z in df.columns:
        return main_x, main_z
    return None, None


def plot_reset_map(episodes: pd.DataFrame, steps: pd.DataFrame, out_path: Path) -> None:
    """Reset anında hedefin x/z düzlemindeki dağılımını outcome rengiyle çizer."""
    if episodes.empty or steps.empty or "step_id" not in steps.columns:
        save_empty(out_path, "Reset Map", "Reset step verisi yok.")
        return

    reset_rows = steps.loc[steps["step_id"].eq(1)].copy()
    target_x, target_z = choose_position_columns(reset_rows, "target")
    if reset_rows.empty or target_x is None or target_z is None:
        save_empty(out_path, "Reset Map", "Target reset pozisyon kolonları bulunamadı.")
        return

    merged = reset_rows.merge(
        episodes[["episode_id", "done_reason", "start_distance"]],
        on="episode_id",
        how="left",
        suffixes=("", "_episode"),
    )

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    ax.set_title("Reset Target Positions by Episode Outcome")
    ax.scatter(0, 0, marker="^", s=90, color="#0f172a", label="Rocket launch")

    for reason in OUTCOME_ORDER:
        group = merged.loc[merged["done_reason"].eq(reason)]
        if not group.empty:
            ax.scatter(group[target_x], group[target_z], s=24, alpha=0.75, color=color_for(reason), label=reason)

    if "start_distance" in merged.columns and merged["start_distance"].notna().any():
        for radius, style in [
            (merged["start_distance"].min(), "--"),
            (merged["start_distance"].max(), "-"),
        ]:
            circle = plt.Circle((0, 0), float(radius), fill=False, linestyle=style, color="#64748b", alpha=0.85)
            ax.add_patch(circle)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("World X (m)")
    ax.set_ylabel("World Z (m)")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_action_diagnostics(steps: pd.DataFrame, out_path: Path) -> None:
    """SAC actionlarının tek yöne çöküp çökmediğini hızlı okumak için çizer."""
    if steps.empty:
        save_empty(out_path, "Action Diagnostics", "Step örnek verisi yok.")
        return

    data = steps.copy().reset_index(drop=True)
    data["sample_index"] = np.arange(len(data))

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), dpi=140, sharex=True)
    fig.suptitle("SAC Action / Flight Diagnostics", fontsize=14, fontweight="bold")

    ax = axes[0]
    action_cols = [c for c in ["action_norm_0", "action_norm_1", "action_norm_2"] if c in data.columns]
    for col in action_cols:
        ax.plot(data["sample_index"], data[col].rolling(40, min_periods=1).mean(), linewidth=1.4, label=col)
    if not action_cols:
        ax.text(0.5, 0.5, "action_norm kolonları yok.", transform=ax.transAxes, ha="center", va="center")
    ax.set_ylabel("Action")
    ax.set_title("Rolling action outputs")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)

    ax = axes[1]
    accel_cols = [c for c in ["direct_accel_cmd_right", "direct_accel_cmd_up", "direct_accel_cmd_forward"] if c in data.columns]
    for col in accel_cols:
        ax.plot(data["sample_index"], data[col].rolling(40, min_periods=1).mean(), linewidth=1.4, label=col)
    if not accel_cols:
        ax.text(0.5, 0.5, "direct_accel_cmd kolonları yok.", transform=ax.transAxes, ha="center", va="center")
    ax.set_ylabel("Accel cmd")
    ax.set_title("Rolling direct acceleration commands")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)

    ax = axes[2]
    if "agl" in data.columns:
        ax.plot(data["sample_index"], data["agl"].rolling(40, min_periods=1).mean(), color="#d97706", label="AGL")
        ax.axhline(0.60, color="#dc2626", linestyle="--", linewidth=1, label="low_agl threshold")
    if "distance" in data.columns:
        ax_dist = ax.twinx()
        ax_dist.plot(
            data["sample_index"],
            data["distance"].rolling(40, min_periods=1).mean(),
            color="#2563eb",
            alpha=0.7,
            label="distance",
        )
        ax_dist.set_ylabel("Distance")
    ax.set_xlabel("Sampled step index")
    ax.set_ylabel("AGL")
    ax.set_title("Altitude and distance trend")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def plot_hit_positions(episodes: pd.DataFrame, steps: pd.DataFrame, out_path: Path) -> None:
    """Success olduğunda hedefin vurulduğu x/z konumlarını gösterir."""
    if episodes.empty or steps.empty:
        save_empty(out_path, "Hit Positions", "Success veya step verisi yok.")
        return

    success_eps = set(episodes.loc[episodes["success_flag"], "episode_id"].dropna().astype(int).tolist())
    if not success_eps:
        save_empty(out_path, "Hit Positions", "Bu faz aralığında success yok.")
        return

    success_steps = steps.loc[
        steps["episode_id"].isin(success_eps)
        & (
            steps.get("success", pd.Series(0, index=steps.index)).fillna(0).astype(float).gt(0)
            | steps.get("done_reason", pd.Series("", index=steps.index)).astype(str).eq("success")
        )
    ].copy()

    target_x, target_z = choose_position_columns(success_steps, "target")
    rocket_x, rocket_z = choose_position_columns(success_steps, "rocket")
    if success_steps.empty or target_x is None or target_z is None:
        save_empty(out_path, "Hit Positions", "Success terminal pozisyon kolonları bulunamadı.")
        return

    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    ax.set_title("Target Hit Positions")
    ax.scatter(0, 0, marker="^", s=90, color="#0f172a", label="Rocket launch")
    ax.scatter(success_steps[target_x], success_steps[target_z], s=42, color="#1f9d55", label="Target hit point")
    if rocket_x and rocket_z:
        ax.scatter(
            success_steps[rocket_x],
            success_steps[rocket_z],
            s=22,
            color="#111827",
            alpha=0.65,
            label="Rocket at success",
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("World X (m)")
    ax.set_ylabel("World Z (m)")
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_update_diagnostics(updates: pd.DataFrame, out_path: Path) -> None:
    """SAC'a ozgu optimizer, critic, entropy ve alpha sinyallerini cizer."""
    if updates.empty or "update_id" not in updates.columns:
        save_empty(out_path, "SAC Update Diagnostics", "update_log.csv icinde okunabilir veri yok.")
        return

    x = updates["update_id"]
    fig, axes = plt.subplots(2, 2, figsize=(14, 8), dpi=140)
    fig.suptitle("SAC Update Diagnostics", fontsize=14, fontweight="bold")

    ax = axes[0, 0]
    for col, label, color in [
        ("loss", "total", "#111827"),
        ("policy_loss", "actor", "#2563eb"),
        ("value_loss", "critic total", "#dc2626"),
    ]:
        if col in updates.columns and updates[col].notna().any():
            ax.plot(x, updates[col], label=label, linewidth=1.4, color=color)
    ax.set_title("Loss Components")
    ax.set_xlabel("Global step")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    ax = axes[0, 1]
    if "entropy" in updates.columns and updates["entropy"].notna().any():
        ax.plot(x, updates["entropy"], color="#7c3aed", linewidth=1.5, label="entropy")
    ax.set_title("Entropy / Alpha")
    ax.set_xlabel("Global step")
    ax.set_ylabel("Entropy")
    ax.grid(alpha=0.25)
    ax_alpha = ax.twinx()
    if "alpha" in updates.columns and updates["alpha"].notna().any():
        ax_alpha.plot(x, updates["alpha"], color="#d97706", linewidth=1.4, label="alpha")
    ax_alpha.set_ylabel("Alpha")
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax_alpha.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, fontsize=8, loc="best")

    ax = axes[1, 0]
    plotted_q = False
    for col, label, color in [
        ("q1_loss", "q1", "#0891b2"),
        ("q2_loss", "q2", "#1f9d55"),
    ]:
        if col in updates.columns and updates[col].notna().any():
            ax.plot(x, updates[col], label=label, linewidth=1.3, color=color)
            plotted_q = True
    if not plotted_q and "value_loss" in updates.columns and updates["value_loss"].notna().any():
        ax.plot(x, updates["value_loss"], label="critic total", linewidth=1.3, color="#dc2626")
    ax.set_title("Critic Loss")
    ax.set_xlabel("Global step")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    for col, label, color in [
        ("lr", "lr", "#0f172a"),
        ("gamma", "gamma", "#64748b"),
    ]:
        if col in updates.columns and updates[col].notna().any():
            ax.plot(x, updates[col], label=label, linewidth=1.3, color=color)
    ax.set_title("Training Constants")
    ax.set_xlabel("Global step")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out_path)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SAC/V15 canlı loglarından PNG grafik raporu üretir.")
    parser.add_argument("--logs-dir", type=Path, default=Path("logs"), help="Log klasörü.")
    parser.add_argument("--out-dir", type=Path, default=Path("logs") / "plots", help="Grafik çıktı klasörü.")
    parser.add_argument("--phase-contains", default="v15_1_0", help="phase_name içinde aranacak metin.")
    parser.add_argument("--prefix", default="", help="Çıktı dosyası ön eki. Boşsa faz adından üretilir.")
    parser.add_argument("--bin-size", type=float, default=10.0, help="Radius histogram bin genişliği.")
    parser.add_argument("--step-sample-stride", type=int, default=20, help="Step log örnekleme aralığı.")
    parser.add_argument("--chunksize", type=int, default=200_000, help="Step CSV parça okuma boyutu.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    episodes = load_episodes(args.logs_dir, args.phase_contains)
    updates = load_updates(args.logs_dir)
    steps = load_step_rows(args.logs_dir, args.phase_contains, args.step_sample_stride, args.chunksize)

    if args.prefix:
        prefix = slugify(args.prefix)
    elif not episodes.empty and "phase_name" in episodes.columns:
        prefix = slugify(str(episodes["phase_name"].dropna().iloc[-1]))
    else:
        prefix = slugify(args.phase_contains or "sac_live")

    outputs = {
        "summary": args.out_dir / f"{prefix}_summary.png",
        "success_rug": args.out_dir / f"{prefix}_success_rug.png",
        "radius_phase_plan": args.out_dir / f"{prefix}_reset_radius_phase_plan.png",
        "reset_map": args.out_dir / f"{prefix}_reset_map.png",
        "action_diagnostics": args.out_dir / f"{prefix}_action_diagnostics.png",
        "hit_positions": args.out_dir / f"{prefix}_hit_positions.png",
        "update_diagnostics": args.out_dir / f"{prefix}_update_diagnostics.png",
    }

    plot_summary(episodes, outputs["summary"])
    plot_success_rug(episodes, outputs["success_rug"])
    plot_radius_plan(episodes, outputs["radius_phase_plan"], args.bin_size)
    plot_reset_map(episodes, steps, outputs["reset_map"])
    plot_action_diagnostics(steps, outputs["action_diagnostics"])
    plot_hit_positions(episodes, steps, outputs["hit_positions"])
    plot_update_diagnostics(updates, outputs["update_diagnostics"])

    print(f"[plot_sac_report] episodes={len(episodes)} sampled_steps={len(steps)} updates={len(updates)}")
    for name, path in outputs.items():
        print(f"[plot_sac_report] {name}: {path}")


if __name__ == "__main__":
    main()
