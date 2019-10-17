import unittest

from espn.baseball.lineup_slot import LineupSlot
from lineup_transition import LineupTransition
from notifications.notifier import Notifier
from scoring_setting import ScoringSetting
from stats import Stat
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
    t1 = LineupTransition(PlayerTest.muncy, LineupSlot.CORNER_INFIELD, LineupSlot.BENCH)
    t2 = LineupTransition(PlayerTest.merrifield, LineupSlot.OUTFIELD, LineupSlot.SECOND)

    lt1 = LineupTotalTest.lt1

    def test_transition_message(self):
        self.assertEqual(Notifier.transition_message(self.t1), "Muncy: 1B/3B->BE")
        self.assertEqual(Notifier.transition_message(self.t2), "Merrifield: OF->2B")

    def test_notify_set_lineup(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Team1"
        ts = [self.t1, self.t2]

        n.notify_set_lineup(team, self.lt1, ts, [ScoringSetting(Stat.H, False)])

        msg = team + ": 50.00PA\n10.00H "
        for t in ts:
            msg += "\n" + Notifier.transition_message(t)

        (msg_rec, url_rec) = mock_client.messages[0]

        self.assertEqual(msg, msg_rec)
        self.assertEqual(None, url_rec)

    def test_notify_set_lineup_truncate(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong team name"
        ts = [self.t1, self.t1]

        n.notify_set_lineup(team, self.lt1, ts, [ScoringSetting(Stat.H, False)])

        expected = team + ": 50.00PA\n10.00H "
        expected += "\n" + Notifier.transition_message(self.t1)
        expected += "\n" + "Muncy: ..."

        self.assertEqual(expected, mock_client.messages[0][0])

    def test_notify_ignore_non_hitting_stat(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Name"
        ts = [self.t1, self.t2]

        n.notify_set_lineup(team, self.lt1, ts, [ScoringSetting(Stat.WHIP, True)])

        expected = team + ": 50.00PA\n"
        for t in ts:
            expected += "\n" + Notifier.transition_message(t)

        (msg_rec, url_rec) = mock_client.messages[0]

        self.assertEqual(expected, msg_rec)
        self.assertEqual(None, url_rec)
