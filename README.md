# Supply Chain Logistics Network Optimization using Mixed-Integer Programming

A Mixed-Integer Programming (MIP) model for optimizing shipment allocation in a capacity-constrained supply chain network. The model minimizes transportation cost, warehouse operating cost, and unmet-demand penalties while determining an optimal shipment plan under limited warehouse capacity.

**Technologies:** Python • Gurobi • Pandas • NumPy • Matplotlib

---

# Project Overview

Supply chain networks must continuously balance transportation cost, warehouse utilization, and customer demand. In practice, warehouse capacity is often insufficient to satisfy all demand, requiring companies to determine how limited resources should be allocated to minimize overall logistics cost.

This project formulates the problem as a Mixed-Integer Programming (MIP) optimization model that determines:

- Which warehouses should operate
- How much each warehouse should ship
- Which destinations receive available inventory
- How unmet demand should be managed when total demand exceeds available capacity

The model produces an optimal shipment allocation while satisfying operational constraints.

---

# Business Problem

Consider a logistics network consisting of multiple warehouses with different operating costs and daily shipping capacities.

Customer demand exceeds the total available warehouse capacity, making it impossible to satisfy every order.

The objective is to answer several key business questions:

- Which warehouses should operate?
- How should limited inventory be allocated?
- Which shipment routes minimize transportation cost?
- How should shortages be distributed across destinations?
- What is the minimum achievable total logistics cost?

The optimization model provides an analytical decision-support tool for answering these questions.

---

# Optimization Model

The problem is formulated as a Mixed-Integer Programming model.

## Decision Variables

- Shipment quantity from each warehouse to each destination
- Warehouse activation (open or closed)
- Unfulfilled demand at each destination

## Objective

Minimize total logistics cost consisting of:

- Transportation cost
- Warehouse operating cost
- Penalty cost for unmet demand

## Constraints

- Demand balance
- Warehouse capacity
- Warehouse activation
- Non-negativity
- Integer shipment quantities

---

# Data Processing

The original dataset required several preprocessing steps before optimization.

These included:

- Cleaning and standardizing logistics data
- Aggregating demand information
- Processing warehouse capacities
- Processing warehouse operating costs
- Building transportation cost matrices

### Public Repository Note

The original dataset did not contain transportation costs for every warehouse–destination combination.

To construct a complete optimization model, missing transportation costs were estimated using a consistent cost-scaling approach based on the lowest available transportation cost. This assumption is documented to make the model reproducible while acknowledging the limitations of the available data.

The public version of this repository will use anonymized or synthetic sample data while preserving the optimization framework.

---

# Repository Structure

```
supply-chain-logistics-optimization/

├── data/
│
├── docs/
│
├── notebooks/
│
├── results/
│
├── src/
│   ├── data_processing.py
│   ├── optimization_model.py
│   ├── visualization.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Results

The optimization model successfully:

- Allocated all available warehouse capacity
- Determined an optimal shipment plan
- Minimized transportation and warehouse operating costs
- Quantified unmet demand under severe capacity limitations
- Generated shipment decisions suitable for further logistics analysis

Visualizations included in this repository illustrate:

- Warehouse capacities
- Transportation network
- Shipment allocation
- Optimized logistics network

---

# Key Insights

Several observations emerged from the optimization study:

- Total warehouse capacity was substantially smaller than total demand, making shortages unavoidable.
- Transportation cost optimization alone cannot eliminate shortages when capacity is insufficient.
- Capacity constraints dominate overall network performance.
- Mathematical optimization provides a systematic approach for prioritizing shipments when resources are limited.

---

# Technologies

- Python
- Gurobi Optimizer
- Pandas
- NumPy
- Matplotlib
- Jupyter Notebook

---

# Future Improvements

Potential extensions include:

- Multi-period planning
- Inventory decisions
- Demand uncertainty
- Stochastic optimization
- Robust optimization
- Carbon-emission objectives
- Service-level constraints
- Dynamic transportation costs

---

# References

This project was developed as part of graduate coursework in Supply Chain Systems at the University of Washington.

The repository has been reorganized into a reusable engineering project with modular code and documentation.
