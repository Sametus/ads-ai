from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "docs" / "readme_assets"
LOG_DIR = ROOT / "logs"


def tr(text: str) -> str:
    return text.encode("ascii").decode("unicode_escape")


def setup_plot():
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.unicode_minus"] = False
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def read_episode_rows():
    path = LOG_DIR / "episode_log.csv"
    rows = []
    if not path.exists():
        return rows
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "v16_0_7" in str(row.get("phase_name", "")):
                rows.append(row)
    return rows


def read_update_rows():
    path = LOG_DIR / "update_log.csv"
    rows = []
    if not path.exists():
        return rows
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows.extend(reader)
    return rows


def fnum(row, key, default=np.nan):
    try:
        value = row.get(key, "")
        if value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(row, key, default=0):
    try:
        value = row.get(key, "")
        if value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def save(fig, name):
    fig.savefig(ASSET_DIR / name, bbox_inches="tight")
    plt.close(fig)


def empty_chart(name, title, message):
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=160)
    ax.set_title(title, fontweight="bold")
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    save(fig, name)


def rolling_mean(values, window):
    if not values:
        return []
    out = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        out.append(float(np.mean(values[start : i + 1])))
    return out


def plot_alignment_theta():
    theta = np.linspace(0, 180, 361)
    alignment = np.cos(np.radians(theta))
    fig, ax = plt.subplots(figsize=(9, 5), dpi=160)
    ax.plot(theta, alignment, color="#2563eb", linewidth=2.5)
    ax.axvline(30, color="#16a34a", linestyle="--", linewidth=1.5, label=tr("30\\u00b0 e\\u015fik"))
    ax.axhline(math.cos(math.radians(30)), color="#16a34a", linestyle=":", linewidth=1.4)
    ax.axhline(0, color="#111827", linewidth=1.0, alpha=0.7)
    ax.set_title(tr("Alignment ve theta ili\\u015fkisi"), fontsize=14, fontweight="bold")
    ax.set_xlabel(tr("Theta a\\u00e7\\u0131s\\u0131 (derece)"))
    ax.set_ylabel("alignment = cos(theta)")
    ax.grid(True, color="#e5e7eb")
    ax.legend(frameon=False)
    ax.annotate(
        tr("K\\u00fc\\u00e7\\u00fck theta\\nhedefe daha iyi hizalanma"),
        xy=(18, math.cos(math.radians(18))),
        xytext=(50, 0.75),
        arrowprops=dict(arrowstyle="->", color="#374151"),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#d1d5db"),
    )
    save(fig, "alignment_theta_curve.png")


def plot_theta_nonlinearity():
    h = 100.0
    x = np.linspace(20, 700, 500)
    theta = np.degrees(np.arctan2(h, x))
    derivative = np.degrees(h / (x * x + h * h))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), dpi=160)
    fig.suptitle(tr("Sabit hedef irtifas\\u0131nda theta nonlineerli\\u011fi"), fontsize=14, fontweight="bold")

    axes[0].plot(x, theta, color="#0f766e", linewidth=2.4)
    axes[0].set_title(tr("Mesafe azald\\u0131k\\u00e7a theta h\\u0131zl\\u0131 b\\u00fcy\\u00fcr"))
    axes[0].set_xlabel(tr("Yatay mesafe x (m)"))
    axes[0].set_ylabel(tr("theta = atan(h / x) (derece)"))
    axes[0].grid(True, color="#e5e7eb")

    axes[1].plot(x, derivative, color="#dc2626", linewidth=2.4)
    axes[1].set_title(tr("Yak\\u0131nda a\\u00e7\\u0131 de\\u011fi\\u015fim hassasiyeti artar"))
    axes[1].set_xlabel(tr("Yatay mesafe x (m)"))
    axes[1].set_ylabel(tr("|d theta / dx|"))
    axes[1].grid(True, color="#e5e7eb")

    fig.text(
        0.5,
        -0.02,
        tr("h = 100 m sabitken uzak mesafede al\\u00e7akta bekleme, alignment sinyali taraf\\u0131ndan fazla cezaland\\u0131r\\u0131lmayabilir."),
        ha="center",
        fontsize=9.5,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    save(fig, "theta_nonlinearity_fixed_altitude.png")


def plot_phase_timeline():
    labels = [
        ("PPO", tr("K\\u00fc\\u00e7\\u00fck radius\\nba\\u015flang\\u0131\\u00e7 denemeleri")),
        ("PN", tr("Klasik g\\u00fcd\\u00fcm\\nsa\\u011fl\\u0131k testi")),
        ("SAC", tr("Replay buffer\\ncontinuous control")),
        ("V16", tr("Aim point\\nellipsoid hit")),
        ("Final", tr("step675000\\ndeterministik test")),
    ]
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=160)
    ax.plot(x, np.zeros_like(x), color="#1f2937", linewidth=2)
    colors = ["#64748b", "#0891b2", "#7c3aed", "#d97706", "#16a34a"]
    for i, ((title, note), color) in enumerate(zip(labels, colors)):
        ax.scatter(i, 0, s=420, color=color, edgecolor="white", linewidth=2, zorder=3)
        ax.text(i, 0.16, title, ha="center", fontsize=12, fontweight="bold", color=color)
        ax.text(i, -0.22, note, ha="center", va="top", fontsize=9)
    ax.set_title(tr("ADS-AI geli\\u015ftirme fazlar\\u0131"), fontsize=14, fontweight="bold")
    ax.set_xlim(-0.5, len(labels) - 0.5)
    ax.set_ylim(-0.65, 0.55)
    ax.set_axis_off()
    save(fig, "phase_timeline.png")


