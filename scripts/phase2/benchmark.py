import csv
import time
from datetime import datetime

import pymysql
from pymongo import MongoClient
from bson.decimal128 import Decimal128


# ============================================================
# Database Configuration
# ============================================================

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "benchmark_user",
    "password": "BenchmarkDB@2026",
    "database": "db_benchmark",
    "autocommit": True
}

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DATABASE = "db_benchmark"


class BenchmarkSuite:

    def __init__(self, csv_filepath):
        self.csv_filepath = csv_filepath

        self.mysql_conn = pymysql.connect(**MYSQL_CONFIG)

        self.mongo_client = MongoClient(MONGO_URI)
        self.mongo_db = self.mongo_client[MONGO_DATABASE]
        self.mongo_coll = self.mongo_db["transactions"]

        # Load and convert the dataset before timing database writes.
        self.rows = self.load_csv()

        self.mysql_rows = [
            (
                row["user_id"],
                row["amount"],
                row["category"],
                row["status"],
                row["created_at"]
            )
            for row in self.rows
        ]

        self.mongo_docs = [
            {
                "user_id": row["user_id"],
                "amount": Decimal128(row["amount"]),
                "category": row["category"],
                "status": row["status"],
                "created_at": row["created_at"]
            }
            for row in self.rows
        ]

    # --------------------------------------------------------
    # Load and normalize CSV data
    # --------------------------------------------------------

    def load_csv(self):

        rows = []

        with open(
            self.csv_filepath,
            mode="r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                rows.append({
                    "user_id": int(row["user_id"]),
                    "amount": row["amount"],
                    "category": row["category"],
                    "status": row["status"],
                    "created_at": datetime.strptime(
                        row["created_at"],
                        "%Y-%m-%d %H:%M:%S"
                    )
                })

        return rows

    # --------------------------------------------------------
    # Reset both databases
    # --------------------------------------------------------

    def reset_databases(self):

        cursor = self.mysql_conn.cursor()

        cursor.execute(
            "DROP TABLE IF EXISTS transactions"
        )

        cursor.execute("""
            CREATE TABLE transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at DATETIME NOT NULL
            )
        """)

        cursor.close()

        self.mongo_coll.drop()

        self.mongo_coll = self.mongo_db["transactions"]

    # --------------------------------------------------------
    # Bulk insertion benchmark
    # --------------------------------------------------------

    def benchmark_insert(self, batch_size=5000):

        self.reset_databases()

        # ----------------------------------------------------
        # MySQL insertion
        # ----------------------------------------------------

        mysql_cursor = self.mysql_conn.cursor()

        mysql_query = """
            INSERT INTO transactions
            (user_id, amount, category, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """

        mysql_start = time.perf_counter_ns()

        for i in range(
            0,
            len(self.mysql_rows),
            batch_size
        ):

            mysql_cursor.executemany(
                mysql_query,
                self.mysql_rows[i:i + batch_size]
            )

        mysql_end = time.perf_counter_ns()

        mysql_latency_ms = (
            mysql_end - mysql_start
        ) / 1_000_000

        mysql_cursor.close()

        # ----------------------------------------------------
        # MongoDB insertion
        # ----------------------------------------------------

        mongo_start = time.perf_counter_ns()

        for i in range(
            0,
            len(self.mongo_docs),
            batch_size
        ):

            self.mongo_coll.insert_many(
                self.mongo_docs[i:i + batch_size]
            )

        mongo_end = time.perf_counter_ns()

        mongo_latency_ms = (
            mongo_end - mongo_start
        ) / 1_000_000

        return {
            "mysql_write_ms": round(
                mysql_latency_ms,
                3
            ),
            "mongo_write_ms": round(
                mongo_latency_ms,
                3
            )
        }

    # --------------------------------------------------------
    # Point lookup benchmark
    # --------------------------------------------------------

    def run_point_lookup(self, target_user_id=1042):

        # MySQL

        cursor = self.mysql_conn.cursor()

        start = time.perf_counter_ns()

        cursor.execute(
            """
            SELECT *
            FROM transactions
            WHERE user_id = %s
            """,
            (target_user_id,)
        )

        cursor.fetchall()

        end = time.perf_counter_ns()

        mysql_ms = (
            end - start
        ) / 1_000_000

        cursor.close()

        # MongoDB

        start = time.perf_counter_ns()

        list(
            self.mongo_coll.find(
                {"user_id": target_user_id}
            )
        )

        end = time.perf_counter_ns()

        mongo_ms = (
            end - start
        ) / 1_000_000

        return (
            round(mysql_ms, 3),
            round(mongo_ms, 3)
        )

    # --------------------------------------------------------
    # Aggregation benchmark
    # --------------------------------------------------------

    def run_aggregation_query(
        self,
        category="Electronics"
    ):

        # MySQL

        cursor = self.mysql_conn.cursor()

        sql = """
            SELECT
                status,
                SUM(amount)
            FROM transactions
            WHERE category = %s
            GROUP BY status
        """

        start = time.perf_counter_ns()

        cursor.execute(
            sql,
            (category,)
        )

        cursor.fetchall()

        end = time.perf_counter_ns()

        mysql_ms = (
            end - start
        ) / 1_000_000

        cursor.close()

        # MongoDB

        pipeline = [
            {
                "$match": {
                    "category": category
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "total_amount": {
                        "$sum": "$amount"
                    }
                }
            }
        ]

        start = time.perf_counter_ns()

        list(
            self.mongo_coll.aggregate(
                pipeline
            )
        )

        end = time.perf_counter_ns()

        mongo_ms = (
            end - start
        ) / 1_000_000

        return (
            round(mysql_ms, 3),
            round(mongo_ms, 3)
        )

    # --------------------------------------------------------
    # Apply indexes
    # --------------------------------------------------------

    def apply_indexes(self):

        cursor = self.mysql_conn.cursor()

        cursor.execute(
            """
            CREATE INDEX idx_user_id
            ON transactions(user_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX idx_category
            ON transactions(category)
            """
        )

        cursor.close()

        self.mongo_coll.create_index(
            "user_id"
        )

        self.mongo_coll.create_index(
            "category"
        )

    # --------------------------------------------------------
    # Close connections
    # --------------------------------------------------------

    def close(self):

        self.mysql_conn.close()
        self.mongo_client.close()
