import unittest
from lineup import Lineup, LineupSlot
from lineup_settings import LineupSettings
from test.test_player import PlayerTest


class Test(unittest.TestCase):
    base_lineup_dict = {
        LineupSlot.CATCHER: [PlayerTest.sanchez],
        LineupSlot.FIRST: [PlayerTest.muncy],
        LineupSlot.SECOND: [PlayerTest.merrifield],
        LineupSlot.THIRD: [PlayerTest.carpenter],
        LineupSlot.SHORT: [PlayerTest.segura],
        LineupSlot.OUTFIELD: [PlayerTest.springer,
                              PlayerTest.rosario,
                              PlayerTest.braun,
                              PlayerTest.santana,
                              PlayerTest.choo],
        LineupSlot.MIDDLE_INFIELD: [PlayerTest.cano],
        LineupSlot.CORNER_INFIELD: [PlayerTest.rizzo],
        LineupSlot.UTIL: [PlayerTest.cabrera],
        LineupSlot.PITCHER: [PlayerTest.degrom,
                             PlayerTest.kimbrel,
                             PlayerTest.morton,
                             PlayerTest.hill,
                             PlayerTest.arrieta,
                             PlayerTest.glasnow,
                             PlayerTest.barnes,
                             PlayerTest.stripling,
                             PlayerTest.smith],
        LineupSlot.BENCH: [PlayerTest.paddack,
                           PlayerTest.yelich,
                           PlayerTest.peraza],
        LineupSlot.INJURED: [PlayerTest.olson,
                             PlayerTest.jimenez],
    }

    simple_lineup = Lineup(base_lineup_dict)

    def test_possible_starters_one_slot(self):
        lineup_settings = LineupSettings({
            LineupSlot.CATCHER: 0,
            LineupSlot.FIRST: 1,
            LineupSlot.SECOND: 0,
            LineupSlot.THIRD: 0,
            LineupSlot.SHORT: 0,
            LineupSlot.MIDDLE_INFIELD: 0,
            LineupSlot.CORNER_INFIELD: 0,
            LineupSlot.OUTFIELD: 0,
            LineupSlot.UTIL: 0,
            LineupSlot.BENCH: 0,
            LineupSlot.PITCHER: 0,
            LineupSlot.INJURED: 0
        })

        starters = self.simple_lineup.possible_starting_hitters(lineup_settings)
        self.assertEqual(len(starters), 4)
        self.assertTrue(frozenset({PlayerTest.rizzo}) in starters)
        self.assertTrue(frozenset({PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter}) in starters)
        self.assertTrue(frozenset({PlayerTest.cabrera}) in starters)

    def test_possible_starters_two_slots_no_dups(self):
        lineup_settings = LineupSettings({
            LineupSlot.CATCHER: 0,
            LineupSlot.FIRST: 1,
            LineupSlot.SECOND: 0,
            LineupSlot.THIRD: 0,
            LineupSlot.SHORT: 0,
            LineupSlot.MIDDLE_INFIELD: 0,
            LineupSlot.CORNER_INFIELD: 1,
            LineupSlot.OUTFIELD: 0,
            LineupSlot.UTIL: 0,
            LineupSlot.BENCH: 0,
            LineupSlot.PITCHER: 0,
            LineupSlot.INJURED: 0
        })

        starters = self.simple_lineup.possible_starting_hitters(lineup_settings)
        self.assertEqual(len(starters), 6)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.carpenter}) in starters)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.cabrera}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter, PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter, PlayerTest.cabrera}) in starters)
        self.assertTrue(frozenset({PlayerTest.muncy, PlayerTest.cabrera}) in starters)

