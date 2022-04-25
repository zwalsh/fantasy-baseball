import logging

from functools import reduce
from typing import Dict

from espn.basketball.basketball_api import BasketballApi
from espn.basketball.basketball_slot import BasketballSlot
from fantasysp.api import FantasySPApi

LOGGER = logging.getLogger("optimize.optimize_fp")


def player_to_fp(fantasysp: FantasySPApi, espn: BasketballApi) -> Dict[str, float]:
    """
    Returns a map from name to points for each player based on the fantasy sports api.

    Currently, FantasySPApi is behind a paywall :( refactoring in case it comes back
    """
    projections = fantasysp.players()
    points_map = espn.points_per_stat()
    return {player_proj.name: stats_to_fp(player_proj.stats, points_map)
            for player_proj in projections}


def optimize_fp(espn, player_to_points: Dict[str, float], notifier):
    """
    Set the lineup that will maximize fantasy points.
    :param EspnApi espn: access to espn
    :param player_to_points: the number of fantasy points each player is projected to get
    :param Notifier notifier: notifier for taking action
    """

    cur_lineup = espn.lineup()
    LOGGER.info(f"num projections: {len(player_to_points)}")

    poss_lineups = cur_lineup.possible_lineups(
        espn.lineup_settings(), BasketballSlot.starting_slots()
    )

    for player in cur_lineup.players():
        projection = player_to_points.get(player.name)
        if projection is None:
            LOGGER.warning(f"No projection for {player.name}")
        else:
            LOGGER.info(f"Projection for {player.name:<30}{projection}")

    # min/max least transitions, most points
    cur_max_points = 0.0
    cur_least_transitions = 0
    cur_best_lineup = cur_lineup
    for l in poss_lineups:
        fp = total_fp_given_starters(player_to_points, l.starters())
        if cur_max_points + 0.1 > fp > cur_max_points - 0.1:
            num_transitions = len(cur_lineup.transitions(l))
            if num_transitions < cur_least_transitions:
                cur_best_lineup = l
                cur_least_transitions = num_transitions
                cur_max_points = fp
        if fp > cur_max_points + 0.1:
            cur_best_lineup = l
            cur_least_transitions = len(cur_lineup.transitions(l))
            cur_max_points = fp

    total_points = total_fp_given_starters(player_to_points, cur_best_lineup.starters())
    LOGGER.info(f"Best lineup: {cur_best_lineup}, fp: {total_points}")

    transitions = cur_lineup.transitions(cur_best_lineup)
    notifier.notify_set_fba_lineup(
        espn.team_name(), transitions, total_points, player_to_points
    )
    try:
        if len(transitions) > 0:
            espn.set_lineup(cur_best_lineup)
    except Exception as e:
        LOGGER.exception(e)
        notifier.error_occurred()
        raise e


def total_fp_given_starters(projections, starters):
    """
    Returns the number of fantasy points given the set of starters
    :param dict projections: map of player name to projected fantasy points
    :param set starters: set of starters
    """
    return reduce(
        lambda so_far, starter: so_far + projections.get(starter.name, 0.0),
        starters,
        0.0,
    )


def stats_to_fp(stats, points_map):
    """

    :param stats:
    :return:
    """
    if stats is None:
        return 0.0

    total = 0.0
    for stat, value in stats.stat_dict.items():
        total += points_map.get(stat, 0.0) * value
    return total


def find_projection(projections, name):
    """
    Given a list of PlayerProjections, finds the projection for the player with the given name.
    :param projections:
    :param name:
    :return:
    """
    return next(filter(lambda proj: proj.name == name, projections), None)
