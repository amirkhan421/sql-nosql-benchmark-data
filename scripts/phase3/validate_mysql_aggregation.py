import time
import pymysql


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "benchmark_user",
    "password": "BenchmarkDB@2026",
    "database": "db_benchmark",
}

QUERY = """
    SELECT
        status,
        SUM(amount)
    FROM transactions
    WHERE category = %s
    GROUP BY status
"""

ITERATIONS = 5
CATEGORY = "Electronics"


def measure(cursor):
    timings = []

    for _ in range(ITERATIONS):

        start = time.perf_counter_ns()

        cursor.execute(
            QUERY,
            (CATEGORY,)
        )

        cursor.fetchall()

        end = time.perf_counter_ns()

        elapsed_ms = (
            end - start
        ) / 1_000_000

        timings.append(elapsed_ms)

    return timings


def print_results(label, timings):

    print()
    print(label)
    print("-" * 50)

    for i, value in enumerate(timings, start=1):
        print(f"Iteration {i}: {value:.3f} ms")

    print(f"Average : {sum(timings) / len(timings):.3f} ms")
    print(f"Minimum : {min(timings):.3f} ms")
    print(f"Maximum : {max(timings):.3f} ms")


def main():

    connection = pymysql.connect(
    **DB_CONFIG
)

    cursor = connection.cursor()

    print("=" * 60)
    print("MYSQL 1M AGGREGATION VALIDATION")
    print("=" * 60)

    print("\nChecking current index state...")

    cursor.execute(
        "SHOW INDEX FROM transactions"
    )

    indexes = cursor.fetchall()

    for index in indexes:
        print(
            f"  {index[2]} -> {index[4]}"
        )

    # --------------------------------------------------------
    # Indexed measurement
    # --------------------------------------------------------

    print("\nMeasuring INDEXED aggregation...")

    indexed_timings = measure(cursor)

    print_results(
        "INDEXED",
        indexed_timings
    )

    # --------------------------------------------------------
    # Remove category index
    # --------------------------------------------------------

    print("\nRemoving idx_category...")

    cursor.execute(
        "DROP INDEX idx_category ON transactions"
    )

    # --------------------------------------------------------
    # Unindexed measurement
    # --------------------------------------------------------

    print("Measuring UNINDEXED aggregation...")

    unindexed_timings = measure(cursor)

    print_results(
        "UNINDEXED",
        unindexed_timings
    )

    # --------------------------------------------------------
    # Restore category index
    # --------------------------------------------------------

    print("\nRestoring idx_category...")

    cursor.execute(
        """
        CREATE INDEX idx_category
        ON transactions(category)
        """
    )

    connection.commit()

    print("Index restored.")

    cursor.close()
    connection.close()

    print()
    print("=" * 60)
    print("VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
