"""Generate figures from model inputs and optimization results."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_warehouse_capacity(
    capacity_data: pd.DataFrame,
    output_path: str | Path,
) -> None:
    ordered = capacity_data.sort_values("capacity", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(ordered["warehouse"], ordered["capacity"])
    ax.set_title("Warehouse Capacity")
    ax.set_xlabel("Warehouse")
    ax.set_ylabel("Capacity (units)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_cost_summary(
    cost_summary: pd.DataFrame,
    output_path: str | Path,
) -> None:
    components = cost_summary[
        cost_summary["cost_component"] != "Total objective value"
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(components["cost_component"], components["value"])
    ax.set_title("Optimized Cost Components")
    ax.set_xlabel("Cost component")
    ax.set_ylabel("Cost")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_shipment_allocation(
    shipments: pd.DataFrame,
    output_path: str | Path,
) -> None:
    if shipments.empty:
        raise ValueError(
            "No shipments to plot. The model routed nothing, which usually "
            "means the unmet-demand penalty is lower than the cheapest "
            "transportation cost."
        )

    pivot = shipments.pivot_table(
        index="warehouse",
        columns="destination",
        values="shipped_units",
        aggfunc="sum",
        fill_value=0,
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    image = ax.imshow(pivot.values, aspect="auto")
    ax.set_title("Optimized Shipment Allocation")
    ax.set_xlabel("Destination")
    ax.set_ylabel("Warehouse")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    for row in range(pivot.shape[0]):
        for column in range(pivot.shape[1]):
            value = int(pivot.iloc[row, column])
            if value:
                ax.text(column, row, str(value), ha="center", va="center")

    fig.colorbar(image, ax=ax, label="Shipped units")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
