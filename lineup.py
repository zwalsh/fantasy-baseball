from itertools import combinations
import copy


class Lineup:
    def __init__(self, player_dict):
        # map from slot -> [Player, ...]
        self.player_dict = player_dict

    def possible_lineups(self, lineup_settings):
        slot_lists = self.player_dict.values()
        players = []
        for sl in slot_lists:
            players.extend(sl)

        lineups = [(Lineup(dict()), players)]

        for slot in lineup_settings.slot_counts.keys():
            print("Adding all combos of {} to {} lineups".format(slot, len(lineups)))
            new_lineups = []
            for lineup, remaining_players in lineups:
                candidates = list(filter(lambda player: player.can_play(slot), remaining_players))
                count = lineup_settings.slot_counts.get(slot)
                possible_combos = list(combinations(candidates, count))
                if len(possible_combos) == 0:
                    new_lineups.append((lineup, remaining_players))
                for players in possible_combos:
                    l_copy = lineup.copy()
                    rem_copy = copy.copy(remaining_players)
                    rem_copy = list(filter(lambda p: p not in players, rem_copy))
                    l_copy.player_dict[slot] = players
                    new_lineups.append((l_copy, rem_copy))
            lineups = new_lineups
        return list(map(lambda l_rem: l_rem[0], filter(lambda l_rem: len(l_rem[1]) == 0, lineups)))

    def copy(self):
        new_dict = dict()
        for slot in self.player_dict.keys():
            new_list = copy.copy(self.player_dict.get(slot))
            new_dict[slot] = new_list
        return Lineup(new_dict)

    def starters(self):
        starters = set()
        for slot, players in self.player_dict.items():
            if slot != 16:  # the bench
                starters.update(players)
        return frozenset(starters)

    def benched(self):
        return frozenset(self.player_dict[16])

    # [(Player, from_slot, to_slot), ...]
    def transitions(self, to_lineup):
        transitions = []

        for slot, players in self.player_dict.items():
            for player in players:
                if player not in to_lineup.player_dict.get(slot, []):
                    to_slots = to_lineup.player_dict.keys()
                    to_slot = list(filter(lambda s: player in to_lineup.player_dict[s], to_slots))[0]

                    t = (player, slot, to_slot)
                    transitions.append(t)

        return transitions
