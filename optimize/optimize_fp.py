import logging

from functools import reduce

from espn.basketball.basketball_slot import BasketballSlot

LOGGER = logging.getLogger("optimize.optimize_fp")


def optimize_fp(espn, fantasysp, notifier):
    """
    Set the lineup that will maximize fantasy points.
    :param EspnApi espn: access to espn
    :param FantasySPApi fantasysp: access to FantasySP
    :param Notifier notifier: notifier for taking action
    """

    points_map = espn.points_per_stat()
    cur_lineup = espn.lineup()
    projections = fantasysp.players()
    LOGGER.info(f"num projections: {len(projections)}")

    poss_lineups = cur_lineup.possible_lineups(
        espn.lineup_settings(), BasketballSlot.starting_slots()
    )

    player_to_proj = dict()
    for player in cur_lineup.players():
        projection = find_projection(projections, player.name)
        if projection is None:
            LOGGER.warning(f"No projection for {player.name}")
        else:
            LOGGER.info(
                f"Projection for {player.name:<30}{stats_to_fp(projection.stats, points_map)}"
            )
        player_to_proj[player.name] = (
            projection.stats if projection is not None else None
        )

    # min/max least transitions, most points
    cur_max_points = 0.0
    cur_least_transitions = 0
    cur_best_lineup = cur_lineup
    for l in poss_lineups:
        fp = total_fp_given_starters(player_to_proj, l.starters(), points_map)
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

    total_points = total_fp_given_starters(player_to_proj, cur_best_lineup.starters(), points_map)
    LOGGER.info(f"Best lineup: {cur_best_lineup}, fp: {total_points}")

    transitions = cur_lineup.transitions(cur_best_lineup)
    player_to_fp = {name: stats_to_fp(stats, points_map) for name, stats in player_to_proj.items()}
    notifier.notify_set_fba_lineup(
        espn.team_name(), transitions, total_points, player_to_fp
    )
    try:
        if len(transitions) > 0:
            espn.set_lineup(cur_best_lineup)
    except Exception as e:
        LOGGER.exception(e)
        notifier.error_occurred()
        raise e


def total_fp_given_starters(projections, starters, points_map):
    """
    Returns the number of fantasy points given the set of starters
    :param dict projections: map of player name to projected fantasy points
    :param set starters: set of starters
    :param dict points_map: points per basketball stat
    :return float: number of fantasy points
    """
    return reduce(
        lambda so_far, starter: so_far + stats_to_fp(projections.get(starter.name), points_map),
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
