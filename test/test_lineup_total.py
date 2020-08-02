import operator
import unittest

from optimize.lineup_total import LineupTotal
from scoring_setting import ScoringSetting
from stats import Stats
from espn.baseball.baseball_stat import BaseballStat
from test.test_lineup import LineupTest
from test.test_stats import StatsTest


class LineupTotalTest(unittest.TestCase):

    lt1 = LineupTotal(LineupTest.simple_lineup, StatsTest.s1)

    def test_compare_true(self):
        less_hits = Stats({BaseballStat.H: 9.0}, BaseballStat)

        less_hits_lt = LineupTotal(LineupTest.simple_lineup, less_hits)

        self.assertTrue(self.lt1.compare(less_hits_lt, BaseballStat.H, operator.gt))
        self.assertFalse(less_hits_lt.compare(self.lt1, BaseballStat.H, operator.gt))

    def test_bte_equal(self):
        same_hits = Stats({BaseballStat.H: 10.0}, BaseballStat)

        same_hits_lt = LineupTotal(LineupTest.simple_lineup, same_hits)
        self.assertFalse(self.lt1.compare(same_hits_lt, BaseballStat.H, operator.gt))
        self.assertTrue(self.lt1.compare(same_hits_lt, BaseballStat.H, operator.ge))
        self.assertTrue(self.lt1.compare(same_hits_lt, BaseballStat.H, operator.le))

    def test_bte_false(self):
        more_hits = Stats({BaseballStat.H: 10.01}, BaseballStat)

        more_hits_lt = LineupTotal(LineupTest.simple_lineup, more_hits)
        self.assertFalse(self.lt1.compare(more_hits_lt, BaseballStat.H, operator.gt))
        self.assertTrue(self.lt1.compare(more_hits_lt, BaseballStat.H, operator.lt))
