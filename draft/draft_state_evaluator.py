import logging

from draft.draft_game_info import DraftGameInfo
from draft.draft_state import DraftState
from espn.baseball.baseball_position import BaseballPosition
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from lineup import Lineup
from minimax.state_evaluator import StateEvaluator
from stats import Stats

LOGGER = logging.getLogger('draft.draft_state_evaluator')


class DraftStateEvaluator(StateEvaluator):

    def __init__(self, player_projections: dict):
        """
        Evaluates different draft states for the value they represent to all players of a draft.
        Bases values on given player projections.
        :param player_projections: maps player names to their year's projections
        """
        self.player_projections = player_projections

    def heuristic(self, game_state: DraftState, game_info: DraftGameInfo):
        return []

    def terminal_state_value(self, game_state: DraftState, game_info: DraftGameInfo):
        return []

    def _cumulative_stats(self, lineup: Lineup):
        """
        Calculates an approximation of the final statistics of this lineup, assuming
        ideal management (setting lineups daily, etc.)
        :param Lineup lineup: the lineup to examine and use to calculate stats
        :return Stats: the accumulated, year-end total stats
        """
        total_stats = Stats({}, BaseballStat)
        for p in lineup.starters():
            total_stats += self.player_projections[p.name]
        for p in lineup.benched():
            total_stats += self.player_projections[p.name] * self.likelihood(p, lineup)

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
            LOGGER.debug(f'Evaluating people in slot {slot}')
            for starter in lineup.player_dict.get(slot, []):
                proj = self.player_projections[starter.name]
                if proj is None:
                    LOGGER.error(f'NO PROJECTIONS FOR {starter.name}')
                    continue
                pas = proj.plate_appearances()
                likelihood_playing = min(1, pas / 650) * (162 / 183)
                LOGGER.debug(f'{starter}: {likelihood_playing:.3f} - {pas}')
                p_none_open *= likelihood_playing
        projected_pas = self.player_projections[p.name].plate_appearances()
        likelihood_available = projected_pas / 650 * (162 / 183)
        return (1 - p_none_open) * likelihood_available



