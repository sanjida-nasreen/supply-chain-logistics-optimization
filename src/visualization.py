"""Create portfolio-ready figures from optimization outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_warehouse_capacity(
    capacity_data: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Create a bar chart of warehouse capacity."""
    required = {"warehouse", "capacity"}
    missing = required.difference(capacity_data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    ordered = capacity_data.sort_values("capacity", ascending=False)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(ordered["warehouse"], ordered["capacity"])
    ax.set_title("Warehouse Capacity")
    ax.set_xlabel("Warehouse")
    ax.set_ylabel("Capacity")
    ax.tick_params(axis="x", rotation=60)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_cost_summary(
    cost_summary: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """Create a bar chart of major objective-cost components."""
    required = {"cost_component", "value"}
    missing = required.difference(cost_summary.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    components = cost_summary[
        cost_summary["cost_component"] != "Total objective value"
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(components["cost_component"], components["value"])
    ax.set_title("Optimization Cost Components")
    ax.set_xlabel("Cost component")
    ax.set_ylabel("Cost")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
