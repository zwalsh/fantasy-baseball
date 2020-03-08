from copy import copy, deepcopy
from itertools import islice
from typing import List

from draft.draft_game_info import DraftGameInfo
from espn.baseball.baseball_slot import BaseballSlot
from minimax.game_state import GameState


class DraftState(GameState):
    def __init__(self, game_info: DraftGameInfo, ranked_players: list, drafted: set, lineups: list, current_player: int,
                 is_next_larger):
        super().__init__()
        self.game_info = game_info
        self.ranked_players = ranked_players
        self.lineups = lineups
        self.drafted = drafted
        self.current_player = current_player
        self.is_next_larger = is_next_larger

    def children(self) -> List['GameState']:
        # for player who's playing, get lineup, run over top x players at each position
        # add to drafted set
        relevant_lineup = self.lineups[self.current_player]
        new_states = []
        for baseball_player, slot_to_fill in self._possible_additions(self.current_player):
            # add player to deepcopy of this lineup (shallow copy of all lineups)
            successor_lineups = copy(self.lineups)
            next_lineup = deepcopy(relevant_lineup)
            current_in_slot = next_lineup.player_dict.get(slot_to_fill, [])
            current_in_slot.append(baseball_player)
            next_lineup.player_dict[slot_to_fill] = current_in_slot
            successor_lineups[self.current_player] = next_lineup
            # add player to copy of drafted
            successor_drafted = copy(self.drafted)
            successor_drafted.add(baseball_player)
            next_state = DraftState(self.game_info, self.ranked_players, successor_drafted, successor_lineups,
                                    self._next_player(), self._next_direction())
            new_states.append(next_state)
        return new_states

    def _next_player(self):
        if self.current_player == 0:
            return 1 if self.is_next_larger else 0
        if self.current_player == self.game_info.total_players - 1:
            return self.current_player if self.is_next_larger else self.current_player - 1
        return self.current_player + 1 if self.is_next_larger else self.current_player - 1

    def _next_direction(self):
        if self.current_player not in {0, self.game_info.total_players - 1}:
            return self.is_next_larger
        return self.current_player == 0

    def _possible_additions(self, player_index) -> list:
        relevant_lineup = self.lineups[player_index]
        open_slots = []
        for ls, count in self.game_info.lineup_settings.slot_counts.items():
            if len(relevant_lineup.player_dict.get(ls, [])) < count:
                open_slots.append(ls)

        possible_additions = []

        for player in first_n_not_drafted(self.ranked_players, self.drafted, 5):
            fillable_slots = filter(lambda slot: player.can_play(slot), open_slots)
            sorted_bench_last = sorted(fillable_slots, key=slot_value, reverse=True)
            slot_to_fill = next(iter(sorted_bench_last), None)
            if slot_to_fill is None:
                continue
            possible_additions.append((player, slot_to_fill))

        return possible_additions

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
