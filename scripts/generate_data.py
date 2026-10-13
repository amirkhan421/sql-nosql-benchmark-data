import csv
import random
from faker import Faker

SEED = 42

fake = Faker()
Faker.seed(SEED)
random.seed(SEED)


def generate_transactions(num_records, filename):
    categories = ["Electronics", "Clothing", "Home", "Books", "Sports"]
    statuses = ["Completed", "Pending", "Failed"]

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "user_id",
            "amount",
            "category",
            "status",
            "created_at"
        ])

        for _ in range(num_records):
            writer.writerow([
                random.randint(1, 50000),
                round(random.uniform(5.0, 1000.0), 2),
                random.choice(categories),
                random.choice(statuses),
                fake.date_time_between(
                    start_date="-2y",
                    end_date="now"
                ).strftime("%Y-%m-%d %H:%M:%S")
            ])

    print(f"Successfully generated {num_records} records in {filename}")


if __name__ == "__main__":
    generate_transactions(10_000, "data/data_10k.csv")
    generate_transactions(100_000, "data/data_100k.csv")
    generate_transactions(1_000_000, "data/data_1m.csv")
