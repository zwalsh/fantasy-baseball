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
    best_lineup_for_stat = dict()

    for lineup in lineup.possible_starting_hitters(lineup_settings):
        cumulative_stats = stats_with_projections(lineup, projections)
        for scoring_stat in scoring_settings:
            cur_starters_value = cumulative_stats.value_for_stat(scoring_stat.stat)
            if cur_starters_value is None:
                continue
            cur_max = best_lineup_for_stat.get(scoring_stat.stat)
            if cur_max is None:
                best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)
            else:
                (max_value, cur_max_starters) = cur_max
                if scoring_stat.is_reverse and max_value > cur_starters_value:
                    best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)
                elif not scoring_stat.is_reverse and max_value < cur_starters_value:
                    best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)

    for stat in best_lineup_for_stat.keys():
        _, lineup = best_lineup_for_stat[stat]
        best_lineup_for_stat[stat] = lineup

    return best_lineup_for_stat


def stats_with_projections(lineup, projections):
    """
    Calculates the accumulated statistics of this set of starters, based on the given projections
    for each player
    :param Lineup lineup: the lineup of players that are starting
    :param dict projections: the projected stats that those players will accrue
    :return Stats: a Stats object holding their cumulative totals
    """
    stats = Stats({})

    for starter in lineup.starters():
        projection = projections.get(starter.name)
        if projection is not None:
            stats += projection

    for stat, value in stats.stat_dict.items():
        stats.stat_dict[stat] = round(value, 2)

    return stats
