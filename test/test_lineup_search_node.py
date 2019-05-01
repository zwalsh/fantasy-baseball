import unittest
from lineup import LineupSearchNode, Lineup
from lineup_settings import LineupSettings
from lineup_slot import LineupSlot
from player import Player


class Test(unittest.TestCase):
    rizzo = Player("Anthony Rizzo", 123, {LineupSlot.FIRST})
    goldschmidt = Player("Paul Goldschmidt", 456, {LineupSlot.FIRST})

    empty_lineup = Lineup(dict())
    basic_node = LineupSearchNode(empty_lineup, [rizzo], {LineupSlot.FIRST})
    simple_settings = LineupSettings({LineupSlot.FIRST: 1})

    two_firsts_left_node = LineupSearchNode(empty_lineup, [rizzo, goldschmidt], {LineupSlot.FIRST})

    def test_successors_one_player(self):
        result = self.basic_node.successors(self.simple_settings)
        self.assertEqual(len(result), 1)
        successor = result[0]
        self.assertEqual(len(successor.players_left), 0)
        self.assertEqual(successor.lineup.starters(), {self.rizzo})

    def test_successors_two_players(self):
        result = self.two_firsts_left_node.successors(self.simple_settings)
        self.assertEqual(len(result), 2)
        s0 = result[0]
        s0rem = s0.players_left[0]
        s0first = s0.lineup.player_dict.get(LineupSlot.FIRST)[0]
        s1 = result[1]
        s1rem = s1.players_left[0]
        s1first = s1.lineup.player_dict.get(LineupSlot.FIRST)[0]

        self.assertEqual({s0rem, s1rem}, {self.rizzo, self.goldschmidt})
        self.assertNotEqual(s0rem, s0first)
        self.assertNotEqual(s1rem, s1first)
        self.assertEqual(s0rem, s1first)

