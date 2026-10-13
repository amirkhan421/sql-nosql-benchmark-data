import json
import os
import sys

from benchmark import BenchmarkSuite


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "data"
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results",
    "phase2"
)

DATASETS = {
    "10k": os.path.join(DATA_DIR, "data_10k.csv"),
    "100k": os.path.join(DATA_DIR, "data_100k.csv"),
    "1m": os.path.join(DATA_DIR, "data_1m.csv")
}

RESULT_FILE = os.path.join(
    RESULTS_DIR,
    "benchmark_results_corrected.json"
)

NUM_ITERATIONS = 5


# ============================================================
# Utility functions
# ============================================================

def average(values):
    return round(
        sum(values) / len(values),
        3
    )


def run_query_iterations(suite):

    mysql_point = []
    mongo_point = []

    mysql_aggregation = []
    mongo_aggregation = []

    for _ in range(NUM_ITERATIONS):

        mysql_p, mongo_p = suite.run_point_lookup()

        mysql_a, mongo_a = suite.run_aggregation_query()

        mysql_point.append(mysql_p)
        mongo_point.append(mongo_p)

        mysql_aggregation.append(mysql_a)
        mongo_aggregation.append(mongo_a)

    return {
        "point_lookup": {
            "mysql": average(mysql_point),
            "mongo": average(mongo_point)
        },
        "aggregation": {
            "mysql": average(mysql_aggregation),
            "mongo": average(mongo_aggregation)
        }
    }
def run_warm_cache_iterations(suite):

    # Warm-up queries: results are intentionally not measured.
    suite.run_point_lookup()
    suite.run_aggregation_query()

    # Measured warm-cache queries.
    return run_query_iterations(suite)

# ============================================================
# Main benchmark
# ============================================================

def run_suite():

    os.makedirs(
        RESULTS_DIR,
        exist_ok=True
    )

    final_results = {}

    print()
    print("=" * 60)
    print("      SQL vs NoSQL DATABASE BENCHMARK")
    print("           CORRECTED EXPERIMENT")
    print("=" * 60)
    print()

    for scale, csv_file in DATASETS.items():

        if not os.path.exists(csv_file):

            print(
                f"[ERROR] Dataset not found: {csv_file}"
            )

            continue

        print()
        print("=" * 60)
        print(
            f"STARTING CORRECTED BENCHMARK: "
            f"{scale.upper()}"
        )
        print("=" * 60)

        print(
            f"Dataset: {csv_file}"
        )

        print()

        suite = BenchmarkSuite(
            csv_file
        )

        try:

            # ------------------------------------------------
            # Bulk write benchmark
            # ------------------------------------------------

            print(
                f"[{scale}] Measuring bulk write latency..."
            )

            write_metrics = suite.benchmark_insert()

            print(
                f"  MySQL  : "
                f"{write_metrics['mysql_write_ms']} ms"
            )

            print(
                f"  MongoDB: "
                f"{write_metrics['mongo_write_ms']} ms"
            )

            # ------------------------------------------------
            # Unindexed queries
            # ------------------------------------------------

            print()

            print(
                f"[{scale}] Measuring UNINDEXED queries "
                f"({NUM_ITERATIONS} iterations)..."
            )

            unindexed_results = (
                run_query_iterations(suite)
            )

            print(
                "  Point Lookup:"
            )

            print(
                f"    MySQL  : "
                f"{unindexed_results['point_lookup']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{unindexed_results['point_lookup']['mongo']} ms"
            )

            print(
                "  Aggregation:"
            )

            print(
                f"    MySQL  : "
                f"{unindexed_results['aggregation']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{unindexed_results['aggregation']['mongo']} ms"
            )

            # ------------------------------------------------
            # Apply indexes
            # ------------------------------------------------

            print()

            print(
                f"[{scale}] Applying single-field indexes..."
            )

            suite.apply_indexes()

            print(
                "  Indexes applied successfully."
            )

            # ------------------------------------------------
            # Indexed queries
            # ------------------------------------------------

            print()

            print(
                f"[{scale}] Measuring INDEXED queries "
                f"({NUM_ITERATIONS} iterations)..."
            )

            indexed_results = (
                run_query_iterations(suite)
            )

            print(
                "  Point Lookup:"
            )

            print(
                f"    MySQL  : "
                f"{indexed_results['point_lookup']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{indexed_results['point_lookup']['mongo']} ms"
            )

            print(
                "  Aggregation:"
            )

            print(
                f"    MySQL  : "
                f"{indexed_results['aggregation']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{indexed_results['aggregation']['mongo']} ms"
            )
            # ------------------------------------------------
            # Warm-cache queries
            # ------------------------------------------------

            print()

            print(
                f"[{scale}] Warming database caches..."
            )

            # Warm-up queries are intentionally not timed.
            suite.run_point_lookup()
            suite.run_aggregation_query()

            print(
                f"[{scale}] Measuring WARM-CACHE queries "
                f"({NUM_ITERATIONS} iterations)..."
            )

            warm_cache_results = (
                run_query_iterations(suite)
            )

            print(
                "  Point Lookup:"
            )

            print(
                f"    MySQL  : "
                f"{warm_cache_results['point_lookup']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{warm_cache_results['point_lookup']['mongo']} ms"
            )

            print(
                "  Aggregation:"
            )

            print(
                f"    MySQL  : "
                f"{warm_cache_results['aggregation']['mysql']} ms"
            )

            print(
                f"    MongoDB: "
                f"{warm_cache_results['aggregation']['mongo']} ms"
            )
            # ------------------------------------------------
            # Store results
            # ------------------------------------------------

            final_results[scale] = {
                "dataset": csv_file,
                "iterations": NUM_ITERATIONS,
                "write_latency_ms": write_metrics,
                "unindexed": unindexed_results,
                "indexed": indexed_results,
                "warm_cache": warm_cache_results
            }

        finally:

            suite.close()

            print()

            print(
                f"[{scale}] Database connections closed."
            )

    # ========================================================
    # Save corrected results
    # ========================================================

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_results,
            file,
            indent=4
        )

    print()
    print("=" * 60)
    print("CORRECTED BENCHMARK SUITE COMPLETE")
    print("=" * 60)

    print(
        f"Results saved to:\n{RESULT_FILE}"
    )


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":

    sys.path.insert(
        0,
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    run_suite()