from .log_setup.setup import setup, logging
import json
import pandas as pd
import os

logger = logging.getLogger(__name__)
setup(logger)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_df(df: pd.DataFrame) -> None:
    df.to_csv(OUTPUT_DIR + "/final_table.csv", mode="w")


def write_json(summary: dict):
    """
    Save summary dictionary to a JSON file.
    """
    logger.info("Saving summary to a semi-structured JSON format")
    with open(OUTPUT_DIR + "/summary.json", "w") as f:
        json.dump(summary, f, indent=4, default=str)
    logger.info("Saved")


def write_summary_table(summary: dict, format: str = "all"):
    """
    Flatten summary dictionary into a table and write as CSV or Markdown.
    Filters out sub-dictionaries (like value_counts) and unhashable columns.
    """
    logger.info("Saving summary to a table format (csv, md)")
    summary_table = []

    for col, stats in summary.items():
        # Only include columns with basic stats (i.e., not unhashable-only)
        if isinstance(stats, dict) and "eda_type" in stats:
            row = {"column": col}
            for k, v in stats.items():
                if not isinstance(
                    v, dict
                ):  # Skip value_counts or nested dicts
                    row[k] = v
            summary_table.append(row)

    df = pd.DataFrame(summary_table)

    error_flag = True
    if format in ("csv", "all"):
        df.to_csv(OUTPUT_DIR + "/summary.csv", index=False)
        error_flag = False
    if format in ("md", "all"):
        df.to_markdown(buf=OUTPUT_DIR + "/summary.md")
        error_flag = False
    if error_flag:
        raise ValueError("Unsupported format: choose 'csv' or 'md'")

    logger.info("Saved")
