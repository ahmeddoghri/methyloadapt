"""Domain-weighted adaptation, as a parallel non-destructive fix.

methyloadapt.py's `adapted` model trains on `source + target_train*4`: raw
vote counts, where source contributes 360 examples and the oversampled
target contributes 24. Two problems compound: (1) target's vote share is
tiny and easily swamped by source, and (2) source species (0,1) use a
different positive motif ("ACG") than the target species (2, "GCG"), so
source's dominant signal doesn't even point at the right answer for target.
The published seed=17 result (50pp gain, 100% adapted accuracy) turns out to
be a lucky outlier: across many seeds, the median gain is close to 0, and on
some seeds adapted is measurably *worse* than target-only.

This module trains source and target as separately normalized (per-example
averaged) k-mer vote profiles, then combines them with an explicit domain
weight instead of raw counts, so target's signal can't be numerically
drowned out by source's larger sample size.
"""
import json
import random


def features(seq):
    return {seq[i:i + 2] for i in range(len(seq) - 1)}


def train_normalized(rows):
    pos = sum(1 for _, y in rows if y)
    neg = len(rows) - pos
    score = {}
    for seq, y in rows:
        for k in features(seq):
            score[k] = score.get(k, 0) + (1.0 / pos if y else -1.0 / neg)
    return score


def train_weighted_domains(source_rows, target_rows, target_weight=0.5):
    src_score = train_normalized(source_rows)
    tgt_score = train_normalized(target_rows)
    keys = set(src_score) | set(tgt_score)
    return {k: (1 - target_weight) * src_score.get(k, 0) + target_weight * tgt_score.get(k, 0) for k in keys}


def predict(model, seq):
    return sum(model.get(k, 0) for k in features(seq)) >= 0


def _sample(rng, species, n):
    rows = []
    for _ in range(n):
        y = rng.random() < .5
        s = [rng.choice("AT") for _ in range(25)]
        motif = ("ACG" if species < 2 else "GCG") if y else "TTA"
        pos = rng.randrange(4, 18)
        s[pos:pos + 3] = motif
        rows.append(("".join(s), y))
    return rows


def run(seed=17, target_weight=0.5):
    rng = random.Random(seed)
    source = _sample(rng, 0, 180) + _sample(rng, 1, 180)
    target_train = _sample(rng, 2, 6)
    test = _sample(rng, 2, 160)
    local = train_normalized(target_train)
    adapted = train_weighted_domains(source, target_train, target_weight)
    a = sum(predict(local, x) == y for x, y in test) / len(test)
    b = sum(predict(adapted, x) == y for x, y in test) / len(test)
    return {
        "target_only_accuracy": round(a, 3),
        "adapted_accuracy": round(b, 3),
        "accuracy_gain_pct": round(100 * (b - a), 1),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
