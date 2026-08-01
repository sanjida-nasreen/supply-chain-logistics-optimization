# Supply Chain Logistics Network Optimization using Mixed-Integer Programming

A mixed-integer optimization model for allocating limited supply capacity across a logistics network while minimizing transportation, facility operating, and unmet-demand costs.

## Project Overview

Supply chain networks must determine how available capacity should be allocated across multiple destinations while balancing transportation expenses, facility costs, and customer demand.

This project develops a mixed-integer programming model that determines:

- Which facilities should operate
- How much product should be shipped between locations
- How limited capacity should be allocated
- How unmet demand should be handled when total demand exceeds supply

The model was implemented in Python and solved using Gurobi.

## Business Problem

The network contains multiple supply locations and demand locations. Each supply location has limited capacity and may incur a fixed operating cost. Transportation costs vary by origin-destination pair.

Because total demand may exceed available capacity, the model includes an unmet-demand variable with a penalty cost.

The objective is to identify the allocation strategy that minimizes total network cost while satisfying operational constraints.

## Methodology

The optimization model includes:

### Decision Variables

- Shipment quantity between each origin and destination
- Binary facility operating decisions
- Unmet demand at each destination

### Objective Function

Minimize:

- Transportation cost
- Fixed facility operating cost
- Unmet-demand penalty

### Constraints

- Demand balance
- Supply capacity
- Facility activation
- Non-negativity and integrality

## Technologies Used

- Python
- Gurobi
- pandas
- NumPy
- Matplotlib
- Jupyter Notebook

## Repository Structure

```text
data/        Sample input data
notebooks/   Main optimization analysis
src/         Reusable Python modules
results/     Model outputs and visualizations
docs/        Mathematical model documentation
