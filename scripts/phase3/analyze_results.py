import json
import os


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "results",
    "phase2",
    "benchmark_results_corrected.json"
)


def percent_change(old, new):
    return ((new - old) / old) * 100


def improvement_percent(baseline, optimized):
    return ((baseline - optimized) / baseline) * 100


def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def analyze():
    data = load_data()

    scales = ["10k", "100k", "1m"]

    print("=" * 70)
    print("DATABASE BENCHMARK NUMERICAL ANALYSIS")
    print("=" * 70)

    # ========================================================
    # 1. WRITE PERFORMANCE
    # ========================================================

    print("\n1. BULK WRITE PERFORMANCE")
    print("-" * 70)

    for scale in scales:
        mysql = data[scale]["write_latency_ms"]["mysql_write_ms"]
        mongo = data[scale]["write_latency_ms"]["mongo_write_ms"]

        mongo_advantage = ((mysql - mongo) / mysql) * 100

        print(f"\n{scale.upper()}")
        print(f"MySQL   : {mysql:.3f} ms")
        print(f"MongoDB : {mongo:.3f} ms")
        print(
            f"MongoDB relative to MySQL: "
            f"{mongo_advantage:.2f}% lower latency"
        )

    # ========================================================
    # 2. POINT LOOKUP
    # ========================================================

    print("\n\n2. POINT LOOKUP PERFORMANCE")
    print("-" * 70)

    for scale in scales:

        print(f"\n{scale.upper()}")

        for db in ["mysql", "mongo"]:

            unindexed = data[scale]["unindexed"]["point_lookup"][db]
            indexed = data[scale]["indexed"]["point_lookup"][db]
            warm = data[scale]["warm_cache"]["point_lookup"][db]

            indexed_improvement = improvement_percent(
                unindexed,
                indexed
            )

            warm_improvement = improvement_percent(
                unindexed,
                warm
            )

            print(f"\n{db.upper()}")
            print(f"Unindexed  : {unindexed:.3f} ms")
            print(f"Indexed    : {indexed:.3f} ms")
            print(f"Warm-cache : {warm:.3f} ms")

            print(
                f"Indexed improvement: "
                f"{indexed_improvement:.2f}%"
            )

            print(
                f"Warm-cache improvement: "
                f"{warm_improvement:.2f}%"
            )

    # ========================================================
    # 3. AGGREGATION
    # ========================================================

    print("\n\n3. AGGREGATION PERFORMANCE")
    print("-" * 70)

    for scale in scales:

        print(f"\n{scale.upper()}")

        for db in ["mysql", "mongo"]:

            unindexed = data[scale]["unindexed"]["aggregation"][db]
            indexed = data[scale]["indexed"]["aggregation"][db]
            warm = data[scale]["warm_cache"]["aggregation"][db]

            indexed_change = percent_change(
                unindexed,
                indexed
            )

            warm_improvement = improvement_percent(
                unindexed,
                warm
            )

            print(f"\n{db.upper()}")
            print(f"Unindexed  : {unindexed:.3f} ms")
            print(f"Indexed    : {indexed:.3f} ms")
            print(f"Warm-cache : {warm:.3f} ms")

            print(
                f"Indexed change: "
                f"{indexed_change:+.2f}%"
            )

            print(
                f"Warm-cache improvement: "
                f"{warm_improvement:.2f}%"
            )

    # ========================================================
    # 4. DATABASE COMPARISON
    # ========================================================

    print("\n\n4. MYSQL VS. MONGODB QUERY COMPARISON")
    print("-" * 70)

    for scale in scales:

        print(f"\n{scale.upper()}")

        for state in [
            "unindexed",
            "indexed",
            "warm_cache"
        ]:

            print(f"\n{state.upper()}")

            mysql_point = data[scale][state]["point_lookup"]["mysql"]
            mongo_point = data[scale][state]["point_lookup"]["mongo"]

            mysql_agg = data[scale][state]["aggregation"]["mysql"]
            mongo_agg = data[scale][state]["aggregation"]["mongo"]

            point_difference = (
                ((mysql_point - mongo_point) / mysql_point) * 100
            )

            aggregation_difference = (
                ((mysql_agg - mongo_agg) / mysql_agg) * 100
            )

            print(
                f"Point lookup — MongoDB relative to MySQL: "
                f"{point_difference:+.2f}%"
            )

            print(
                f"Aggregation — MongoDB relative to MySQL: "
                f"{aggregation_difference:+.2f}%"
            )

    # ========================================================
    # 5. SCALING
    # ========================================================

    print("\n\n5. SCALING FROM 10K TO 1M")
    print("-" * 70)

    for db in ["mysql", "mongo"]:

        print(f"\n{db.upper()}")

        write_10k = data["10k"]["write_latency_ms"][
            f"{db}_write_ms"
        ]

        write_1m = data["1m"]["write_latency_ms"][
            f"{db}_write_ms"
        ]

        write_growth = percent_change(
            write_10k,
            write_1m
        )

        print(
            f"Write latency growth: "
            f"{write_growth:.2f}%"
        )

        for state in [
            "unindexed",
            "indexed",
            "warm_cache"
        ]:

            point_10k = data["10k"][state]["point_lookup"][db]
            point_1m = data["1m"][state]["point_lookup"][db]

            aggregation_10k = data["10k"][state]["aggregation"][db]
            aggregation_1m = data["1m"][state]["aggregation"][db]

            point_growth = percent_change(
                point_10k,
                point_1m
            )

            aggregation_growth = percent_change(
                aggregation_10k,
                aggregation_1m
            )

            print(f"\n{state.upper()}")

            print(
                f"Point lookup growth: "
                f"{point_growth:.2f}%"
            )

            print(
                f"Aggregation growth: "
                f"{aggregation_growth:.2f}%"
            )

    print("\n")
    print("=" * 70)
    print("NUMERICAL ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    analyze()
