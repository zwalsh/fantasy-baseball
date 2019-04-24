import copy
from itertools import combinations


class Lineup:
    slots = [(0, "C"),
             (1, "1B"),
             (2, "2B"),
             (3, "3B"),
             (4, "SS"),
             (6, "2B/SS"),
             (7, "1B/3B"),
             (5, "OF"),
             (12, "UTIL"),
             (13, "P"),
             (16, "BE"),
             (17, "IL")]

    hitting_slots = {0, 1, 2, 3, 4, 5, 6, 7, 12}

    def __init__(self, player_dict):
        """
        Accepts a map from LineupSlot to list of Player saying which players are
        currently lined up in each slot
        :param dict player_dict: map from LineupSlot to list of players
        """
        self.player_dict = player_dict

    def possible_starting_hitters(self, lineup_settings):
        """
        settings -> {starters, ...}

        :param lineup_settings:
        :return: set of all possible combinations of starting hitters
        """
        lineups = [(Lineup(dict()), self.players(), Lineup.hitting_slots.copy())]
        all_starters = set()
        total_proc = 0

        while not len(lineups) == 0:
            (cur_lineup, remaining_players, slots_to_process) = lineups.pop(0)
            next_slot = slots_to_process.pop()
            slot_count = lineup_settings.slot_counts.get(next_slot)
            new_lineups = cur_lineup.add_players_for_slot(next_slot, slot_count, remaining_players)
            total_proc += len(new_lineups)
            if len(slots_to_process) == 0:
                for (new_lin, _) in new_lineups:
                    all_starters.add(new_lin.starters())
            else:
                for (new_lin, rem_play) in new_lineups:
                    created_lineup = (new_lin, rem_play, slots_to_process.copy())
                    lineups.insert(0, created_lineup)
        print("Possible starting combos: {} / {} lineups".format(len(all_starters), total_proc))
        return all_starters

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
        """
        Filters the given list of players to the ones eligible to play in
        the given Slot
        :param list slot: LineupSlots that match
        :param list players: players available to play
        :return:
        """
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
