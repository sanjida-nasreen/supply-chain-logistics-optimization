"""Load and validate supply-chain optimization input data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class SupplyChainData:
    """Container for validated optimization inputs."""

    destinations: list[str]
    warehouses: list[str]
    demand: dict[str, float]
    capacity: dict[str, float]
    fixed_cost: dict[str, float]
    transport_cost: dict[tuple[str, str], float]


def _read_csv(path: Path, required_columns: set[str]) -> pd.DataFrame:
    """Read a CSV file and verify that required columns are present."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    frame = pd.read_csv(path)
    missing = required_columns.difference(frame.columns)

    if missing:
        raise ValueError(
            f"{path.name} is missing required columns: {sorted(missing)}"
        )

    return frame


def load_supply_chain_data(data_dir: str | Path) -> SupplyChainData:
    """
    Load processed supply-chain data from four CSV files.

    Expected files
    --------------
    demand.csv
        destination, demand

    warehouse_capacity.csv
        warehouse, capacity

    warehouse_cost.csv
        warehouse, fixed_cost

    transport_cost.csv
        warehouse, destination, cost_per_unit
    """
    data_path = Path(data_dir)

    demand_df = _read_csv(
        data_path / "demand.csv",
        {"destination", "demand"},
    )
    capacity_df = _read_csv(
        data_path / "warehouse_capacity.csv",
        {"warehouse", "capacity"},
    )
    warehouse_cost_df = _read_csv(
        data_path / "warehouse_cost.csv",
        {"warehouse", "fixed_cost"},
    )
    transport_df = _read_csv(
        data_path / "transport_cost.csv",
        {"warehouse", "destination", "cost_per_unit"},
    )

    # Remove duplicate keys to prevent ambiguous dictionary values.
    demand_df = demand_df.drop_duplicates(subset=["destination"], keep="last")
    capacity_df = capacity_df.drop_duplicates(subset=["warehouse"], keep="last")
    warehouse_cost_df = warehouse_cost_df.drop_duplicates(
        subset=["warehouse"], keep="last"
    )
    transport_df = transport_df.drop_duplicates(
        subset=["warehouse", "destination"], keep="last"
    )

    numeric_checks = [
        (demand_df, "demand"),
        (capacity_df, "capacity"),
        (warehouse_cost_df, "fixed_cost"),
        (transport_df, "cost_per_unit"),
    ]

    for frame, column in numeric_checks:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if (frame[column] < 0).any():
            raise ValueError(f"Column '{column}' cannot contain negative values.")

    destinations = demand_df["destination"].astype(str).tolist()
    warehouses = capacity_df["warehouse"].astype(str).tolist()

    missing_warehouse_costs = set(warehouses).difference(
        warehouse_cost_df["warehouse"].astype(str)
    )
    if missing_warehouse_costs:
        raise ValueError(
            "Missing fixed costs for warehouses: "
            f"{sorted(missing_warehouse_costs)}"
        )

    expected_routes = {
        (warehouse, destination)
        for warehouse in warehouses
        for destination in destinations
    }
    available_routes = set(
        zip(
            transport_df["warehouse"].astype(str),
            transport_df["destination"].astype(str),
        )
    )
    missing_routes = expected_routes.difference(available_routes)

    if missing_routes:
        preview = sorted(missing_routes)[:10]
        raise ValueError(
            "Transportation-cost matrix is incomplete. "
            f"Example missing routes: {preview}"
        )

    demand = dict(
        zip(
            demand_df["destination"].astype(str),
            demand_df["demand"].astype(float),
        )
    )
    capacity = dict(
        zip(
            capacity_df["warehouse"].astype(str),
            capacity_df["capacity"].astype(float),
        )
    )
    fixed_cost = dict(
        zip(
            warehouse_cost_df["warehouse"].astype(str),
            warehouse_cost_df["fixed_cost"].astype(float),
        )
    )
    transport_cost = {
        (str(row.warehouse), str(row.destination)): float(row.cost_per_unit)
        for row in transport_df.itertuples(index=False)
    }

    return SupplyChainData(
        destinations=destinations,
        warehouses=warehouses,
        demand=demand,
        capacity=capacity,
        fixed_cost=fixed_cost,
        transport_cost=transport_cost,
    )
