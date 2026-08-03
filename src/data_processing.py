"""Load and validate supply-chain optimization input data."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class SupplyChainData:
    """Validated model inputs."""

    warehouses: list[str]
    destinations: list[str]
    demand: dict[str, float]
    capacity: dict[str, float]
    fixed_cost: dict[str, float]
    transport_cost: dict[tuple[str, str], float]


def _read_csv(path: Path, required_columns: set[str]) -> pd.DataFrame:
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
    """Load, validate, and convert four input CSV files."""
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

    for frame, key_columns in [
        (demand_df, ["destination"]),
        (capacity_df, ["warehouse"]),
        (warehouse_cost_df, ["warehouse"]),
        (transport_df, ["warehouse", "destination"]),
    ]:
        if frame.duplicated(subset=key_columns).any():
            raise ValueError(
                f"Duplicate keys found in columns: {key_columns}"
            )

    for frame, column in [
        (demand_df, "demand"),
        (capacity_df, "capacity"),
        (warehouse_cost_df, "fixed_cost"),
        (transport_df, "cost_per_unit"),
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if (frame[column] < 0).any():
            raise ValueError(f"'{column}' cannot contain negative values.")

    warehouses = capacity_df["warehouse"].astype(str).tolist()
    destinations = demand_df["destination"].astype(str).tolist()

    missing_fixed_costs = set(warehouses).difference(
        warehouse_cost_df["warehouse"].astype(str)
    )
    if missing_fixed_costs:
        raise ValueError(
            f"Missing fixed costs for: {sorted(missing_fixed_costs)}"
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
        raise ValueError(
            "Transportation-cost matrix is incomplete. "
            f"Example missing routes: {sorted(missing_routes)[:5]}"
        )

    return SupplyChainData(
        warehouses=warehouses,
        destinations=destinations,
        demand=dict(
            zip(
                demand_df["destination"].astype(str),
                demand_df["demand"].astype(float),
            )
        ),
        capacity=dict(
            zip(
                capacity_df["warehouse"].astype(str),
                capacity_df["capacity"].astype(float),
            )
        ),
        fixed_cost=dict(
            zip(
                warehouse_cost_df["warehouse"].astype(str),
                warehouse_cost_df["fixed_cost"].astype(float),
            )
        ),
        transport_cost={
            (str(row.warehouse), str(row.destination)): float(row.cost_per_unit)
            for row in transport_df.itertuples(index=False)
        },
    )
