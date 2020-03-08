from unittest import TestCase

from draft.draft_game_info import DraftGameInfo
from draft.draft_state import DraftState
from espn.baseball.baseball_slot import BaseballSlot
from lineup import Lineup
from lineup_settings import LineupSettings
from test.test_player import PlayerTest


class TestDraftState(TestCase):
    ls = LineupSettings({
        BaseballSlot.OUTFIELD: 2,
        BaseballSlot.SHORT: 1,
        BaseballSlot.PITCHER: 1,
        BaseballSlot.UTIL: 1,
        BaseballSlot.BENCH: 1
    })
    l1 = Lineup(
        {
            BaseballSlot.OUTFIELD: [PlayerTest.yelich, PlayerTest.braun],
            BaseballSlot.UTIL: [PlayerTest.santana]
        },
        BaseballSlot)
    l2 = Lineup(
        {
            BaseballSlot.PITCHER: [PlayerTest.degrom],
            BaseballSlot.SHORT: [PlayerTest.segura]
        },
        BaseballSlot
    )
    l3 = Lineup(
        {
            BaseballSlot.OUTFIELD: [PlayerTest.springer, PlayerTest.rosario]
        },
        BaseballSlot
    )
    info = DraftGameInfo(3, 100, ls)
    state = DraftState(info, {
        PlayerTest.springer,
        PlayerTest.rosario,
        PlayerTest.degrom,
        PlayerTest.segura,
        PlayerTest.rizzo,
        PlayerTest.peraza,
        PlayerTest.choo,
        PlayerTest.morton,
        PlayerTest.yelich,
        PlayerTest.braun,
        PlayerTest.santana,
    }, {
                           PlayerTest.springer,
                           PlayerTest.rosario,
                           PlayerTest.degrom,
                           PlayerTest.segura,
                           PlayerTest.yelich,
                           PlayerTest.braun,
                           PlayerTest.santana
                       }, [l1, l2, l3], 0, True)

    small_lineup_settings = LineupSettings({BaseballSlot.OUTFIELD: 1, BaseballSlot.INJURED: 1})
    sl0 = Lineup({BaseballSlot.OUTFIELD: [PlayerTest.springer]}, BaseballSlot)
    sl1 = Lineup({BaseballSlot.OUTFIELD: [PlayerTest.rosario]}, BaseballSlot)
    sl2 = Lineup({BaseballSlot.OUTFIELD: [PlayerTest.yelich]}, BaseballSlot)
    terminal_state = DraftState(DraftGameInfo(3, 1000, small_lineup_settings), {
        PlayerTest.springer,
        PlayerTest.rosario,
        PlayerTest.yelich
    }, {
                                    PlayerTest.springer, PlayerTest.rosario, PlayerTest.yelich
                                }, [sl0, sl1, sl2], 0, True)

    def test__possible_additions(self):
        poss_p0 = self.state._possible_additions(0)
        self.assertEqual(4, len(poss_p0))
        self.assertTrue((PlayerTest.rizzo, BaseballSlot.BENCH) in poss_p0)
        self.assertTrue((PlayerTest.peraza, BaseballSlot.SHORT) in poss_p0)
        self.assertTrue((PlayerTest.choo, BaseballSlot.BENCH) in poss_p0)
        self.assertTrue((PlayerTest.morton, BaseballSlot.PITCHER) in poss_p0)

        poss_p1 = self.state._possible_additions(1)
        self.assertEqual(4, len(poss_p1))
        self.assertTrue((PlayerTest.rizzo, BaseballSlot.UTIL) in poss_p1)
        self.assertTrue((PlayerTest.peraza, BaseballSlot.UTIL) in poss_p1)
        self.assertTrue((PlayerTest.choo, BaseballSlot.OUTFIELD) in poss_p1)
        self.assertTrue((PlayerTest.morton, BaseballSlot.BENCH) in poss_p1)

        poss_p2 = self.state._possible_additions(2)
        self.assertEqual(4, len(poss_p2))
        self.assertTrue((PlayerTest.rizzo, BaseballSlot.UTIL) in poss_p2)
        self.assertTrue((PlayerTest.peraza, BaseballSlot.SHORT) in poss_p2)
        self.assertTrue((PlayerTest.choo, BaseballSlot.UTIL) in poss_p2)
        self.assertTrue((PlayerTest.morton, BaseballSlot.PITCHER) in poss_p2)

    def test_children(self):
        children_p0 = self.state.children()
        self.assertEqual(4, len(children_p0))
        for child in children_p0:
            # different lineup lists
            self.assertTrue(self.state.lineups != child.lineups)
            # different lineups for player 0
            self.assertNotEqual(self.state.lineups[0], child.lineups[0])
            # same lineups for all other players
            self.assertEqual(self.state.lineups[1], child.lineups[1])
            self.assertEqual(self.state.lineups[2], child.lineups[2])

    def test_is_terminal(self):
        self.assertFalse(self.state.is_terminal())
        self.assertTrue(self.terminal_state.is_terminal())

    def test__next_player(self):
        self.assertEqual(1, self.state._next_player())

    def test__next_player_end_returning(self):
        ds = DraftState(self.info, [], {}, [], 2, False)
        self.assertEqual(1, ds._next_player())

    def test__next_direction(self):
        self.assertTrue(self.state._next_direction())

    def test__next_direction_returning(self):
        ds = DraftState(self.info, [], {}, [], 2, False)
        self.assertFalse(ds._next_direction())
