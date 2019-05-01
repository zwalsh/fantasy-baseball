import copy
from itertools import combinations
from lineup_slot import LineupSlot


class Lineup:
    slots = [LineupSlot.CATCHER,
             LineupSlot.FIRST,
             LineupSlot.SECOND,
             LineupSlot.THIRD,
             LineupSlot.SHORT,
             LineupSlot.MIDDLE_INFIELD,
             LineupSlot.CORNER_INFIELD,
             LineupSlot.OUTFIELD,
             LineupSlot.UTIL,
             LineupSlot.BENCH,
             LineupSlot.PITCHER,
             LineupSlot.INJURED]

    hitting_slots = {LineupSlot.CATCHER,
                     LineupSlot.FIRST,
                     LineupSlot.SECOND,
                     LineupSlot.THIRD,
                     LineupSlot.SHORT,
                     LineupSlot.MIDDLE_INFIELD,
                     LineupSlot.CORNER_INFIELD,
                     LineupSlot.OUTFIELD,
                     LineupSlot.UTIL}

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
        initial_node = LineupSearchNode(Lineup(dict()), self.players(), Lineup.hitting_slots.copy())
        # list of nodes representing the frontier of the search graph
        frontier = [initial_node]
        all_starters = set()
        total_proc = 0

        while not len(frontier) == 0:
            node = frontier.pop(0)
            successors = node.successors(lineup_settings)

            for successor in successors:
                if successor.all_slots_filled():
                    all_starters.add(successor.lineup)
                else:
                    frontier.insert(0, successor)
        print("Possible starting combos: {} / {} lineups".format(len(all_starters), total_proc))
        return all_starters

    def add_players_for_slot(self, slot, count, remaining_players):
        """
        Generates all possible lineups that are the same as this one except
        count players from remaining_players have been added in slot
        :param LineupSlot slot: the slot in which to add players
        :param int count: the number of players to add
        :param list remaining_players: the players from which to choose
        :return: list of tuples, where each tuple is the new lineup and the remaining players
        """
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
        :param LineupSlot slot: the Slot that must match
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

        for slot in Lineup.slots:
            result += slot.name + "\n"
            for player in self.player_dict.get(slot, []):
                result += player.__str__() + "\n"
        return result


class LineupSearchNode:

    def __init__(self, lineup, players_left, slots_left):
        """
        Represents a node in a search of all possible lineups given a set of players.
        :param Lineup lineup: lineup of players currently assigned to slots in this search
        :param list players_left: list of players still available to be assigned
        :param set slots_left: set of slots that have yet to be filled
        """
        self.lineup = lineup
        self.players_left = players_left
        self.slots_left = slots_left

    def successors(self, lineup_settings):
        """
        Returns a list of all successors of this node in the graph search.

        Does so by picking a remaining slot, and generating all possible lineups
        where that slot is filled with some subset of the remaining players.

        Returns all
        :param LineupSettings lineup_settings: the restrictions for making new lineups
        :return: a list of all successor nodes
        """
        next_slot = self.slots_left.pop()
        slot_count = lineup_settings.slot_counts.get(next_slot)
        new_lineups = self.lineup.add_players_for_slot(next_slot, slot_count, self.players_left)
        successors = []
        for (new_lin, rem_players) in new_lineups:
            rem_slots = self.slots_left.copy()
            node = LineupSearchNode(new_lin, rem_players, rem_slots)
            successors.append(node)

        return successors

    def all_slots_filled(self):
        """
        Checks if all slots have been filled for this node.
        :return boolean: True if there are no slots left
        """
        return len(self.slots_left) == 0
