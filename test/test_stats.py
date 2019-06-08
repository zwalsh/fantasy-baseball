import unittest

from stats import Stat, Stats


class StatsTest(unittest.TestCase):
    s1 = Stats({
        Stat.H: 10.0,
        Stat.AB: 40.0,
        Stat.BB: 5.0,
        Stat.PA: 50.0
    })

    s2 = Stats({
        Stat.H: 1.0,
        Stat.AB: 3.0,
        Stat.PA: 4.0,
        Stat.BB: 1.0
    })

    def test_value_for_stat_counting_stat(self):
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.H), 10.0)
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.PA), 50.0)

    def test_value_for_stat_function(self):
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.AVG), .250)
        self.assertEqual(StatsTest.s1.value_for_stat(Stat.OBP), .300)

    def test_addition(self):
        added = self.s1 + self.s2

        self.assertEqual(added.value_for_stat(Stat.H), 11.0)
        self.assertEqual(added.value_for_stat(Stat.AB), 43.0)
        self.assertEqual(added.value_for_stat(Stat.PA), 54.0)
        self.assertEqual(added.value_for_stat(Stat.AVG), round(11.0 / 43.0, 3))
