import unittest

from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from espn.basketball.basketball_slot import BasketballSlot
from lineup_transition import LineupTransition
from notifications.notifier import Notifier
from scoring_setting import ScoringSetting
from test.test_lineup_total import LineupTotalTest
from test.test_player import PlayerTest


class MockClient:
    def __init__(self):
        """
        Fake client to be used by a Notifier in tests
        """
        self.messages = []

    def send_message(self, content, content_url=None):
        self.messages.append((content, content_url))


class Test(unittest.TestCase):
    t1 = LineupTransition(
        PlayerTest.muncy, BaseballSlot.CORNER_INFIELD, BaseballSlot.BENCH
    )
    t2 = LineupTransition(
        PlayerTest.merrifield, BaseballSlot.OUTFIELD, BaseballSlot.SECOND
    )

    lt1 = LineupTotalTest.lt1

    def test_transition_message(self):
        self.assertEqual(Notifier.transition_message(self.t1), "Muncy: 1B/3B->BE")
        self.assertEqual(Notifier.transition_message(self.t2), "Merrifield: OF->2B")

    def test_notify_set_lineup(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Team1"
        ts = [self.t1, self.t2]

        n.notify_set_lineup(team, self.lt1, ts, [ScoringSetting(BaseballStat.H, False, 0.0)])

        msg = team + ": 50.00PA\n10.00H "
        for t in ts:
            msg += "\n" + Notifier.transition_message(t)

        (msg_rec, url_rec) = mock_client.messages[0]

        self.assertEqual(msg, msg_rec)
        self.assertEqual(None, url_rec)

    def test_notify_ignore_non_hitting_stat(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Name"
        ts = [self.t1, self.t2]

        n.notify_set_lineup(
            team, self.lt1, ts, [ScoringSetting(BaseballStat.WHIP, True, 0.0)]
        )

        expected = team + ": 50.00PA\n"
        for t in ts:
            expected += "\n" + Notifier.transition_message(t)

        (msg_rec, url_rec) = mock_client.messages[0]

        self.assertEqual(expected, msg_rec)
        self.assertEqual(None, url_rec)

    def test_notify_when_no_projection(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        n.notify_set_fba_lineup(
            team_name="name",
            transitions=[
                LineupTransition(PlayerTest.lebron, BasketballSlot.POINT_GUARD, BaseballSlot.BENCH)
            ],
            total_points=123.0,
            player_to_fp={} # no projection for lebron
        )

        self.assertEqual(mock_client.messages[0][0],"name: 123.0 points\nJames: PG->BE (0.0)")
