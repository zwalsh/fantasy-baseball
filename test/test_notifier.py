import unittest

from lineup_slot import LineupSlot
from lineup_transition import LineupTransition
from notifications.client.pushed import PushedClient
from notifications.notifier import Notifier
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

    def test_transition_message(self):
        self.assertEqual(Notifier.transition_message(self.t1), "Muncy: 1B/3B->BE")
        self.assertEqual(Notifier.transition_message(self.t2), "Merrifield: OF->2B")

    def test_notify_set_lineup(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Team1"
        pas = 45.0234
        ts = [self.t1, self.t2]

        n.notify_set_lineup(team, pas, ts)

        msg = team + ": proj. " + str(round(pas, 2)) + " PA"
        for t in ts:
            msg += "\n" + Notifier.transition_message(t)

        (msg_rec, url_rec) = mock_client.messages[0]

        self.assertEqual(msg, msg_rec)
        self.assertEqual(None, url_rec)

    def test_notify_set_lineup_truncate(self):
        mock_client = MockClient()
        n = Notifier(mock_client)

        team = "Loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong team name"
        pas = 1234567890.11
        ts = [self.t1, self.t1]

        n.notify_set_lineup(team, pas, ts)

        expected = team + ": proj. " + str(round(pas, 2)) + " PA"
        expected += "\n" + Notifier.transition_message(self.t1)
        expected += "\n" + "Muncy: 1..."

        self.assertEqual(expected, mock_client.messages[0][0])
