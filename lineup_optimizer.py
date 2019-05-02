from stats import Stats


def optimize_lineup(lineup, lineup_settings, projections, scoring_settings):
    """
    Returns a dictionary mapping stat id to set of starters that has the best value.
    :param Lineup lineup: the lineup to optimize
    :param lineup_settings:
    :param dict projections: mapping of hitter name to Stats
    :param scoring_settings:
    :return:
    """
    maximums = dict()

    for starters in lineup.possible_starting_hitters(lineup_settings):
        cumulative_stats = stats_with_projections(starters, projections)
        for scoring_stat in scoring_settings:
            cur_starters_value = cumulative_stats.value_for_stat(scoring_stat.stat)
            if cur_starters_value is None:
                continue
            cur_max = maximums.get(scoring_stat.stat)
            if cur_max is None:
                maximums[scoring_stat.stat] = (cur_starters_value, starters)
            else:
                (max_value, cur_max_starters) = cur_max
                if scoring_stat.is_reverse and max_value > cur_starters_value:
                    maximums[scoring_stat.stat] = (cur_starters_value, starters)
                elif not scoring_stat.is_reverse and max_value < cur_starters_value:
                    maximums[scoring_stat.stat] = (cur_starters_value, starters)

    for stat in maximums.keys():
        _, starters = maximums[stat]
        maximums[stat] = starters

    return maximums


def stats_with_projections(starters, projections):
    """
    Calculates the accumulated statistics of this set of starters, based on the given projections
    for each player
    :param set starters: the set of players that are starting
    :param dict projections: the projected stats that those players will accrue
    :return Stats: a Stats object holding their cumulative totals
    """
    stats = Stats({})

    for starter in starters:
        projection = projections.get(starter.name)
        if projection is not None:
            stats += projection

    return stats
