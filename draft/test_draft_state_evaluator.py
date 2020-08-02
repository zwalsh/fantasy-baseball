from unittest import TestCase

from draft.draft_state_evaluator import rank_values, slots_to_fill
from draft.test_draft_state import TestDraftState
from espn.baseball.baseball_slot import BaseballSlot


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
        self.assertEqual(
            rank_values([1.0, 1.0, 1.0, 1.0, 2.0], False), [2.5, 2.5, 2.5, 2.5, 5.0]
        )

    def test__slots_to_fill(self):
        lineups = [TestDraftState.l1, TestDraftState.l2, TestDraftState.l3]
        d = {
            BaseballSlot.OUTFIELD: 2,
            BaseballSlot.SHORT: 2,
            BaseballSlot.PITCHER: 2,
            BaseballSlot.UTIL: 2,
            BaseballSlot.BENCH: 3,
        }
        self.assertEqual(d, slots_to_fill(lineups, TestDraftState.ls))
