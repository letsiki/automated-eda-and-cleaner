# **eda\_cleaner**

**eda\_cleaner** is a Python-based CLI tool for **automated data cleaning** and **exploratory data analysis (EDA)**. It supports loading tabular data from PostgreSQL databases or CSV files, applies robust cleaning pipelines, infers semantic column types, and outputs clear summaries and visualizations.

## **✨ Features**

* 📥 Load data from:

  * PostgreSQL databases (via SQLAlchemy URI)

  * Local CSV files

  * Built-in default dataset

* 🧹 Automatic data cleaning:

  * Standardizes column names

  * Removes duplicate rows

  * Coerces types (numeric, date, boolean, etc.)

  * Handles missing values with sensible defaults

* 🔍 Semantic type tagging:

  * Assigns each column an `eda_type` like `boolean`, `category`, `numeric`, `date`, `primary id`, etc.

* 📊 EDA outputs:

  * JSON summary with counts, stats, and inferred types

  * Formatted summary table (`CSV`)

  * Visualizations (`PNG`)

* 📝 Cleaned dataset export

## **🚀 Installation**

1. Clone the repo:

<pre>git clone https://github.com/yourusername/eda_cleaner.git
cd eda_cleaner</pre>

2. Setup environment:

<pre># Option 1: Using Conda

conda env create -f environment.yml

conda activate eda_cleaner

# Option 2: Using Docker

docker-compose up</pre>

## **⚙️ Usage**

You can run `eda_cleaner` as a CLI tool in one of three ways:

### **1\. Load from a PostgreSQL database**

<pre>python -m eda_cleaner.cli -d "postgresql://username:password@localhost:5432/dbname"</pre>

### **2\. Load from a CSV file**

<pre>python -m eda_cleaner.cli -c data/my_file.csv</pre>

### **3\. Use the default dataset**

<pre>python -m eda_cleaner.cli
# When prompted, type 'y' to load the default dataset.</pre>

## **📂 Output**

Results are saved in the `output/` directory:

* `cleaned_data.csv` — Cleaned dataset

* `summary_table.csv` — Tabular EDA summary

* `summary.json` — JSON-formatted summary with stats and column types

* `plots/` — Histogram or bar chart per column, based on inferred type

## **🧠 Project Structure**

eda\_cleaner/  
├── cleaner.py           \# Cleaning pipeline  
├── cli.py               \# Command-line interface  
├── loader.py            \# Data loading logic  
├── profiler.py          \# Column-type tagging \+ summary  
├── visualizer.py        \# EDA plots  
├── writer.py            \# Writes outputs  
├── log\_setup/           \# Logging configuration  
│   └── setup.py
├── data/                \# Default dataset  
│   └── global-air-pollution-dataset.csv  
├── output/              \# Results (auto-generated)  
│   ├── cleaned\_data.csv  
│   ├── summary\_table.csv  
│   ├── summary.json  
│   └── plots/  
├── environment.yml      \# Conda environment definition  
├── docker-compose.yml   \# Dockerized environment  
└── README.md

## **🔧 Dev & Contribution**

* Modular, testable functions for each step

* Logging integrated throughout via `log_setup`

* Contributions welcome: open an issue or PR\!

## **📜 License**

MIT
