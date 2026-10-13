import json
import os

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "results",
    "phase2",
    "benchmark_results_corrected.json"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "results",
    "phase3"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Plot configuration
# ============================================================

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9
})


# ============================================================
# Load benchmark data
# ============================================================

def load_data():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# Generate figures
# ============================================================

def generate_plots():

    data = load_data()

    scales = [
        "10k",
        "100k",
        "1m"
    ]

    scale_labels = [
        "10K",
        "100K",
        "1M"
    ]

    # --------------------------------------------------------
    # Extract write latency
    # --------------------------------------------------------

    mysql_writes = [
        data[s]["write_latency_ms"]["mysql_write_ms"]
        for s in scales
    ]

    mongo_writes = [
        data[s]["write_latency_ms"]["mongo_write_ms"]
        for s in scales
    ]

    # --------------------------------------------------------
    # Extract point lookup latency
    # --------------------------------------------------------

    mysql_point_unindexed = [
        data[s]["unindexed"]["point_lookup"]["mysql"]
        for s in scales
    ]

    mysql_point_indexed = [
        data[s]["indexed"]["point_lookup"]["mysql"]
        for s in scales
    ]

    mysql_point_cached = [
        data[s]["warm_cache"]["point_lookup"]["mysql"]
        for s in scales
    ]

    mongo_point_unindexed = [
        data[s]["unindexed"]["point_lookup"]["mongo"]
        for s in scales
    ]

    mongo_point_indexed = [
        data[s]["indexed"]["point_lookup"]["mongo"]
        for s in scales
    ]

    mongo_point_cached = [
        data[s]["warm_cache"]["point_lookup"]["mongo"]
        for s in scales
    ]

    # --------------------------------------------------------
    # Extract aggregation latency
    # --------------------------------------------------------

    mysql_agg_unindexed = [
        data[s]["unindexed"]["aggregation"]["mysql"]
        for s in scales
    ]

    mysql_agg_indexed = [
        data[s]["indexed"]["aggregation"]["mysql"]
        for s in scales
    ]

    mysql_agg_cached = [
        data[s]["warm_cache"]["aggregation"]["mysql"]
        for s in scales
    ]

    mongo_agg_unindexed = [
        data[s]["unindexed"]["aggregation"]["mongo"]
        for s in scales
    ]

    mongo_agg_indexed = [
        data[s]["indexed"]["aggregation"]["mongo"]
        for s in scales
    ]

    mongo_agg_cached = [
        data[s]["warm_cache"]["aggregation"]["mongo"]
        for s in scales
    ]

    x = np.arange(len(scales))

    # ========================================================
    # FIGURE 1 — Bulk Write Latency
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(6.5, 4.2)
    )

    width = 0.35

    ax.bar(
        x - width / 2,
        mysql_writes,
        width,
        label="MySQL",
        hatch="//",
        edgecolor="black"
    )

    ax.bar(
        x + width / 2,
        mongo_writes,
        width,
        label="MongoDB",
        hatch="\\\\",
        edgecolor="black"
    )

    ax.set_xlabel(
        "Dataset Size (Records)"
    )

    ax.set_ylabel(
        "Write Latency (ms)"
    )

    ax.set_title(
        "Bulk Write Latency Comparison"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(scale_labels)

    ax.set_yscale("log")

    ax.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.7
    )

    ax.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "fig1_bulk_write_latency.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # ========================================================
    # FIGURE 2 — Point Lookup Latency
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    width = 0.13

    ax.bar(
        x - 2 * width,
        mysql_point_unindexed,
        width,
        label="MySQL - Unindexed",
        hatch="//",
        edgecolor="black"
    )

    ax.bar(
        x - width,
        mysql_point_indexed,
        width,
        label="MySQL - Indexed",
        edgecolor="black"
    )

    ax.bar(
        x,
        mysql_point_cached,
        width,
        label="MySQL - Warm-cache",
        hatch="..",
        edgecolor="black"
    )

    ax.bar(
        x + width,
        mongo_point_unindexed,
        width,
        label="MongoDB - Unindexed",
        hatch="//",
        edgecolor="black"
    )

    ax.bar(
        x + 2 * width,
        mongo_point_indexed,
        width,
        label="MongoDB - Indexed",
        edgecolor="black"
    )

    ax.bar(
        x + 3 * width,
        mongo_point_cached,
        width,
        label="MongoDB - Warm-cache",
        hatch="..",
        edgecolor="black"
    )

    ax.set_xlabel(
        "Dataset Size (Records)"
    )

    ax.set_ylabel(
        "Point Lookup Latency (ms)"
    )

    ax.set_title(
        "Point Lookup Latency Across Database States"
    )

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(scale_labels)

    ax.set_yscale("log")

    ax.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.7
    )

    ax.legend(
        ncol=2
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "fig2_point_lookup_latency.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # ========================================================
    # FIGURE 3 — Aggregation Latency
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(7, 4.5)
    )

    ax.plot(
        scale_labels,
        mysql_agg_unindexed,
        marker="o",
        linestyle="--",
        label="MySQL - Unindexed"
    )

    ax.plot(
        scale_labels,
        mysql_agg_indexed,
        marker="o",
        linestyle="-",
        label="MySQL - Indexed"
    )

    ax.plot(
        scale_labels,
        mysql_agg_cached,
        marker="o",
        linestyle=":",
        label="MySQL - Warm-cache"
    )

    ax.plot(
        scale_labels,
        mongo_agg_unindexed,
        marker="s",
        linestyle="--",
        label="MongoDB - Unindexed"
    )

    ax.plot(
        scale_labels,
        mongo_agg_indexed,
        marker="s",
        linestyle="-",
        label="MongoDB - Indexed"
    )

    ax.plot(
        scale_labels,
        mongo_agg_cached,
        marker="s",
        linestyle=":",
        label="MongoDB - Warm-cache"
    )

    ax.set_xlabel(
        "Dataset Size (Records)"
    )

    ax.set_ylabel(
        "Aggregation Latency (ms)"
    )

    ax.set_title(
        "Aggregation Query Latency Across Database States"
    )

    ax.set_yscale("log")

    ax.grid(
        True,
        which="both",
        linestyle="--",
        linewidth=0.5,
        alpha=0.7
    )

    ax.legend(
        ncol=2
    )

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "fig3_aggregation_latency.png"
        ),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    print()
    print("=" * 60)
    print("PHASE 3 FIGURES GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"Output directory:\n{OUTPUT_DIR}"
    )

    print()
    print("Generated figures:")
    print("  1. fig1_bulk_write_latency.png")
    print("  2. fig2_point_lookup_latency.png")
    print("  3. fig3_aggregation_latency.png")


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    generate_plots()
