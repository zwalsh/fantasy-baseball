from stats import Stats


def optimize_lineup(lineup, lineup_settings, projections, scoring_settings):
    """
    Returns a dictionary mapping stat id to set of starters that has the best value.
    :param lineup:
    :param lineup_settings:
    :param projections:
    :param scoring_settings:
    :return:
    """
    maximums = dict()

    for starters in lineup.possible_starting_hitters(lineup_settings):
        stats = stats_with_projections(starters, projections)
        for scoring_stat in scoring_settings:
            cur_starters_value = stats.value_for_stat(scoring_stat.stat_id)
            if cur_starters_value is None:
                continue
            cur_max = maximums.get(scoring_stat.stat_id)
            if cur_max is None:
                maximums[scoring_stat.stat_id] = (cur_starters_value, starters)
            else:
                (max_value, cur_max_starters) = cur_max
                if scoring_stat.is_reverse and max_value > cur_starters_value:
                    maximums[scoring_stat.stat_id] = (cur_starters_value, starters)
                elif not scoring_stat.is_reverse and max_value < cur_starters_value:
                    maximums[scoring_stat.stat_id] = (cur_starters_value, starters)

    for stat_id in maximums.keys():
        _, starters = maximums[stat_id]
        maximums[stat_id] = starters

    return maximums


def stats_with_projections(starters, projections):
    stats = Stats({})

    for starter in starters:
        projection = projections.get(starter.name)
        if projection is not None:
            stats += projection

    return stats
