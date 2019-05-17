import unittest
from lineup import Lineup, LineupSlot
from lineup_settings import LineupSettings
from lineup_transition import LineupTransition
from test.test_player import PlayerTest


class LineupTest(unittest.TestCase):
    empty_lineup_dict = {
        LineupSlot.CATCHER: [],
        LineupSlot.FIRST: [],
        LineupSlot.SECOND: [],
        LineupSlot.THIRD: [],
        LineupSlot.SHORT: [],
        LineupSlot.OUTFIELD: [],
        LineupSlot.MIDDLE_INFIELD: [],
        LineupSlot.CORNER_INFIELD: [],
        LineupSlot.UTIL: [],
        LineupSlot.PITCHER: [],
        LineupSlot.BENCH: [],
        LineupSlot.INJURED: [],
    }
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

        lineups = self.simple_lineup.possible_starting_hitters(lineup_settings)
        starters = set(map(Lineup.starters, lineups))
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

        lineups = self.simple_lineup.possible_starting_hitters(lineup_settings)
        starters = set(map(Lineup.starters, lineups))
        self.assertEqual(len(starters), 6)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.carpenter}) in starters)
        self.assertTrue(frozenset({PlayerTest.rizzo, PlayerTest.cabrera}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter, PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter, PlayerTest.cabrera}) in starters)
        self.assertTrue(frozenset({PlayerTest.muncy, PlayerTest.cabrera}) in starters)

    def test_transitions_single_swap(self):
        carpenter_first_dict = self.empty_lineup_dict.copy()
        carpenter_first_dict[LineupSlot.FIRST] = [PlayerTest.carpenter]
        cf_lineup = Lineup(carpenter_first_dict)

        carpenter_corner_inf_dict = self.empty_lineup_dict.copy()
        carpenter_corner_inf_dict[LineupSlot.CORNER_INFIELD] = [PlayerTest.carpenter]
        cci_lineup = Lineup(carpenter_corner_inf_dict)

        transitions = cf_lineup.transitions(cci_lineup)

        self.assertEqual(len(transitions), 1)
        self.assertTrue(LineupTransition(PlayerTest.carpenter, LineupSlot.FIRST, LineupSlot.CORNER_INFIELD) in transitions)

    def test_transitions_swap_two_players(self):
        l1_dict = self.empty_lineup_dict.copy()
        l1_dict[LineupSlot.BENCH] = [PlayerTest.merrifield]
        l1_dict[LineupSlot.OUTFIELD] = [PlayerTest.yelich]
        l1 = Lineup(l1_dict)

        l2_dict = self.empty_lineup_dict.copy()
        l2_dict[LineupSlot.OUTFIELD] = [PlayerTest.merrifield]
        l2_dict[LineupSlot.BENCH] = [PlayerTest.yelich]
        l2 = Lineup(l2_dict)

        transitions = l1.transitions(l2)

        self.assertEqual(len(transitions), 2)
        self.assertTrue(LineupTransition(PlayerTest.merrifield, LineupSlot.BENCH, LineupSlot.OUTFIELD) in transitions)
        self.assertTrue(LineupTransition(PlayerTest.yelich, LineupSlot.OUTFIELD, LineupSlot.BENCH) in transitions)
