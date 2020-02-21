import logging
from math import isclose, sqrt
from statistics import NormalDist
from typing import List, Optional

from draft.draft_game_info import DraftGameInfo
from draft.draft_state import DraftState
from espn.baseball.baseball_position import BaseballPosition
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from lineup import Lineup
from minimax.state_evaluator import StateEvaluator
from scoring_setting import ScoringSetting
from stats import Stats

LOGGER = logging.getLogger('draft.draft_state_evaluator')


class DraftStateEvaluator(StateEvaluator):

    def __init__(self, player_projections: dict, scoring_settings: List[ScoringSetting]):
        """
        Evaluates different draft states for the value they represent to all players of a draft.
        Bases values on given player projections.
        :param player_projections: maps player names to their year's projections
        """
        self.player_projections = player_projections
        self.scoring_settings = scoring_settings

    def _get_projection(self, name: str) -> Optional[Stats]:
        replaced_name = {
            'Nicholas Castellanos': 'Nick Castellanos'
        }.get(name, name)

        proj = self.player_projections.get(replaced_name)
        if proj is None:
            LOGGER.warning(f'NO PROJECTIONS FOR {name}')
        return proj

    def heuristic(self, game_state: DraftState, game_info: DraftGameInfo):
        return []

    def terminal_state_value(self, game_state: DraftState, game_info: DraftGameInfo):
        totals = list(map(self._cumulative_stats, game_state.lineups))
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
            values_for_stat = self._accrued_value_in_league(list(map(lambda stats: stats.unrounded_value_for_stat(ss.stat), totals)),
                                                            ss.is_reverse,
                                                            stat_std_devs[ss.stat])
            LOGGER.debug(f'Accrued for {ss.stat}:')
            LOGGER.debug(values_for_stat)
            for i, val in enumerate(values_for_stat):
                values[i] += val
        return values

    def _accrued_value_in_league(self, stat_values: List[float], is_reverse: bool, std_dev) -> List[float]:
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
                    result[second] += (1 - p_second_greater)
                    result[first] += p_second_greater
                else:
                    result[second] += p_second_greater
                    result[first] += (1 - p_second_greater)
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
            total_stats += self._get_projection(p.name) or Stats({}, BaseballStat) * self.likelihood(p, lineup)

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
        map(lambda tup: tup[0], sorted(enumerate(values), reverse=is_reverse, key=lambda tup: tup[1])))
    i = 0
    while i < len(positions_ranked):
        j = i + 1
        cur_value = values[positions_ranked[i]]
        while j < len(positions_ranked) and isclose(cur_value, values[positions_ranked[j]], rel_tol=1e-09, abs_tol=0.0):
            j += 1
        points_to_split = sum(points_by_pos[i:j])
        for points_index in range(i, j):
            points[positions_ranked[points_index]] = points_to_split / len(range(i, j))
        i = j
    return points
