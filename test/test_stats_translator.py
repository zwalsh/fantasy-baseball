import unittest
import espn.stats_translator


class Test(unittest.TestCase):

    def test_create_stats(self):
        stats_ex = {
            41: "1.1105",
            5: "2"
        }
        stats = espn.stats_translator.create_stats(stats_ex)
        self.assertEqual(stats.home_runs(), 2.0)
        self.assertEqual(stats.whip(), 1.111)
