import unittest
from lineup import Lineup, BaseballSlot
from lineup_settings import LineupSettings
from lineup_transition import LineupTransition
from test.test_player import PlayerTest


class LineupTest(unittest.TestCase):
    empty_lineup_dict = {
        BaseballSlot.CATCHER: [],
        BaseballSlot.FIRST: [],
        BaseballSlot.SECOND: [],
        BaseballSlot.THIRD: [],
        BaseballSlot.SHORT: [],
        BaseballSlot.OUTFIELD: [],
        BaseballSlot.MIDDLE_INFIELD: [],
        BaseballSlot.CORNER_INFIELD: [],
        BaseballSlot.UTIL: [],
        BaseballSlot.PITCHER: [],
        BaseballSlot.BENCH: [],
        BaseballSlot.INJURED: [],
    }
    base_lineup_dict = {
        BaseballSlot.CATCHER: [PlayerTest.sanchez],
        BaseballSlot.FIRST: [PlayerTest.muncy],
        BaseballSlot.SECOND: [PlayerTest.merrifield],
        BaseballSlot.THIRD: [PlayerTest.carpenter],
        BaseballSlot.SHORT: [PlayerTest.segura],
        BaseballSlot.OUTFIELD: [PlayerTest.springer,
                                PlayerTest.rosario,
                                PlayerTest.braun,
                                PlayerTest.santana,
                                PlayerTest.choo],
        BaseballSlot.MIDDLE_INFIELD: [PlayerTest.cano],
        BaseballSlot.CORNER_INFIELD: [PlayerTest.rizzo],
        BaseballSlot.UTIL: [PlayerTest.cabrera],
        BaseballSlot.PITCHER: [PlayerTest.degrom,
                               PlayerTest.kimbrel,
                               PlayerTest.morton,
                               PlayerTest.hill,
                               PlayerTest.arrieta,
                               PlayerTest.glasnow,
                               PlayerTest.barnes,
                               PlayerTest.stripling,
                               PlayerTest.smith],
        BaseballSlot.BENCH: [PlayerTest.paddack,
                             PlayerTest.yelich,
                             PlayerTest.peraza],
        BaseballSlot.INJURED: [PlayerTest.olson,
                               PlayerTest.jimenez],
    }

    simple_lineup = Lineup(base_lineup_dict, BaseballSlot)

    def test_possible_starters_one_slot(self):
        lineup_settings = LineupSettings({
            BaseballSlot.CATCHER: 0,
            BaseballSlot.FIRST: 1,
            BaseballSlot.SECOND: 0,
            BaseballSlot.THIRD: 0,
            BaseballSlot.SHORT: 0,
            BaseballSlot.MIDDLE_INFIELD: 0,
            BaseballSlot.CORNER_INFIELD: 0,
            BaseballSlot.OUTFIELD: 0,
            BaseballSlot.UTIL: 0,
            BaseballSlot.BENCH: 0,
            BaseballSlot.PITCHER: 0,
            BaseballSlot.INJURED: 0
        })

        lineups = self.simple_lineup.possible_lineups(lineup_settings, BaseballSlot.hitting_slots())
        starters = set(map(Lineup.starters, lineups))
        self.assertEqual(len(starters), 4)
        self.assertTrue(frozenset({PlayerTest.rizzo}) in starters)
        self.assertTrue(frozenset({PlayerTest.muncy}) in starters)
        self.assertTrue(frozenset({PlayerTest.carpenter}) in starters)
        self.assertTrue(frozenset({PlayerTest.cabrera}) in starters)

    def test_possible_starters_two_slots_no_dups(self):
        lineup_settings = LineupSettings({
            BaseballSlot.CATCHER: 0,
            BaseballSlot.FIRST: 1,
            BaseballSlot.SECOND: 0,
            BaseballSlot.THIRD: 0,
            BaseballSlot.SHORT: 0,
            BaseballSlot.MIDDLE_INFIELD: 0,
            BaseballSlot.CORNER_INFIELD: 1,
            BaseballSlot.OUTFIELD: 0,
            BaseballSlot.UTIL: 0,
            BaseballSlot.BENCH: 0,
            BaseballSlot.PITCHER: 0,
            BaseballSlot.INJURED: 0
        })

        lineups = self.simple_lineup.possible_lineups(lineup_settings, BaseballSlot.hitting_slots())
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
        carpenter_first_dict[BaseballSlot.FIRST] = [PlayerTest.carpenter]
        cf_lineup = Lineup(carpenter_first_dict, BaseballSlot)

        carpenter_corner_inf_dict = self.empty_lineup_dict.copy()
        carpenter_corner_inf_dict[BaseballSlot.CORNER_INFIELD] = [PlayerTest.carpenter]
        cci_lineup = Lineup(carpenter_corner_inf_dict, BaseballSlot)

        transitions = cf_lineup.transitions(cci_lineup)

        self.assertEqual(len(transitions), 1)
        self.assertTrue(LineupTransition(PlayerTest.carpenter, BaseballSlot.FIRST, BaseballSlot.CORNER_INFIELD) in transitions)

    def test_transitions_swap_two_players(self):
        l1_dict = self.empty_lineup_dict.copy()
        l1_dict[BaseballSlot.BENCH] = [PlayerTest.merrifield]
        l1_dict[BaseballSlot.OUTFIELD] = [PlayerTest.yelich]
        l1 = Lineup(l1_dict, BaseballSlot)

        l2_dict = self.empty_lineup_dict.copy()
        l2_dict[BaseballSlot.OUTFIELD] = [PlayerTest.merrifield]
        l2_dict[BaseballSlot.BENCH] = [PlayerTest.yelich]
        l2 = Lineup(l2_dict, BaseballSlot)

        transitions = l1.transitions(l2)

        self.assertEqual(len(transitions), 2)
        self.assertTrue(LineupTransition(PlayerTest.merrifield, BaseballSlot.BENCH, BaseballSlot.OUTFIELD) in transitions)
        self.assertTrue(LineupTransition(PlayerTest.yelich, BaseballSlot.OUTFIELD, BaseballSlot.BENCH) in transitions)
