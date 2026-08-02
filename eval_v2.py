"""Compare methyloadapt.py's raw-vote-count adaptation to methyloadapt_v2.py's
domain-weighted adaptation across many seeds, showing the published seed=17
result (50pp gain) is a lucky outlier, not a typical outcome."""
import json
import statistics as st

import methyloadapt
import methyloadapt_v2
from adversarial import HOLDOUT_SEEDS, TUNING_SEEDS


def summarize(seeds):
    original_gains = [methyloadapt.run(seed=seed)["accuracy_gain_pct"] for seed in seeds]
    v2_gains = [methyloadapt_v2.run(seed=seed)["accuracy_gain_pct"] for seed in seeds]
    return {
        "n": len(seeds),
        "original_mean_gain_pct": round(st.mean(original_gains), 2),
        "original_median_gain_pct": round(st.median(original_gains), 2),
        "original_min_gain_pct": min(original_gains),
        "original_seeds_worse_than_target_only": sum(1 for g in original_gains if g < 0),
        "v2_mean_gain_pct": round(st.mean(v2_gains), 2),
        "v2_median_gain_pct": round(st.median(v2_gains), 2),
        "v2_min_gain_pct": min(v2_gains),
        "v2_seeds_worse_than_target_only": sum(1 for g in v2_gains if g < 0),
    }


def main():
    print("methyloadapt eval_v2: raw-count adaptation vs. domain-weighted adaptation")
    print(f"published seed=17: {methyloadapt.run(seed=17)}")
    for label, seeds in (("tuning", TUNING_SEEDS), ("holdout", HOLDOUT_SEEDS)):
        print(f"\n{label} ({len(seeds)} seeds):")
        print(json.dumps(summarize(seeds), indent=2))


if __name__ == "__main__":
    main()