def plot_formula_cards():
    formulas = [
        (
            "formula_ppo.png",
            "PPO",
            r"$L^{CLIP}(\theta)=\mathbb{E}[\min(r_t A_t,\ clip(r_t,1-\epsilon,1+\epsilon)A_t)]$",
            tr("Policy g\\u00fcncellemesini s\\u0131n\\u0131rlayarak ani davran\\u0131\\u015f de\\u011fi\\u015fimlerini azalt\\u0131r."),
            "#2563eb",
        ),
        (
            "formula_sac.png",
            "SAC",
            r"$J_{\pi}=\mathbb{E}[\alpha \log \pi(a|s)-Q(s,a)]$",
            tr("Actor y\\u00fcksek Q de\\u011ferli action ararken entropy ile ke\\u015ffi korur."),
            "#7c3aed",
        ),
        (
            "formula_pn.png",
            "PN",
            r"$a_{cmd}=N \cdot V_c \cdot \dot{\lambda}$",
            tr("Kapanma h\\u0131z\\u0131 ve LOS rate ile klasik hedef kesme komutu \\u00fcretir."),
            "#0f766e",
        ),
    ]
    for filename, title, formula, note, color in formulas:
        fig, ax = plt.subplots(figsize=(9, 3.0), dpi=160)
        ax.set_axis_off()
        ax.text(0.03, 0.78, title, fontsize=18, fontweight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.50, formula, fontsize=17, ha="center", va="center", transform=ax.transAxes)
        ax.text(0.5, 0.18, note, fontsize=10.5, ha="center", color="#374151", transform=ax.transAxes)
        ax.add_patch(plt.Rectangle((0.015, 0.08), 0.97, 0.82, transform=ax.transAxes, fill=False, ec=color, lw=1.8))
        save(fig, filename)


def plot_stochastic_deterministic():
    x = np.linspace(0, 1, 240)
    mu = 0.55 + 0.22 * np.sin(2 * np.pi * x)
    rng = np.random.default_rng(12)
    stochastic = mu + rng.normal(0, 0.09, len(x))
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=160)
    ax.plot(x, stochastic, color="#94a3b8", alpha=0.55, linewidth=1.3, label=tr("Stokastik train action"))
    ax.plot(x, mu, color="#7c3aed", linewidth=2.8, label=tr("Deterministik test action (mu)"))
    ax.fill_between(x, mu - 0.09, mu + 0.09, color="#7c3aed", alpha=0.12, label=tr("Ke\\u015fif band\\u0131"))
    ax.set_title(tr("SAC: stokastik e\\u011fitim, deterministik test"), fontsize=14, fontweight="bold")
    ax.set_xlabel(tr("Zaman / episode i\\u00e7i ilerleme"))
    ax.set_ylabel("action")
    ax.grid(True, color="#e5e7eb")
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.28))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "sac_stochastic_vs_deterministic.png")


def plot_terminal_distribution(rows):
    if not rows:
        empty_chart("v16_terminal_distribution.png", tr("Terminal da\\u011f\\u0131l\\u0131m\\u0131"), tr("episode_log.csv bulunamad\\u0131."))
        return
    counts = {}
    for row in rows:
        key = row.get("done_reason", "unknown") or "unknown"
        counts[key] = counts.get(key, 0) + 1
    order = sorted(counts, key=lambda k: counts[k], reverse=True)
    colors = {
        "success": "#16a34a",
        "missed_intercept": "#f59e0b",
        "timeout": "#64748b",
        "high_altitude": "#06b6d4",
        "low_agl": "#ef4444",
        "bad_angle": "#8b5cf6",
        "wrong_way": "#dc2626",
    }
    fig, ax = plt.subplots(figsize=(9.5, 5), dpi=160)
    bars = ax.bar(order, [counts[k] for k in order], color=[colors.get(k, "#94a3b8") for k in order])
    ax.set_title(tr("V16 terminal sebebi da\\u011f\\u0131l\\u0131m\\u0131"), fontsize=14, fontweight="bold")
    ax.set_ylabel(tr("Episode say\\u0131s\\u0131"))
    ax.tick_params(axis="x", rotation=20)
    ax.grid(True, axis="y", color="#e5e7eb")
    total = sum(counts.values())
    for bar in bars:
        value = int(bar.get_height())
        ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value}\n%{100*value/total:.1f}", ha="center", va="bottom", fontsize=8.5)
    fig.tight_layout()
    save(fig, "v16_terminal_distribution.png")


