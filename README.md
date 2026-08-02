# methyloadapt

**Cross-species DNA methylation prediction that transfers motifs before labels run out.**

You can't run a proper methylation study on a species with six labeled samples. There just aren't enough examples to learn a motif from scratch, and pretending otherwise is how you get a model that's memorized six data points and calls it biology. methyloadapt doesn't wait for the target species to have enough labels — it pretrains on related species where labels are plentiful, then fine-tunes on the handful the target species actually has, so six samples are a starting point instead of the entire dataset.

It's a compact, inspectable implementation inspired by [the 2025 iDNA-DAPHA work on domain-adaptive pretraining for methylation prediction](https://academic.oup.com/bib/article/26/6/bbaf642/8374030), rebuilt small enough to read in one sitting and run without a GPU, a checkpoint, or an API key.

## The result

```bash
python methyloadapt.py
```
```json
{
  "target_only_accuracy": 0.5,
  "adapted_accuracy": 1.0,
  "accuracy_gain_pct": 50.0
}
```

Train only on the target species' 6 labeled sequences and you get a coin flip: 50% accuracy, because six examples isn't a model, it's a guess with extra steps. Pretrain on 360 labeled sequences from two related species, then fine-tune with the target's 6 examples oversampled into the mix, and accuracy hits 100% on 160 held-out target-species sequences — a 50 percentage-point gain from data the target species never had to produce.

**Update:** that 50-point gain is a lucky outlier, not a typical result.
`adapted` trains on raw vote counts (`source + target_train*4`), so
source's 360 examples numerically swamp target's oversampled 24 — and
source (species 0/1) uses a different positive motif ("ACG") than target
(species 2, "GCG"). Across 60 seeds, the median gain is close to 0, and on
some seeds `adapted` is measurably *worse* than the target-only baseline.
`methyloadapt_v2.py` normalizes each domain's vote profile before
combining them with an explicit weight instead of raw counts, which never
regresses below target-only across 60 tuning + 30 disjoint holdout seeds
(median gain ~47-49pp). Details below.

## How it works

Each species has its own dominant methylation motif embedded in an otherwise random sequence. The model is a k-mer count classifier: score each 2-mer by how often it appears in positive vs. negative examples, then sum scores at prediction time. `target_only` trains on six target-species examples alone. `adapted` trains on the pooled source-species examples plus the same six target examples, oversampled so they still get a real vote. No transformer, no pretraining checkpoint — just the actual transfer-learning claim (more data from related domains beats too little data from the right one) made checkable in twenty lines.

## Run it

```bash
python methyloadapt.py
python -m unittest discover -s tests -v
```

## What is tested

The test compares domain-adapted accuracy against the target-only baseline and requires `accuracy_gain_pct >= 15`. The data generator is seeded, so the number in this README, in CI, and in the portfolio case study are the same number, not three different ones that happen to rhyme.

## Scope

This is an educational research reproduction on controlled synthetic sequences and synthetic motifs. It is not a clinical, diagnostic, production genomics, or safety-critical system, and it makes no claim about real cross-species methylation data. The point is to make one mechanism — related-domain pretraining beats scarce in-domain labels — measurable without hiding it behind a checkpoint.

## The published gain was a lucky seed, not a typical one

`adapted=train(source+target_train*4)` counts raw votes: source contributes
360 examples, oversampled target contributes 24 — target's signal is easily
swamped. Worse, source species (0, 1) share positive motif `"ACG"` while
target species (2) uses `"GCG"` — a different motif, so source's dominant
signal doesn't reliably point at the right answer for target at all.

```bash
python eval_v2.py
```
```
tuning (60 seeds):  original_median_gain_pct=1.2   original_worse_count=5    v2_median_gain_pct=49.1   v2_worse_count=0
holdout (30 seeds): original_median_gain_pct=3.75  original_worse_count=1    v2_median_gain_pct=46.55  v2_worse_count=0
```

The published `seed=17` (50pp gain) sits far above the typical outcome:
across 60 tuning seeds the *median* gain is 1.2 points, and 5 of 60 seeds
show `adapted` doing measurably worse than the target-only baseline (worst
case -16.9pp). A disjoint 30-seed holdout, evaluated once, confirms it:
median 3.75pp, 1 seed worse.

`methyloadapt_v2.py`'s `train_weighted_domains` trains source and target as
separately normalized (per-example averaged) vote profiles, then combines
them with an explicit domain weight instead of raw counts, so target's
signal can no longer be numerically drowned out. Across both the same 60
tuning seeds and the disjoint 30-seed holdout, it never regresses below the
target-only baseline (0 seeds worse on either sweep) and holds a median
gain of 46.6-49.1 points. `methyloadapt.py` is untouched and the published
50.0pp number still reproduces exactly.

## Research basis

- [The 2025 iDNA-DAPHA work on domain-adaptive pretraining for methylation prediction](https://academic.oup.com/bib/article/26/6/bbaf642/8374030)
- Original implementation and benchmark in this repository are MIT licensed.

## License

MIT
