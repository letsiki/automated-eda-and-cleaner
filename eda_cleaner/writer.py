"""
writer.py

This module handles all export operations for the data cleaning and EDA pipeline.
It writes cleaned DataFrames to CSV, saves profiling summaries as JSON, and
outputs flat summary tables as CSV or Markdown for easy viewing and sharing.

Functions:
- write_df(df): Save the cleaned DataFrame to 'output/clean_data.csv'.
- write_json(summary): Export the profiling summary dictionary to 'output/summary.json'.
- write_summary_table(summary, format): Flatten and export selected summary stats
  to 'summary_table.csv' and/or 'summary_table.md'.

All output is saved in the local 'output/' directory. Logging is used to track each step.
"""

from .log_setup.setup import setup, logging
import json
import pandas as pd
import os

logger = logging.getLogger(__name__)
setup(logger)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_df(df: pd.DataFrame) -> None:
    logger.info("Exporting clean dataframe to csv")
    df.to_csv(OUTPUT_DIR + "/clean_data.csv", mode="w")
    logger.info("Exported")


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
        if isinstance(stats, dict):
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
        df.to_csv(OUTPUT_DIR + "/summary_table.csv", index=False)
        error_flag = False
    if format in ("md", "all"):
        df.to_markdown(buf=OUTPUT_DIR + "/summary_table.md")
        error_flag = False
    if error_flag:
        raise ValueError("Unsupported format: choose 'csv' or 'md'")

    logger.info("Saved")
