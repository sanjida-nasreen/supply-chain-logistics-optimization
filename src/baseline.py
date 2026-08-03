"""Cost of a naive allocation, used as the comparison point for optimization.

The optimization result only means something against an alternative. This
module implements the allocation a planner would produce without an optimizer:
work through destinations in order, and fill each one from whichever warehouse
still has capacity, ignoring transportation cost entirely.

Capacity is consumed in exactly the same way as in the optimized solution, so
the two scenarios ship the same total units and open the same warehouses. The
only difference is *which lane* each unit travels on, which isolates the value
of the routing decision.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from data_processing import SupplyChainData


@dataclass(frozen=True)
class BaselineResults:
    shipments: pd.DataFrame
    transportation_cost: float
    operating_cost: float
    unmet_demand: float


def compute_baseline(data: SupplyChainData) -> BaselineResults:
    """Allocate demand to warehouses in list order, ignoring cost."""
    remaining_capacity = {w: data.capacity[w] for w in data.warehouses}
    rows: list[dict[str, object]] = []
    unmet_total = 0.0
    warehouses_used: set[str] = set()

    for destination in data.destinations:
        outstanding = data.demand[destination]

        for warehouse in data.warehouses:
            if outstanding <= 0:
                break
            available = remaining_capacity[warehouse]
            if available <= 0:
                continue

            shipped = min(available, outstanding)
            remaining_capacity[warehouse] -= shipped
            outstanding -= shipped
            warehouses_used.add(warehouse)

            unit_cost = data.transport_cost[warehouse, destination]
            rows.append(
                {
                    "warehouse": warehouse,
                    "destination": destination,
                    "shipped_units": round(shipped),
                    "cost_per_unit": unit_cost,
                    "transportation_cost": shipped * unit_cost,
                }
            )

        unmet_total += max(outstanding, 0.0)

    return BaselineResults(
        shipments=pd.DataFrame(rows),
        transportation_cost=sum(r["transportation_cost"] for r in rows),
        operating_cost=sum(data.fixed_cost[w] for w in warehouses_used),
        unmet_demand=unmet_total,
    )


def compare(
    baseline: BaselineResults,
    optimized_transportation_cost: float,
) -> pd.DataFrame:
    """Tabulate baseline against optimized transportation cost."""
    saving = baseline.transportation_cost - optimized_transportation_cost
    pct = (
        saving / baseline.transportation_cost * 100
        if baseline.transportation_cost
        else 0.0
    )

    return pd.DataFrame(
        [
            {"scenario": "Baseline (no cost optimization)",
             "transportation_cost": baseline.transportation_cost},
            {"scenario": "Optimized (MIP)",
             "transportation_cost": optimized_transportation_cost},
            {"scenario": "Saving", "transportation_cost": saving},
            {"scenario": "Saving (%)", "transportation_cost": pct},
        ]
    )
