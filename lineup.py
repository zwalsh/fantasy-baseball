from itertools import combinations
import copy


class Lineup:
    slots = [(0, "C"),
             (1, "1B"),
             (2, "2B"),
             (3, "3B"),
             (4, "SS"),
             (6, "2B/SS"),
             (7, "1B/3B"),
             (5, "OF"),
             (13, "P"),
             (16, "BE"),
             (17, "IL")]

    def __init__(self, player_dict):
        # map from slot -> [Player, ...]
        self.player_dict = player_dict

    def possible_lineups(self, lineup_settings):
        lineups = [(Lineup(dict()), self.players())]
        for slot, count in lineup_settings.slot_counts.items():
            print("Slot: {}, Lineups: {}".format(slot, len(lineups)))
            new_lineups = []
            for lineup, remaining_players in lineups:
                new_lineups.extend(lineup.add_players_for_slot(slot, count, remaining_players))
            lineups = new_lineups
        return list(map(lambda l_rem: l_rem[0], filter(lambda l_rem: len(l_rem[1]) == 0, lineups)))

    def add_players_for_slot(self, slot, count, remaining_players):
        candidates = Lineup.candidates(slot, remaining_players)
        possible_combos = list(combinations(candidates, count))
        if len(possible_combos) == 0:
            return [(self, remaining_players)]
        new_lineups = []
        for players in possible_combos:
            l_copy = self.copy()
            rem_copy = copy.copy(remaining_players)
            rem_copy = list(filter(lambda p: p not in players, rem_copy))
            l_copy.player_dict[slot] = players
            new_lineups.append((l_copy, rem_copy))
        return new_lineups

    @staticmethod
    def candidates(slot, players):
        return list(filter(lambda player: player.can_play(slot), players))

    def copy(self):
        new_dict = dict()
        for slot in self.player_dict.keys():
            new_list = copy.copy(self.player_dict.get(slot))
            new_dict[slot] = new_list
        return Lineup(new_dict)

    def players(self):
        all_players = []
        for players_in_slot in self.player_dict.values():
            all_players.extend(players_in_slot)
        return all_players

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

    def __str__(self):
        result = ""
        for (slot, code) in Lineup.slots:
            result += code + "\n"
            for player in self.player_dict.get(slot, []):
                result += player.__str__() + "\n"
        return result
