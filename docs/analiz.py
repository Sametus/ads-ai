from pathlib import Path

import pandas as pd
import plotly.express as px


ROOT = Path(__file__).resolve().parents[1]
EPISODE_LOG = ROOT / "logs" / "episode_log.csv"


def load_episode_log():
    if not EPISODE_LOG.exists():
        raise FileNotFoundError(f"Episode log bulunamadi: {EPISODE_LOG}")
    return pd.read_csv(EPISODE_LOG)


def build_success_rate_frame(episodes: pd.DataFrame) -> pd.DataFrame:
    df = episodes.copy()
    df["is_success"] = (df["done_reason"] == "success").astype(int)
    df["episode"] = range(1, len(df) + 1)
    df["success_rate"] = df["is_success"].expanding().mean() * 100.0
    return df


def main():
    episodes = load_episode_log()
    df = build_success_rate_frame(episodes)

    fig = px.line(
        df,
        x="episode",
        y="success_rate",
        title="V6 Cumulative Success Rate",
        labels={"episode": "Episode", "success_rate": "Success Rate (%)"},
    )
    fig.show()


if __name__ == "__main__":
    main()
