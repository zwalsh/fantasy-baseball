import unittest

from stats import Stat, Stats


class StatsTest(unittest.TestCase):
    s1 = Stats({
        Stat.H: 10.0,
        Stat.AB: 40.0,
        Stat.BB: 5.0,
        Stat.PA: 50.0
    })

    def test_value_for_stat_counting_stat(self):
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.H), 10.0)
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.PA), 50.0)

    def test_value_for_stat_function(self):
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.AVG), .250)
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.OBP), .300)
