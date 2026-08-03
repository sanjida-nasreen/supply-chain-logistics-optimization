"""Build and solve the logistics mixed-integer program with Gurobi."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from gurobipy import GRB, Model, quicksum

from data_processing import SupplyChainData


@dataclass(frozen=True)
class OptimizationResults:
    shipments: pd.DataFrame
    shortages: pd.DataFrame
    cost_summary: pd.DataFrame
    objective_value: float


def solve_supply_chain_model(
    data: SupplyChainData,
    unmet_demand_penalty: float = 1000.0,
    solver_output: bool = True,
) -> OptimizationResults:
    """Solve the capacity-constrained shipment-allocation problem."""
    if unmet_demand_penalty <= 0:
        raise ValueError("unmet_demand_penalty must be positive.")

    model = Model("SupplyChainLogisticsOptimization")
    model.Params.OutputFlag = 1 if solver_output else 0

    shipment = model.addVars(
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

    model.setObjective(
        quicksum(
            data.transport_cost[warehouse, destination]
            * shipment[warehouse, destination]
            for warehouse in data.warehouses
            for destination in data.destinations
        )
        + quicksum(
            data.fixed_cost[warehouse] * warehouse_open[warehouse]
            for warehouse in data.warehouses
        )
        + quicksum(
            unmet_demand_penalty * unmet_demand[destination]
            for destination in data.destinations
        ),
        GRB.MINIMIZE,
    )

    for destination in data.destinations:
        model.addConstr(
            quicksum(
                shipment[warehouse, destination]
                for warehouse in data.warehouses
            )
            + unmet_demand[destination]
            == data.demand[destination],
            name=f"demand_balance[{destination}]",
        )

    for warehouse in data.warehouses:
        model.addConstr(
            quicksum(
                shipment[warehouse, destination]
                for destination in data.destinations
            )
            <= data.capacity[warehouse] * warehouse_open[warehouse],
            name=f"capacity[{warehouse}]",
        )

    model.optimize()

    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"Optimal solution not found. Gurobi status: {model.Status}"
        )

    shipment_rows = []
    for warehouse in data.warehouses:
        for destination in data.destinations:
            quantity = shipment[warehouse, destination].X
            if quantity > 1e-6:
                unit_cost = data.transport_cost[warehouse, destination]
                shipment_rows.append(
                    {
                        "warehouse": warehouse,
                        "destination": destination,
                        "shipped_units": round(quantity),
                        "cost_per_unit": unit_cost,
                        "transportation_cost": quantity * unit_cost,
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
