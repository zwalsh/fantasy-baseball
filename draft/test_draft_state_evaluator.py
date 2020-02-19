from unittest import TestCase

from draft.draft_state_evaluator import rank_values


class TestDraftStateEvaluator(TestCase):
    def test_rank_values_single_value(self):
        self.assertEqual(rank_values([1.0], False), [1.0])

    def test_rank_values_simple(self):
        self.assertEqual(rank_values([1.0, 2.0], False), [1.0, 2.0])
        self.assertEqual(rank_values([2.0, 1.0], False), [2.0, 1.0])

    def test_rank_values_revers(self):
        self.assertEqual(rank_values([2.0, 1.0], True), [1.0, 2.0])

    def test_rank_values_four_numbers(self):
        self.assertEqual(rank_values([0.5, 0.4, 0.3, 0.6], False), [3.0, 2.0, 1.0, 4.0])

    def test_rank_values_ties(self):
        self.assertEqual(rank_values([1.0, 1.0], False), [1.5, 1.5])
        self.assertEqual(rank_values([1.0, 1.0, 1.0, 1.0, 2.0], False), [2.5, 2.5, 2.5, 2.5, 5.0])
