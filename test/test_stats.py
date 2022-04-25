import unittest

from stats import Stats
from espn.baseball.baseball_stat import BaseballStat


class StatsTest(unittest.TestCase):
    s1 = Stats(
        {
            BaseballStat.H: 10.0,
            BaseballStat.AB: 40.0,
            BaseballStat.BB: 5.0,
            BaseballStat.PA: 50.0,
        },
        BaseballStat,
    )

    s2 = Stats(
        {
            BaseballStat.H: 1.0,
            BaseballStat.AB: 3.0,
            BaseballStat.PA: 4.0,
            BaseballStat.BB: 1.0,
        },
        BaseballStat,
    )

    def test_value_for_stat_counting_stat(self):
        self.assertEqual(StatsTest.s1.value_for_stat(BaseballStat.H), 10.0)
        self.assertEqual(StatsTest.s1.value_for_stat(BaseballStat.PA), 50.0)

    def test_value_for_stat_function(self):
        self.assertEqual(StatsTest.s1.value_for_stat(BaseballStat.AVG), 0.250)
        self.assertEqual(StatsTest.s1.value_for_stat(BaseballStat.OBP), 0.300)

    def test_addition(self):
        added = self.s1 + self.s2

        self.assertEqual(added.value_for_stat(BaseballStat.H), 11.0)
        self.assertEqual(added.value_for_stat(BaseballStat.AB), 43.0)
        self.assertEqual(added.value_for_stat(BaseballStat.PA), 54.0)
        self.assertEqual(added.value_for_stat(BaseballStat.AVG), round(11.0 / 43.0, 3))
