# SQL and NoSQL Database Benchmark

This repository contains datasets, benchmarking scripts, experimental results, and visualizations for a comparative evaluation of SQL and NoSQL database performance under different indexing and cache conditions.

## Research Objectives

The project evaluates database performance for different workloads, including bulk data insertion, point lookups, and aggregation queries. It aims to compare performance under documented experimental configurations.

## Repository Structure

```text
data/
  data_10k.csv
  data_100k.csv
  data_1m.csv

results/
  phase2/
    benchmark_results.json
    benchmark_results_corrected.json
  phase3/
    fig1_bulk_write_latency.png
    fig2_point_lookup_latency.png
    fig3_aggregation_latency.png
    mysql_1m_aggregation_validation.txt
    numerical_analysis.txt

scripts/
  generate_data.py
  phase2/
    benchmark.py
    runner.py
  phase3/
    analyze_results.py
    plot_results.py
    validate_mysql_aggregation.py

requirements.txt
```

## Technologies

- MySQL
- MongoDB
- Python
- pandas and NumPy
- Matplotlib
- Faker
- PyMySQL and PyMongo

## Datasets

The repository includes CSV datasets containing 10,000, 100,000, and 1,000,000 records. These datasets are intended to support the database benchmarking experiments.

## Experimental Workloads

The included scripts and results cover:

- Bulk write performance
- Point lookup latency
- Aggregation query latency
- Numerical analysis and result visualization

Refer to the scripts and result files for the implemented workloads and available experimental outputs. Do not assume that every workload uses identical indexing or cache settings; consult the benchmark configuration.

## Installation

Python and running MySQL and MongoDB instances are required.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure database connection settings using environment variables or a local `.env` file. Do not commit passwords, access tokens, or other secrets.

## Reproducibility

Before reproducing the experiments, configure the database connections and verify the database versions, schemas, indexes, cache settings, and benchmark parameters. Review the scripts before running them, as some scripts may generate data or modify database contents.

For accurate comparisons, record the software versions, hardware configuration, dataset size, indexing strategy, cache state, and number of repetitions.

## Research Use

This repository accompanies research comparing SQL and NoSQL database performance. Please cite the associated research paper when referencing these materials. Add the final publication citation and DOI here once available.

## Data Availability

The datasets, scripts, and experimental outputs are provided in this repository. For the persistent archival record, add the Zenodo DOI here once the repository has been archived.
