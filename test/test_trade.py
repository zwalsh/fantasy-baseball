import unittest

from espn.trade import Trade
from test.test_player import PlayerTest

class Test(unittest.TestCase):

    trade1 = Trade(1, 2, [PlayerTest.merrifield], [PlayerTest.carpenter, PlayerTest.olson])


    def test_last_names(self):
        lasts_send = Trade.last_names(self.trade1.send_players)
        lasts_rec = Trade.last_names(self.trade1.receive_players)

        self.assertEqual(lasts_send, "Merrifield")
        self.assertEqual(lasts_rec, "Carpenter Olson")
