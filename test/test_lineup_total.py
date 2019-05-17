import operator
import unittest

from optimize.lineup_total import LineupTotal
from scoring_setting import ScoringSetting
from stats import Stat, Stats
from test.test_lineup import LineupTest
from test.test_stats import StatsTest


class LineupTotalTest(unittest.TestCase):

    lt1 = LineupTotal(LineupTest.simple_lineup, StatsTest.s1)

    def test_compare_true(self):
        less_hits = Stats({
            Stat.H: 9.0
        })

        less_hits_lt = LineupTotal(LineupTest.simple_lineup, less_hits)

        self.assertTrue(self.lt1.compare(less_hits_lt, Stat.H, operator.gt))
        self.assertFalse(less_hits_lt.compare(self.lt1, Stat.H, operator.gt))

    def test_bte_equal(self):
        same_hits = Stats({
            Stat.H: 10.0
        })

        same_hits_lt = LineupTotal(LineupTest.simple_lineup, same_hits)
        self.assertFalse(self.lt1.compare(same_hits_lt, Stat.H, operator.gt))
        self.assertTrue(self.lt1.compare(same_hits_lt, Stat.H, operator.ge))
        self.assertTrue(self.lt1.compare(same_hits_lt, Stat.H, operator.le))

    def test_bte_false(self):
        more_hits = Stats({
            Stat.H: 10.01
        })

        more_hits_lt = LineupTotal(LineupTest.simple_lineup, more_hits)
        self.assertFalse(self.lt1.compare(more_hits_lt, Stat.H, operator.gt))
        self.assertTrue(self.lt1.compare(more_hits_lt, Stat.H, operator.lt))
