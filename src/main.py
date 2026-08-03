"""Run data loading, optimization, result export, and visualization."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from baseline import compare, compute_baseline
from data_processing import load_supply_chain_data
from optimization_model import solve_supply_chain_model
from visualization import (
    plot_cost_summary,
    plot_shipment_allocation,
    plot_warehouse_capacity,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = RESULTS_DIR / "figures"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_supply_chain_data(DATA_DIR)
    results = solve_supply_chain_model(
        data=data,
        unmet_demand_penalty=1000.0,
        solver_output=True,
    )

    results.shipments.to_csv(
        RESULTS_DIR / "optimized_shipments.csv",
        index=False,
    )
    results.shortages.to_csv(
        RESULTS_DIR / "unmet_demand.csv",
        index=False,
    )
    results.cost_summary.to_csv(
        RESULTS_DIR / "cost_summary.csv",
        index=False,
    )

    baseline = compute_baseline(data)
    optimized_transport = float(
        results.shipments["transportation_cost"].sum()
    )
    comparison = compare(baseline, optimized_transport)
    comparison.to_csv(RESULTS_DIR / "baseline_comparison.csv", index=False)

    capacity_data = pd.DataFrame(
        {
            "warehouse": data.warehouses,
            "capacity": [
                data.capacity[warehouse]
                for warehouse in data.warehouses
            ],
        }
    )

    plot_warehouse_capacity(
        capacity_data,
        FIGURES_DIR / "warehouse_capacity.png",
    )
    plot_cost_summary(
        results.cost_summary,
        FIGURES_DIR / "cost_breakdown.png",
    )
    plot_shipment_allocation(
        results.shipments,
        FIGURES_DIR / "shipment_allocation.png",
    )

    print("\nOptimization completed successfully.")
    print(f"Objective value: {results.objective_value:,.2f}")
    print(
        f"Transportation cost: {baseline.transportation_cost:,.2f} (baseline) "
        f"-> {optimized_transport:,.2f} (optimized), "
        f"{comparison.iloc[3]['transportation_cost']:.1f}% saving"
    )
    print(f"Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
