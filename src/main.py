"""Run the supply-chain logistics optimization workflow."""

from __future__ import annotations

from pathlib import Path

from data_processing import load_supply_chain_data
from optimization_model import solve_supply_chain_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"


def main() -> None:
    """Load inputs, solve the model, and save result tables."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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

    print("\nOptimization completed successfully.")
    print(f"Objective value: {results.objective_value:,.2f}")
    print(f"Results saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
