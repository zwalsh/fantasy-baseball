import logging
from functools import reduce
from math import isclose, sqrt
from statistics import NormalDist
from typing import List, Optional

from draft.draft_game_info import DraftGameInfo
from draft.draft_state import DraftState, slot_value
from espn.baseball.baseball_position import BaseballPosition
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from lineup import Lineup
from lineup_settings import LineupSettings
from minimax.state_evaluator import StateEvaluator
from player import Player
from scoring_setting import ScoringSetting
from stats import Stats

LOGGER = logging.getLogger("draft.draft_state_evaluator")


class DraftStateEvaluator(StateEvaluator):
    def __init__(
        self,
        player_projections: dict,
        scoring_settings: List[ScoringSetting],
        players_ranked: List[Player],
    ):
        """
        Evaluates different draft states for the value they represent to all players of a draft.
        Bases values on given player projections.
        :param players_ranked: list of player names, ranking them best to worst
        :param player_projections: maps player names to their year's projections
        """
        self.player_projections = player_projections
        self.scoring_settings = scoring_settings
        self.players_ranked = players_ranked
        self.averages_cache = dict()
        self.total_heuristics = 0

    def _get_projection(self, name: str) -> Optional[Stats]:
        replaced_name = {"Nicholas Castellanos": "Nick Castellanos"}.get(name, name)

        proj = self.player_projections.get(replaced_name)
        if proj is None:
            LOGGER.warning(f"NO PROJECTIONS FOR {name}")
        return proj

    # @timed(LOGGER)
    def heuristic(self, game_state: DraftState, game_info: DraftGameInfo):
        self.total_heuristics += 1
        if self.total_heuristics % 1000 == 0:
            LOGGER.info(f"Calculated {self.total_heuristics} heuristics")
        empty_slots = slots_to_fill(game_state.lineups, game_info.lineup_settings)
        available_players = list(
            filter(lambda p: p not in game_state.drafted, self.players_ranked)
        )

        best_available = dict()
        players_taken = set()
        # fill slots
        slot_counts = game_info.lineup_settings.slot_counts
        draftable_slots = filter(
            lambda s: s != BaseballSlot.INJURED, slot_counts.keys()
        )
        for slot in sorted(draftable_slots, key=slot_value, reverse=True):
            if (slot, empty_slots[slot]) in self.averages_cache.keys():
                best_available[slot] = []
                continue
            players_needed = empty_slots[slot]
            available_index = 0
            while players_needed > 0 and available_index < len(available_players):
                next_best = available_players[available_index]
                if next_best not in players_taken and next_best.can_play(slot):
                    best_available[slot] = best_available.get(slot, []) + [next_best]
                    players_taken.add(next_best)
                    players_needed -= 1
                available_index += 1

        averages = {}
        for slot, players in best_available.items():
            averages_cache_key = (slot, empty_slots[slot])
            cached = self.averages_cache.get(averages_cache_key)
            if cached is not None:
                averages[slot] = cached
                continue
            # self.averages_cache[(slot, len(players))] = self.averages_cache.get((slot, len(players)), 0) + 1
            projections = list(
                map(self._get_projection, map(lambda p: p.name, players))
            )
            total = reduce(Stats.__add__, projections)
            average = total / len(players)
            averages[slot] = average
            self.averages_cache[averages_cache_key] = average

        totals = []
        for lineup in game_state.lineups:
            so_far = self._cumulative_stats(lineup)
            for slot, count in slot_counts.items():
                count_to_fill = count - len(lineup.player_dict.get(slot, []))
                amount_to_add = (
                    averages.get(slot, Stats({}, BaseballStat)) * count_to_fill
                )
                so_far += amount_to_add
            totals += [so_far]
        return self.values_from_totals(game_info, totals)

    def terminal_state_value(self, game_state: DraftState, game_info: DraftGameInfo):
        totals = list(map(self._cumulative_stats, game_state.lineups))
        return self.values_from_totals(game_info, totals)

    def values_from_totals(self, game_info, totals):
        values = [0] * game_info.total_players
        stat_std_devs = {
            BaseballStat.R: 50.0,
            BaseballStat.RBI: 100.0,
            BaseballStat.AVG: 0.003,
            BaseballStat.AB: 1000.0,
            BaseballStat.H: 200.0,
            BaseballStat.HR: 40.0,
            BaseballStat.SB: 10.0,
            BaseballStat.BB: 50.0,
            BaseballStat.OBP: 0.008,
            BaseballStat.W: 7.0,
            BaseballStat.K: 100.0,
            BaseballStat.SV: 10.0,
            BaseballStat.ER: 50.0,
            BaseballStat.OUTS: 200.0,
            BaseballStat.ERA: 0.01,
            BaseballStat.WHIP: 0.008,
        }
        for ss in self.scoring_settings:
            values_for_stat = self._accrued_value_in_league(
                [stats.unrounded_value_for_stat(ss.stat) for stats in totals],
                ss.is_reverse,
                stat_std_devs[ss.stat],
            )
            for i, val in enumerate(values_for_stat):
                values[i] += val
        return values

    def _accrued_value_in_league(
        self, stat_values: List[float], is_reverse: bool, std_dev
    ) -> List[float]:
        """
        Given a list of accrued stat values, calculates the worth of each of those values.

        Worth is assigned as follows: best value gets n, worst value gets 1. From there, adjust
        the worth of each value based on distance to neighbors.
        :param std_dev:
        :param stat_values:
        :param is_reverse:
        :return:
        """
        result = [1] * len(stat_values)
        for first in range(0, len(stat_values)):
            for second in range(first + 1, len(stat_values)):
                mean_1 = stat_values[first]
                mean_2 = stat_values[second]
                variance = 2 * pow(std_dev, 2)
                first_minus_second = NormalDist(mean_1 - mean_2, sqrt(variance))
                p_second_greater = first_minus_second.cdf(0)
                if is_reverse:
                    result[second] += 1 - p_second_greater
                    result[first] += p_second_greater
                else:
                    result[second] += p_second_greater
                    result[first] += 1 - p_second_greater
        return result

    def _cumulative_stats(self, lineup: Lineup):
        """
        Calculates an approximation of the final statistics of this lineup, assuming
        ideal management (setting lineups daily, etc.)
        :param Lineup lineup: the lineup to examine and use to calculate stats
        :return Stats: the accumulated, year-end total stats
        """
        total_stats = Stats({}, BaseballStat)
        for p in lineup.starters():
            total_stats += self._get_projection(p.name) or Stats({}, BaseballStat)
        for p in lineup.benched():
            total_stats += self._get_projection(p.name) or Stats(
                {}, BaseballStat
            ) * self.likelihood(p, lineup)

        return total_stats

    def likelihood(self, p, lineup):
        """
        Returns the likelihood that player P will be able to start on any day
        :param p:
        :param lineup:
        :return:
        """
        if p.default_position in {BaseballPosition.STARTER, BaseballPosition.RELIEVER}:
            return 1.0
        p_none_open = 1.0
        for slot in BaseballSlot.starting_slots().intersection(p.possible_positions):
            for starter in lineup.player_dict.get(slot, []):
                proj = self._get_projection(starter.name)
                pas = proj.plate_appearances()
                likelihood_playing = min(1, pas / 650) * (162 / 183)
                p_none_open *= likelihood_playing
        projected_pas = self._get_projection(p.name).plate_appearances()
        likelihood_available = projected_pas / 650 * (162 / 183)
        return (1 - p_none_open) * likelihood_available


def rank_values(values: List[float], is_reverse: bool) -> List[float]:
    points_by_pos = range(1, len(values) + 1)
    points = [0.0] * len(values)
    positions_ranked = list(
        map(
            lambda tup: tup[0],
            sorted(enumerate(values), reverse=is_reverse, key=lambda tup: tup[1]),
        )
    )
    i = 0
    while i < len(positions_ranked):
        j = i + 1
        cur_value = values[positions_ranked[i]]
        while j < len(positions_ranked) and isclose(
            cur_value, values[positions_ranked[j]], rel_tol=1e-09, abs_tol=0.0
        ):
            j += 1
        points_to_split = sum(points_by_pos[i:j])
        for points_index in range(i, j):
            points[positions_ranked[points_index]] = points_to_split / len(range(i, j))
        i = j
    return points


def slots_to_fill(lineups: List[Lineup], settings: LineupSettings) -> dict:
    """
    Determines the total count to fill for each slot across all lineups
    """
    empty_counts = dict()
    for lineup in lineups:
        for slot, count in settings.slot_counts.items():
            empty_counts[slot] = (
                empty_counts.get(slot, 0)
                + count
                - len(lineup.player_dict.get(slot, []))
            )
    return empty_counts
