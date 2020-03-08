from copy import copy, deepcopy
from itertools import islice
from typing import List, Optional

from draft.draft_game_info import DraftGameInfo
from espn.baseball.baseball_slot import BaseballSlot
from lineup import Lineup
from minimax.game_state import GameState
from player import Player


class DraftState(GameState):
    def __init__(self, game_info: DraftGameInfo, ranked_players: list, drafted: set, lineups: list, current_player: int,
                 is_next_larger):
        super().__init__()
        self.game_info = game_info
        self.ranked_players = ranked_players
        self.lineups = lineups
        self.drafted = drafted
        self.current_drafter = current_player
        self.is_next_larger = is_next_larger

    def advance_state(self, baseball_player: Player):
        """
        Advance to the next DraftState by picking the given Player
        :param baseball_player: the baseball player chosen by the current drafter
        :return DraftState: the advanced state
        """
        relevant_lineup = self.lineups[self.current_drafter]
        slot = DraftState.slot_to_fill(self.open_slots(relevant_lineup), baseball_player)
        successor_lineups = copy(self.lineups)
        next_lineup = deepcopy(relevant_lineup)
        current_in_slot = next_lineup.player_dict.get(slot, [])
        current_in_slot.append(baseball_player)
        next_lineup.player_dict[slot] = current_in_slot
        successor_lineups[self.current_drafter] = next_lineup
        # add player to copy of drafted
        successor_drafted = copy(self.drafted)
        successor_drafted.add(baseball_player)
        return DraftState(self.game_info, self.ranked_players, successor_drafted, successor_lineups,
                                self._next_player(), self._next_direction())

    def children(self) -> List['GameState']:
        # for player who's playing, get lineup, run over top x players at each position
        # add to drafted set
        relevant_lineup = self.lineups[self.current_drafter]
        new_states = []
        for baseball_player, slot_to_fill in self._possible_additions(self.current_drafter):
            new_states.append(self.advance_state(baseball_player))
        return new_states

    def _next_player(self):
        if self.current_drafter == 0:
            return 1 if self.is_next_larger else 0
        if self.current_drafter == self.game_info.total_players - 1:
            return self.current_drafter if self.is_next_larger else self.current_drafter - 1
        return self.current_drafter + 1 if self.is_next_larger else self.current_drafter - 1

    def _next_direction(self):
        if self.current_drafter not in {0, self.game_info.total_players - 1}:
            return self.is_next_larger
        return self.current_drafter == 0

    def _possible_additions(self, player_index) -> list:
        relevant_lineup = self.lineups[player_index]
        open_slots = self.open_slots(relevant_lineup)
        possible_additions = []

        for player in first_n_not_drafted(self.ranked_players, self.drafted, 7):
            slot = DraftState.slot_to_fill(open_slots, player)
            if slot is None:
                continue
            possible_additions.append((player, slot))

        return possible_additions

    def open_slots(self, relevant_lineup: Lineup) -> List[BaseballSlot]:
        """
        Calculate which slots still require a Player to fill them in the given lineup
        :param relevant_lineup: the lineup for which to find the open slots
        :return list:
        """
        open_slots = []
        for ls, count in self.game_info.lineup_settings.slot_counts.items():
            if len(relevant_lineup.player_dict.get(ls, [])) < count:
                open_slots.append(ls)
        return open_slots

    @staticmethod
    def slot_to_fill(open_slots: List[BaseballSlot], player: Player) -> Optional[BaseballSlot]:
        fillable_slots = filter(lambda slot: player.can_play(slot), open_slots)
        sorted_bench_last = sorted(fillable_slots, key=slot_value, reverse=True)
        return next(iter(sorted_bench_last), None)

    def is_terminal(self) -> bool:
        draftable_slots = filter(lambda tup: tup[0] != BaseballSlot.INJURED,
                                 self.game_info.lineup_settings.slot_counts.items())
        total_slots = sum(map(lambda tup: tup[1], draftable_slots)) * self.game_info.total_players
        return len(self.drafted) == total_slots


def first_n_not_drafted(players, drafted, n):
    return islice(filter(lambda p: p not in drafted, players), n)

def slot_value(slot):
    return {
        BaseballSlot.BENCH: 0,
        BaseballSlot.UTIL: 1,
    }.get(slot, 2)
