"""Generate a synthetic dataset that mirrors the structure of the original.

The coursework used the Supply Chain Logistics Problem Dataset (Kalganova &
Dzalbs, 2019, Brunel University London, https://doi.org/10.17633/rd.brunel.7558679).
That dataset is not redistributed here. This generator produces a synthetic
substitute reproducing the three structural features that drive the original
result, so the model behaves the same way:

1. Demand vastly exceeds capacity.
   Original: 29,513,315 units of demand against 5,791 units of daily capacity
   (0.02%). The binding question is not which warehouses to open -- every
   warehouse runs flat out -- but which lanes the scarce units travel on.

2. Demand is extremely concentrated.
   Original: a single destination accounts for 96.9% of all demand.

3. Most transportation costs are imputed, not observed.
   Original: 133 of 143 lanes carry the same imputed rate (1.2x the cheapest
   observed rate), because the raw freight table prices only a handful of
   lanes. With most lanes priced identically, routing choice has limited
   leverage -- which is why optimization yields a single-digit percentage
   saving rather than a dramatic one.

Feature 3 is the one that is easy to get wrong. A generator giving every lane
its own distance-based cost creates far more routing headroom than the real
data had, and inflates the apparent value of optimization.
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).resolve().parent
RANDOM_SEED = 570

N_DESTINATIONS = 7

# Heavy-tailed capacities summing to 5,791, matching the original spread
# (two large sites, a long tail of small ones).
CAPACITIES = [
    1070, 1013, 554, 549, 490, 457, 385, 332, 265, 209,
    138, 118, 111, 49, 14, 11, 11, 8, 7,
]

# Demand shares mirroring the original concentration (96.9% at one node).
DEMAND_SHARES = [0.9694, 0.0094, 0.0083, 0.0076, 0.0038, 0.0015, 0.0000]
TOTAL_DEMAND = 29_513_315

# Fraction of lanes with an observed freight rate. The rest are imputed at
# IMPUTE_MULTIPLIER x the cheapest observed rate, as the original pipeline did.
OBSERVED_LANE_FRACTION = 0.07
IMPUTE_MULTIPLIER = 1.2


def main() -> None:
    rng = random.Random(RANDOM_SEED)

    warehouses = [f"WH{i:02d}" for i in range(1, len(CAPACITIES) + 1)]
    destinations = [f"DEST{i:02d}" for i in range(1, N_DESTINATIONS + 1)]

    # ---- demand: concentrated, far above total capacity --------------------
    demand = [round(TOTAL_DEMAND * share) for share in DEMAND_SHARES]
    demand[0] += TOTAL_DEMAND - sum(demand)  # absorb rounding

    # ---- warehouse fixed operating cost ------------------------------------
    fixed_cost = [round(rng.uniform(0.4, 1.6), 4) for _ in warehouses]

    # ---- transportation cost -----------------------------------------------
    # A small set of lanes gets an observed rate; everything else is imputed
    # at a single shared value, exactly as the original preprocessing did.
    lanes = [(w, d) for w in warehouses for d in destinations]
    n_observed = max(2, round(len(lanes) * OBSERVED_LANE_FRACTION))
    # Keep the sample as an ordered list. Iterating a set of strings would
    # assign rates in a hash-dependent order and break reproducibility.
    observed_lanes = rng.sample(lanes, n_observed)

    observed_rates = {
        lane: round(rng.uniform(0.11, 0.55), 6) for lane in observed_lanes
    }
    imputed_rate = round(min(observed_rates.values()) * IMPUTE_MULTIPLIER, 6)

    transport_rows = [
        {
            "warehouse": w,
            "destination": d,
            "cost_per_unit": observed_rates.get((w, d), imputed_rate),
        }
        for w, d in lanes
    ]

    # ---- write -------------------------------------------------------------
    pd.DataFrame({"destination": destinations, "demand": demand}).to_csv(
        OUTPUT_DIR / "demand.csv", index=False
    )
    pd.DataFrame({"warehouse": warehouses, "capacity": CAPACITIES}).to_csv(
        OUTPUT_DIR / "warehouse_capacity.csv", index=False
    )
    pd.DataFrame({"warehouse": warehouses, "fixed_cost": fixed_cost}).to_csv(
        OUTPUT_DIR / "warehouse_cost.csv", index=False
    )
    pd.DataFrame(transport_rows).to_csv(
        OUTPUT_DIR / "transport_cost.csv", index=False
    )

    n_vars = len(warehouses) * len(destinations) + len(warehouses) + len(destinations)
    print(f"Synthetic data saved to: {OUTPUT_DIR}")
    print(f"  warehouses         {len(warehouses):>14}")
    print(f"  destinations       {len(destinations):>14}")
    print(f"  total demand       {sum(demand):>14,}")
    print(f"  total capacity     {sum(CAPACITIES):>14,}")
    print(f"  capacity / demand  {sum(CAPACITIES)/sum(demand)*100:>13.2f}%")
    print(f"  lanes              {len(lanes):>14}")
    print(f"  observed rates     {n_observed:>14}")
    print(f"  imputed rate       {imputed_rate:>14}")
    print(f"  model size         {n_vars:>14} variables")


if __name__ == "__main__":
    main()