def plot_rolling_success(rows):
    if not rows:
        empty_chart("v16_rolling_success.png", tr("Rolling success"), tr("episode_log.csv bulunamad\\u0131."))
        return
    rows = sorted(rows, key=lambda r: inum(r, "episode_id"))
    episodes = [inum(r, "episode_id") for r in rows]
    success = [1 if r.get("done_reason") == "success" else 0 for r in rows]
    r50 = rolling_mean(success, 50)
    r100 = rolling_mean(success, 100)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=160)
    ax.plot(episodes, np.array(r50) * 100, color="#0f766e", linewidth=2.2, label="50 episode")
    ax.plot(episodes, np.array(r100) * 100, color="#2563eb", linewidth=2.0, label="100 episode")
    ax.set_title(tr("Rolling success oran\\u0131"), fontsize=14, fontweight="bold")
    ax.set_xlabel("Episode")
    ax.set_ylabel(tr("Success oran\\u0131 (%)"))
    ax.set_ylim(0, 100)
    ax.grid(True, color="#e5e7eb")
    ax.legend(frameon=False)
    save(fig, "v16_rolling_success.png")


def plot_success_scatter(rows):
    if not rows:
        empty_chart("v16_success_scatter_by_episode.png", tr("Success scatter"), tr("episode_log.csv bulunamad\\u0131."))
        return
    rows = sorted(rows, key=lambda r: inum(r, "episode_id"))
    episodes = np.array([inum(r, "episode_id") for r in rows])
    success = np.array([1 if r.get("done_reason") == "success" else 0 for r in rows], dtype=float)
    y = success + np.random.default_rng(4).normal(0, 0.018, len(success))
    colors = np.where(success > 0.5, "#16a34a", "#94a3b8")
    r100 = np.array(rolling_mean(success.tolist(), 100)) * 100

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), dpi=160, sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    axes[0].scatter(episodes, y, s=np.where(success > 0.5, 24, 12), c=colors, alpha=np.where(success > 0.5, 0.9, 0.28), edgecolors="none")
    axes[0].set_yticks([0, 1])
    axes[0].set_yticklabels([tr("ba\\u015far\\u0131s\\u0131z"), "success"])
    axes[0].set_ylabel(tr("Terminal sonucu"))
    axes[0].set_title(tr("Episode s\\u0131ras\\u0131na g\\u00f6re success scatter"), fontsize=14, fontweight="bold")
    axes[0].grid(True, color="#e5e7eb")

    axes[1].plot(episodes, r100, color="#2563eb", linewidth=2.2)
    axes[1].set_ylabel(tr("100 episode rolling (%)"))
    axes[1].set_xlabel("Episode")
    axes[1].grid(True, color="#e5e7eb")
    fig.tight_layout()
    save(fig, "v16_success_scatter_by_episode.png")


def plot_distance_theta(rows):
    if not rows:
        empty_chart("v16_distance_theta.png", tr("Distance ve theta"), tr("episode_log.csv bulunamad\\u0131."))
        return
    rows = sorted(rows, key=lambda r: inum(r, "episode_id"))
    episodes = [inum(r, "episode_id") for r in rows]
    distance = [fnum(r, "final_target_distance", fnum(r, "final_distance")) for r in rows]
    theta = [fnum(r, "final_theta_deg") for r in rows]
    distance_roll = rolling_mean(distance, 50)
    theta_roll = rolling_mean(theta, 50)

    fig, ax1 = plt.subplots(figsize=(10, 5), dpi=160)
    ax1.plot(episodes, distance_roll, color="#2563eb", linewidth=2.1, label=tr("Final mesafe (50 rolling)"))
    ax1.set_xlabel("Episode")
    ax1.set_ylabel(tr("Final mesafe (m)"), color="#2563eb")
    ax1.tick_params(axis="y", labelcolor="#2563eb")
    ax1.grid(True, color="#e5e7eb")

    ax2 = ax1.twinx()
    ax2.plot(episodes, theta_roll, color="#dc2626", linewidth=2.1, label=tr("Theta (50 rolling)"))
    ax2.set_ylabel(tr("Theta a\\u00e7\\u0131s\\u0131 (derece)"), color="#dc2626")
    ax2.tick_params(axis="y", labelcolor="#dc2626")
    ax1.set_title(tr("Final mesafe ve theta e\\u011filimi"), fontsize=14, fontweight="bold")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="upper right")
    fig.tight_layout()
    save(fig, "v16_distance_theta.png")


