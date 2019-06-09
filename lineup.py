import copy
import logging
from itertools import combinations

import time

from lineup_slot import LineupSlot
from lineup_transition import LineupTransition

LOGGER = logging.getLogger("lineup")


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
        Calculates all possible sets of starting hitters.
         For each set of starting hitters, it calculates the lineup with that set
         of starters that is closest to this one.
        Returns a set of such lineups.
        :param LineupSettings lineup_settings:
        :return set: set of lineups with all combinations of starters
        """
        initial_node = LineupSearchNode(Lineup(dict()), self.players(), Lineup.hitting_slots.copy())
        # stack of nodes representing the frontier of the search graph
        frontier = [initial_node]
        max_starters = lineup_settings.total_for_slots(Lineup.hitting_slots)

        all_starters = dict()
        total_proc = 0
        max_stack = 0
        total_stack = 0

        start_time = time.time()
        LOGGER.info("generating all possible lineups")

        while not len(frontier) == 0:
            total_stack += len(frontier)
            node = frontier.pop(0)
            successors = node.successors(lineup_settings)
            total_proc += 1
            if total_proc % 1000 == 0:
                LOGGER.debug("processed {}".format(total_proc))
            max_stack = max(max_stack, len(frontier))
            for successor in successors:
                starters = successor.lineup.starters()
                if len(starters) == max_starters:
                    self.add_lineup_to_unique_starters(successor.lineup, all_starters)
                elif not successor.all_slots_filled():
                    frontier.insert(0, successor)
        end_time = time.time()
        info_dict = {
            "starters": len(all_starters),
            "total": total_proc,
            "max_stack": max_stack,
            "avg_stack": total_stack / float(total_proc),
            "elapsed": end_time - start_time
        }
        LOGGER.info("possible starting combos: %(starters)d / %(total)d lineups,"
                    " max stack: %(max_stack)d, avg stack: %(avg_stack).3f, time: %(elapsed).3fs", info_dict)
        return all_starters.values()

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
            if slot != LineupSlot.BENCH:
                starters.update(players)
        return frozenset(starters)

    def benched(self):
        return frozenset(self.player_dict[LineupSlot.BENCH])

    def injured(self):
        return frozenset(self.player_dict[LineupSlot.INJURED])

    def transitions(self, to_lineup):
        """
        Returns a list of all transitions necessary to convert this Lineup into the given one.
        If a Player in this Lineup is not in the given Lineup, it is assumed to be on the bench of
        the given one.
        :param Lineup to_lineup: the Lineup to create transitions for
        :return list: the list of LineupTransitions necessary to move to the given Lineup
        """
        transitions = []

        for slot, players in self.player_dict.items():
            for player in players:
                if player not in to_lineup.player_dict.get(slot, []):
                    to_slots = to_lineup.player_dict.keys()
                    to_slot = next(filter(lambda s: player in to_lineup.player_dict[s], to_slots), LineupSlot.BENCH)
                    if slot != to_slot and slot != LineupSlot.PITCHER and slot != LineupSlot.INJURED:
                        transitions.append(LineupTransition(player, slot, to_slot))

        return transitions

    def add_lineup_to_unique_starters(self, lineup, all_starters):
        """
        Adds the given lineup to the given dictionary of starters to lineups.
        If the lineup's starters are not in the map, it adds them to the map.
        If they are, it will replace the current value with the given lineup if this
        lineup requires fewer transitions to produce the given one.
        :param Lineup lineup: the lineup to add to the dictionary
        :param dict all_starters: the dictionary from starters to closest lineup
        """
        cur_lineup = all_starters.get(lineup.starters(), lineup)
        cur_lineup_transitions = len(self.transitions(cur_lineup))
        given_lineup_transitions = len(self.transitions(lineup))
        if cur_lineup_transitions < given_lineup_transitions:
            all_starters[lineup.starters()] = cur_lineup
        else:
            all_starters[lineup.starters()] = lineup

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
