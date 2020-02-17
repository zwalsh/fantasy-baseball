from copy import copy, deepcopy
from typing import List

from draft.draft_game_info import DraftGameInfo
from espn.baseball.baseball_slot import BaseballSlot
from minimax.game_state import GameState


class DraftState(GameState):
    def __init__(self, game_info: DraftGameInfo, players: dict, drafted: set, lineups: list):
        super().__init__()
        self.game_info = game_info
        self.players = players
        self.lineups = lineups
        self.drafted = drafted

    def children(self, player_index) -> List['GameState']:
        # for player who's playing, get lineup, run over top x players at each position
        # add to drafted set
        relevant_lineup = self.lineups[player_index]
        new_states = []
        for baseball_player, slot_to_fill in self._possible_additions(player_index):
            # add player to deepcopy of this lineup (shallow copy of all lineups)
            successor_lineups = copy(self.lineups)
            next_lineup = deepcopy(relevant_lineup)
            current_in_slot = next_lineup.player_dict.get(slot_to_fill, [])
            current_in_slot.append(baseball_player)
            next_lineup.player_dict[slot_to_fill] = current_in_slot
            successor_lineups[player_index] = next_lineup
            # add player to copy of drafted
            successor_drafted = copy(self.drafted)
            successor_drafted.add(baseball_player)
            next_state = DraftState(self.game_info, self.players, successor_drafted, successor_lineups)
            new_states.append(next_state)
        return new_states

    def _possible_additions(self, player_index) -> list:
        relevant_lineup = self.lineups[player_index]
        open_slots = []
        for ls, count in self.game_info.lineup_settings.slot_counts.items():
            if len(relevant_lineup.player_dict.get(ls, [])) < count:
                open_slots.append(ls)

        possible_additions = []
        for player in self.players.keys():
            if player in self.drafted:
                continue
            fillable_slots = filter(lambda slot: player.can_play(slot), open_slots)
            sorted_bench_last = sorted(fillable_slots, key=slot_value, reverse=True)
            slot_to_fill = next(iter(sorted_bench_last), None)
            if slot_to_fill is None:
                continue
            possible_additions.append((player, slot_to_fill))

        return possible_additions

    def is_terminal(self) -> bool:
        draftable_slots = filter(lambda tup: tup[0] != BaseballSlot.INJURED, self.game_info.lineup_settings.items())
        total_slots = sum(map(lambda tup: tup[1], draftable_slots)) * self.game_info.total_players
        return len(self.drafted) == total_slots


def slot_value(slot):
    return {
        BaseballSlot.BENCH: 0,
        BaseballSlot.UTIL: 1,
    }.get(slot, 2)
