import unittest
from espn.baseball.baseball_api import BaseballApi


class Test(unittest.TestCase):

    def test_create_stats(self):
        stats_ex = {
            41: "1.1105",
            5: "2"
        }
        stats = BaseballApi.create_stats(stats_ex)
        self.assertEqual(stats.home_runs(), 2.0)
        self.assertEqual(stats.whip(), 1.111)
