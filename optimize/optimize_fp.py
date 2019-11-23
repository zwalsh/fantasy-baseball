import logging

import pickle

from functools import reduce

from espn.basketball.basketball_slot import BasketballSlot
from espn.basketball.basketball_stat import BasketballStat
from notifications.notifier import Notifier

LOGGER = logging.getLogger("optimize.optimize_fp")


def optimize_fp(espn, fantasysp, notifier):
    """
    Set the lineup that will maximize fantasy points.
    :param EspnApi espn: access to espn
    :param FantasySPApi fantasysp: access to FantasySP
    :param Notifier notifier: notifier for taking action
    """

    cur_lineup = espn.lineup()
    projections = fantasysp.players()
    LOGGER.info(f"num projections: {len(projections)}")

    poss_lineups = cur_lineup.possible_lineups(espn.lineup_settings(), BasketballSlot.starting_slots())

    player_to_proj = dict()
    for player in cur_lineup.players():
        projection = find_projection(projections, player.name)
        if projection is None:
            LOGGER.warning(f"No projection for {player.name}")
        else:
            LOGGER.info(f"Projection for {player.name:<30}{stats_to_fp(projection.stats)}")
        player_to_proj[player.name] = projection.stats if projection is not None else None

    # min/max least transitions, most points
    cur_max_points = 0.0
    cur_least_transitions = 0
    cur_best_lineup = cur_lineup
    for l in poss_lineups:
        fp = total_fp_given_starters(player_to_proj, l.starters())
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

    total_points = total_fp_given_starters(player_to_proj, cur_best_lineup.starters())
    LOGGER.info(f"Best lineup: {cur_best_lineup}, fp: {total_points}")

    transitions = cur_lineup.transitions(cur_best_lineup)
    player_to_fp = {name: stats_to_fp(stats) for name, stats in player_to_proj.items()}
    notifier.notify_set_fba_lineup(espn.team_name(), transitions, total_points, player_to_fp)
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
    :return float: number of fantasy points
    """
    return reduce(lambda so_far, starter: so_far + stats_to_fp(projections.get(starter.name)), starters, 0.0)


def stats_to_fp(stats):
    """

    :param stats:
    :return:
    """
    if stats is None:
        return 0.0
    else:
        return (stats.unrounded_value_for_stat(BasketballStat.FGM) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.FGA) or 0.0) * -1 + \
               (stats.unrounded_value_for_stat(BasketballStat.FTM) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.FTA) or 0.0) * -1 + \
               (stats.unrounded_value_for_stat(BasketballStat.REBOUNDS) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.ASSISTS) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.STEALS) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.BLOCKS) or 0.0) * 1 + \
               (stats.unrounded_value_for_stat(BasketballStat.TURNOVERS) or 0.0) * -1 + \
               (stats.unrounded_value_for_stat(BasketballStat.POINTS) or 0.0) * 1


def find_projection(projections, name):
    """
    Given a list of PlayerProjections, finds the projection for the player with the given name.
    :param projections:
    :param name:
    :return:
    """
    return next(filter(lambda proj: proj.name == name, projections), None)
