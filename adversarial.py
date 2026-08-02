"""Adversarial seeds for the domain-weighted adaptation fix.

TUNING_SEEDS: used to characterize methyloadapt.py's instability and tune
methyloadapt_v2.py's fix.
HOLDOUT_SEEDS: disjoint, evaluated exactly once after the fix was finalized.
"""

TUNING_SEEDS = list(range(1, 61))
HOLDOUT_SEEDS = list(range(1000, 1030))
