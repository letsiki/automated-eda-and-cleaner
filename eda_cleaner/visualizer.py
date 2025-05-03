"""
visualizer.py

Provides plotting utilities for visual exploratory data analysis (EDA) on a tagged DataFrame.
Requires columns to have an `eda_type` metadata attribute set beforehand.

Public Functions:
- generate_plots(df): Creates appropriate plots for each column based on its `eda_type`.

Private Functions:
- _bucket_datetime_series(s, freq): Buckets datetime data into time intervals.
- _plot_correlation_heatmap(df): Plots and saves a correlation heatmap of numeric variables.
- save_plot(fig, name): Saves a Matplotlib figure to a consistent output directory.
"""

from .log_setup.setup import setup, logging
import os
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pandas as pd

logger = logging.getLogger(__name__)
setup(logger)

matplotlib.use("Agg")
PLOT_OUTPUT_DIR = "output/plots"
os.makedirs(PLOT_OUTPUT_DIR, exist_ok=True)


def save_plot(fig: matplotlib.figure.Figure, name: str) -> None:
    """Saves a Matplotlib figure to the designated output directory.

    Args:
        fig (matplotlib.figure.Figure): The figure to save.
        name (str): The base filename (without extension).

    Notes:
        Files are saved as PNG and the figure is closed afterward to free memory.
    """
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_OUTPUT_DIR, f"{name}.png"))
    logger.info(f"Saved {name}.png")
    plt.close(fig)


def generate_plots(df: pd.DataFrame) -> None:
    """Generates column-wise plots based on EDA tags and saves them to disk.

    Args:
        df (pd.DataFrame): DataFrame with `eda_type` set as metadata on each column.

    Notes:
        This function generates:
        - Histograms for numeric columns
        - Bar plots for boolean and categorical columns
        - Time series counts for datetime columns
        - A correlation heatmap if at least two numeric columns are present
    """
    logger.info("Generating column based plots")
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

            _bucket_datetime_series(df[col]).plot(ax=ax)
            ax.set_title(f"Time series of {col}")
            save_plot(fig, f"date_{col}")

    logger.info("Finished generating column based plots")
    _plot_correlation_heatmap(df)


def _bucket_datetime_series(
    s: pd.Series, freq: str = None
) -> pd.Series:
    """Buckets datetime values into regular intervals and counts occurrences.

    Args:
        s (pd.Series): A datetime column to bucket.
        freq (str, optional): Pandas-compatible frequency string (e.g., 'M', 'D').
                              If None, inferred based on time span.

    Returns:
        pd.Series: A Series indexed by time buckets, with counts of values in each.

    Notes:
        Automatically handles timezone-stripped timestamps.
        Frequency is inferred if not provided, based on span of the date range.

    Examples:
        >>> _bucket_datetime_series(df['created_at'])
        2023-01-01    43
        2023-01-02    38
        ...
    """
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


def _plot_correlation_heatmap(
    df: pd.DataFrame,
    output_path: str = PLOT_OUTPUT_DIR + "/correlation_heatmap.png",
) -> None:
    """Generates and saves a heatmap of correlations among numeric columns.

    Args:
        df (pd.DataFrame): DataFrame with EDA-tagged columns.
        output_path (str): Path where the heatmap PNG should be saved.

    Notes:
        Only columns tagged with `eda_type == "numeric"` are considered.
        Skips plotting if fewer than 2 valid numeric columns are present.
    """
    numeric_cols = [
        col_name
        for col_name in df.columns
        if df[col_name].eda_type == "numeric"
    ]

    if len(numeric_cols) < 2:
        logger.info(
            "Not enough valid numeric variables for a correlation heatmap."
        )
        return

    logger.info("Generating correlation heatmap for the dataset")
    corr = df[numeric_cols].corr(method="pearson")

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
    )
    plt.title("Correlation Heatmap (Numeric Variables)")
    plt.tight_layout()
    plt.savefig(output_path)
    logger.info("Saved correlation heatmap")
    plt.close()