def plot_alpha_entropy(rows):
    if not rows:
        empty_chart("sac_alpha_entropy.png", tr("SAC alpha ve entropy"), tr("update_log.csv bulunamad\\u0131."))
        return
    rows = sorted(rows, key=lambda r: inum(r, "update_id"))
    update = [inum(r, "update_id") for r in rows]
    alpha = [fnum(r, "alpha", fnum(r, "clip_frac")) for r in rows]
    entropy = [fnum(r, "entropy") for r in rows]
    value_loss = [fnum(r, "value_loss") for r in rows]

    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2), dpi=160, sharex=True)
    axes[0].plot(update, alpha, color="#7c3aed", linewidth=2.0, label="alpha")
    axes[0].plot(update, entropy, color="#0f766e", linewidth=1.8, label="entropy")
    axes[0].set_title(tr("SAC alpha ve entropy e\\u011frileri"), fontsize=14, fontweight="bold")
    axes[0].set_ylabel(tr("De\\u011fer"))
    axes[0].grid(True, color="#e5e7eb")
    axes[0].legend(frameon=False)

    axes[1].plot(update, value_loss, color="#d97706", linewidth=1.5)
    axes[1].set_ylabel("value loss")
    axes[1].set_xlabel("Update")
    axes[1].grid(True, color="#e5e7eb")
    fig.tight_layout()
    save(fig, "sac_alpha_entropy.png")


def plot_selected_checkpoint():
    rows = [
        {"offset": -5.0, "theta": 35.8, "closing": 132.2, "valid": 0},
        {"offset": -3.0, "theta": 32.1, "closing": 132.7, "valid": 0},
        {"offset": 3.0, "theta": 22.4, "closing": 128.0, "valid": 1},
        {"offset": 5.0, "theta": 17.7, "closing": 137.3, "valid": 1},
    ]
    offsets = [r["offset"] for r in rows]
    theta = [r["theta"] for r in rows]
    closing = [r["closing"] for r in rows]
    colors = ["#0f766e" if r["valid"] else "#d97706" for r in rows]

    fig, ax1 = plt.subplots(figsize=(9.5, 5.2), dpi=160)
    ax1.axhspan(0, 30, color="#dcfce7", alpha=0.6, label=tr("Theta hedef band\\u0131 (0-30\\u00b0)"))
    ax1.axhline(30, color="#166534", linestyle="--", linewidth=1.2)
    ax1.scatter(offsets, theta, c=colors, s=120, edgecolor="#111827", linewidth=0.8, zorder=3)
    ax1.plot(offsets, theta, color="#1f2937", linewidth=1.4, alpha=0.7)
    ax1.set_xlabel("Heading offset (derece)")
    ax1.set_ylabel(tr("Vuru\\u015f a\\u00e7\\u0131s\\u0131 theta (derece)"))
    ax1.set_ylim(0, 45)
    ax1.grid(True, color="#e5e7eb")

    ax2 = ax1.twinx()
    ax2.plot(offsets, closing, color="#2563eb", marker="s", linewidth=2.0, label=tr("Closing h\\u0131z\\u0131"))
    ax2.set_ylabel(tr("Closing h\\u0131z\\u0131 (m/s)"))
    ax2.set_ylim(0, 170)

    for row in rows:
        label = "Valid intercept" if row["valid"] else "Weak hit"
        ax1.annotate(
            f"{label}\n\u03b8={row['theta']:.1f}\u00b0\nclosing={row['closing']:.1f}",
            xy=(row["offset"], row["theta"]),
            xytext=(0, 15),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#111827",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#d1d5db", alpha=0.9),
        )

    fig.suptitle(tr("Se\\u00e7ili SAC checkpoint testi: step 675000"), fontsize=14, fontweight="bold")
    ax1.set_title(tr("Deterministik testte +3 ve +5 offsetleri valid intercept verdi; +5 g\\u00f6rsel olarak final aday se\\u00e7ildi."), fontsize=10, pad=10)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 0.92))
    save(fig, "v16_selected_checkpoint_test.png")


def main():
    setup_plot()
    episodes = read_episode_rows()
    updates = read_update_rows()

    plot_alignment_theta()
    plot_theta_nonlinearity()
    plot_phase_timeline()
    plot_formula_cards()
    plot_stochastic_deterministic()
    plot_terminal_distribution(episodes)
    plot_rolling_success(episodes)
    plot_success_scatter(episodes)
    plot_distance_theta(episodes)
    plot_alpha_entropy(updates)
    plot_selected_checkpoint()

    print(tr("README grafikleri T\\u00fcrk\\u00e7e karakter deste\\u011fiyle yeniden \\u00fcretildi."))


if __name__ == "__main__":
    main()
