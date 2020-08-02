import unittest

from espn.baseball.baseball_position import BaseballPosition
from optimize import lineup_optimizer
from test.test_lineup import LineupTest
from test.test_player import PlayerTest


class MockEspn:
    def __init__(self, prob_pitcher_ids):
        self.prob_pitcher_ids = prob_pitcher_ids

    def is_probable_pitcher(self, espn_id):
        return espn_id in self.prob_pitcher_ids


class TestLineupOptimizer(unittest.TestCase):
    def test_must_start_pitchers(self):
        l = LineupTest.simple_lineup
        paddack = PlayerTest.paddack
        mock_espn = MockEspn([paddack.espn_id])

        must_starts = lineup_optimizer.must_start_pitchers(l, mock_espn)
        # includes all probable starters
        self.assertTrue(paddack in must_starts)

        relievers = [
            p for p in l.players() if p.default_position is BaseballPosition.RELIEVER
        ]

        # includes all relievers
        self.assertTrue(all(map(lambda r: r in must_starts, relievers)))

        # includes only probable starters and relievers
        self.assertEqual(len(must_starts), len(relievers) + 1)

    def test_benchable_pitchers(self):
        l = LineupTest.simple_lineup
        must_start = {PlayerTest.paddack}

        benchables = lineup_optimizer.benchable_pitchers(l, must_start)

        self.assertNotIn(PlayerTest.paddack, benchables)
        self.assertEqual(
            benchables,
            {
                PlayerTest.degrom,
                PlayerTest.morton,
                PlayerTest.hill,
                PlayerTest.arrieta,
                PlayerTest.glasnow,
                PlayerTest.smith,
            },
        )
