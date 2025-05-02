from .log_setup.setup import setup, logging

logger = logging.getLogger(__name__)
setup(logger)

import os
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

matplotlib.use("Agg")
PLOT_OUTPUT_DIR = "output/plots"
os.makedirs(PLOT_OUTPUT_DIR, exist_ok=True)


def save_plot(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_OUTPUT_DIR, f"{name}.png"))
    plt.close(fig)


def visualize(df):
    for col in df.columns:
        eda_type = getattr(df[col], "eda_type", None)
        if eda_type == "numeric":
            fig, ax = plt.subplots()
            sns.histplot(df[col].dropna(), kde=True, ax=ax)
            ax.set_title(f"Distribution of {col}")
            save_plot(fig, f"hist_{col}")

        elif eda_type == "boolean":
            fig, ax = plt.subplots()
            df[col].value_counts().plot(kind="bar", ax=ax)
            ax.set_title(f"Boolean distribution of {col}")
            save_plot(fig, f"bool_{col}")

        elif eda_type == "category":
            fig, ax = plt.subplots()
            df[col].value_counts().head(15).plot(kind="bar", ax=ax)
            ax.set_title(f"Top categories in {col}")
            save_plot(fig, f"cat_{col}")

        elif eda_type == "date":
            fig, ax = plt.subplots()

            bucket_datetime_series(df[col]).plot(ax=ax)
            ax.set_title(f"Time series of {col}")
            save_plot(fig, f"date_{col}")


import pandas as pd


def bucket_datetime_series(s: pd.Series, freq: str = None) -> pd.Series:
    s = s.dropna()

    # Drop timezone if present to avoid warnings
    if s.dt.tz is not None:
        s = s.dt.tz_localize(None)

    # Auto-determine frequency based on span
    date_range = s.max() - s.min()
    if freq is None:
        if date_range > pd.Timedelta(days=730):
            freq = "M"
        elif date_range > pd.Timedelta(days=90):
            freq = "W"
        elif date_range > pd.Timedelta(days=7):
            freq = "D"
        else:
            freq = "H"

    # Robust bucketing for any freq
    bucketed = s.dt.to_period(freq).dt.to_timestamp()

    # Return full distribution
    return bucketed.value_counts().sort_index()

def plot_correlation_heatmap(df: pd.DataFrame, output_path: str = PLOT_OUTPUT_DIR + "/correlation_heatmap.png"):
    numeric_cols = [col_name for col_name in df.columns if df[col_name].eda_type == 'numeric']

    # # Exclude constant or ID-like columns
    # filtered_cols = [
    #     col for col in numeric_cols
    #     if df[col].nunique(dropna=False) > 1 and df[col].nunique() < len(df)
    # ]

    if len(numeric_cols) < 2:
        print("Not enough valid numeric variables for a correlation heatmap.")
        return

    corr = df[numeric_cols].corr(method="pearson")

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, linewidths=0.5)
    plt.title("Correlation Heatmap (Numeric Variables)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
