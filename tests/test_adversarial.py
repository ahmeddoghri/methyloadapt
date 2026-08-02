import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import methyloadapt
import methyloadapt_v2
from adversarial import HOLDOUT_SEEDS, TUNING_SEEDS
from eval_v2 import summarize


class AdversarialTest(unittest.TestCase):
    def test_holdout_disjoint_from_tuning(self):
        self.assertTrue(set(TUNING_SEEDS).isdisjoint(HOLDOUT_SEEDS))

    def test_original_benchmark_still_reproduces_exactly(self):
        result = methyloadapt.run()
        self.assertEqual(result["target_only_accuracy"], 0.5)
        self.assertEqual(result["adapted_accuracy"], 1.0)
        self.assertEqual(result["accuracy_gain_pct"], 50.0)

    def test_original_bug_published_seed_is_a_lucky_outlier(self):
        """methyloadapt.py's raw-vote-count adaptation trains on
        source + target_train*4: source (360 examples, motif "ACG") swamps
        the oversampled target (24 examples, motif "GCG"). The published
        seed=17 gain of 50pp is far above the typical result: across 60
        tuning seeds the median gain is close to 0 and some seeds are
        actively worse than the target-only baseline."""
        result = summarize(TUNING_SEEDS)
        self.assertLess(result["original_median_gain_pct"], 10)
        self.assertGreater(result["original_seeds_worse_than_target_only"], 0)

    def test_v2_fix_never_regresses_below_target_only_on_tuning_seeds(self):
        result = summarize(TUNING_SEEDS)
        self.assertEqual(result["v2_seeds_worse_than_target_only"], 0)
        self.assertGreater(result["v2_median_gain_pct"], result["original_median_gain_pct"])

    def test_v2_fix_never_regresses_below_target_only_on_frozen_holdout_seeds(self):
        result = summarize(HOLDOUT_SEEDS)
        self.assertEqual(result["v2_seeds_worse_than_target_only"], 0)
        self.assertGreater(result["v2_median_gain_pct"], result["original_median_gain_pct"])

    def test_v2_does_not_regress_the_original_published_seed(self):
        result = methyloadapt_v2.run(seed=17)
        self.assertEqual(result["accuracy_gain_pct"], 50.0)

    def test_original_module_untouched(self):
        import inspect

        source = inspect.getsource(methyloadapt.run)
        self.assertIn("adapted=train(source+target_train*4)", source)

    def test_report_is_reproducible(self):
        a = summarize(TUNING_SEEDS[:5])
        b = summarize(TUNING_SEEDS[:5])
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
