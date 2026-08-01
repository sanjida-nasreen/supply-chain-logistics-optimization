"""Build and solve the mixed-integer supply-chain optimization model."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from gurobipy import GRB, Model, quicksum

from data_processing import SupplyChainData


@dataclass(frozen=True)
class OptimizationResults:
    """Structured output from the optimization model."""

    shipments: pd.DataFrame
    shortages: pd.DataFrame
    cost_summary: pd.DataFrame
    objective_value: float


def solve_supply_chain_model(
    data: SupplyChainData,
    unmet_demand_penalty: float = 1000.0,
    solver_output: bool = True,
) -> OptimizationResults:
    """
    Solve the capacity-constrained logistics allocation problem.

    The formulation follows the project report:
      - integer shipment quantities,
      - binary warehouse activation,
      - continuous unmet demand,
      - transportation, fixed operating, and shortage costs.

    Warehouse capacity is modeled with a <= constraint so an active warehouse
    may ship up to its capacity rather than being forced to use all capacity.
    """
    if unmet_demand_penalty <= 0:
        raise ValueError("unmet_demand_penalty must be greater than zero.")

    model = Model("SupplyChainLogisticsOptimization")
    model.Params.OutputFlag = 1 if solver_output else 0

    shipments = model.addVars(
        data.warehouses,
        data.destinations,
        vtype=GRB.INTEGER,
        lb=0,
        name="shipment",
    )
    warehouse_open = model.addVars(
        data.warehouses,
        vtype=GRB.BINARY,
        name="warehouse_open",
    )
    unmet_demand = model.addVars(
        data.destinations,
        vtype=GRB.CONTINUOUS,
        lb=0,
        name="unmet_demand",
    )

    transportation_cost = quicksum(
        data.transport_cost[warehouse, destination]
        * shipments[warehouse, destination]
        for warehouse in data.warehouses
        for destination in data.destinations
    )

    operating_cost = quicksum(
        data.fixed_cost[warehouse] * warehouse_open[warehouse]
        for warehouse in data.warehouses
    )

    shortage_cost = quicksum(
        unmet_demand_penalty * unmet_demand[destination]
        for destination in data.destinations
    )

    model.setObjective(
        transportation_cost + operating_cost + shortage_cost,
        GRB.MINIMIZE,
    )

    for destination in data.destinations:
        model.addConstr(
            quicksum(
                shipments[warehouse, destination]
                for warehouse in data.warehouses
            )
            + unmet_demand[destination]
            == data.demand[destination],
            name=f"demand_balance[{destination}]",
        )

    for warehouse in data.warehouses:
        model.addConstr(
            quicksum(
                shipments[warehouse, destination]
                for destination in data.destinations
            )
            <= data.capacity[warehouse] * warehouse_open[warehouse],
            name=f"warehouse_capacity[{warehouse}]",
        )

    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            "The model did not reach an optimal solution. "
            f"Gurobi status code: {model.Status}"
        )

    shipment_rows = []
    for warehouse in data.warehouses:
        for destination in data.destinations:
            quantity = shipments[warehouse, destination].X
            if quantity > 1e-6:
                shipment_rows.append(
                    {
                        "warehouse": warehouse,
                        "destination": destination,
                        "shipped_units": round(quantity),
                        "cost_per_unit": data.transport_cost[
                            warehouse, destination
                        ],
                        "transportation_cost": (
                            quantity
                            * data.transport_cost[warehouse, destination]
                        ),
                    }
                )

    shortage_rows = [
        {
            "destination": destination,
            "demand": data.demand[destination],
            "unmet_demand": unmet_demand[destination].X,
        }
        for destination in data.destinations
    ]

    total_transportation_cost = sum(
        row["transportation_cost"] for row in shipment_rows
    )
    total_operating_cost = sum(
        data.fixed_cost[warehouse] * warehouse_open[warehouse].X
        for warehouse in data.warehouses
    )
    total_shortage_cost = sum(
        unmet_demand_penalty * unmet_demand[destination].X
        for destination in data.destinations
    )

    cost_summary = pd.DataFrame(
        [
            {
                "cost_component": "Transportation cost",
                "value": total_transportation_cost,
            },
            {
                "cost_component": "Warehouse operating cost",
                "value": total_operating_cost,
            },
            {
                "cost_component": "Unmet-demand penalty",
                "value": total_shortage_cost,
            },
            {
                "cost_component": "Total objective value",
                "value": model.ObjVal,
            },
        ]
    )

    return OptimizationResults(
        shipments=pd.DataFrame(shipment_rows),
        shortages=pd.DataFrame(shortage_rows),
        cost_summary=cost_summary,
        objective_value=model.ObjVal,
    )
