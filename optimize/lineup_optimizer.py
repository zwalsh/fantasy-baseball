from stats import Stats


def print_lineup_optimization(espn, fangraphs):
    """
    Given an ESPN api object, prints the lineup optimization information for today.

    Temporary home for this code until it can be formalized and somehow made into a web app
    :param EspnApi espn: access to ESPN for a team/league
    :param FangraphsApi fangraphs: access to Fangraphs to get projections
    :return:
    """
    current_lineup = espn.lineup(espn.team_id)
    lineup_settings = espn.lineup_settings()

    scoring_settings = espn.scoring_settings()

    proj = fangraphs.hitter_projections()

    max_lineup_for_stats = optimize_lineup(current_lineup, lineup_settings, proj, scoring_settings)

    lineup_maxes = dict()
    print("CURRENT LINEUP")
    print(current_lineup)
    print(stats_with_projections(current_lineup, proj))

    for stat, best_lineup in max_lineup_for_stats.items():
        cur_bests = lineup_maxes.get(best_lineup.starters(), [best_lineup])
        cur_bests.append(stat)
        lineup_maxes[best_lineup.starters()] = cur_bests

    for bests in lineup_maxes.values():
        lineup = bests[0]
        stats = stats_with_projections(lineup, proj)
        transitions = current_lineup.transitions(lineup)
        print(lineup)
        for t in transitions:
            print(t)
        print(stats)
        print("Best for:")
        for best in bests[1:]:
            print("{}".format(best))
        print("\n\n\n")


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
