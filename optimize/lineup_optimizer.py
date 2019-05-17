import operator

import logging

from optimize.lineup_total import LineupTotal
from scoring_setting import ScoringSetting
from stats import Stats, Stat

# first - log/notify number of lineups to choose from within 95% of max PA
# then - choose best: first one to appear within some % of max of all categories

LOGGER = logging.getLogger('optimize.optimizer')


def optimize_lineup(espn, fangraphs, notifier):
    """
    Optimizes the lineup that is accessible from the given ESPN api object, with
    projections from the given Fangraphs api object. Notifies the notifier object
    of appropriate actions taken.
    :param EspnApi espn: API access to ESPN for a particular fantasy team
    :param FangraphsApi fangraphs: API access to Fangraphs projections
    :param Notifier notifier: wrapper around a Notifier client
    """
    lineup = espn.lineup()
    l_settings = espn.lineup_settings()
    s_settings = espn.scoring_settings()
    hitting_settings = filter(lambda s: s.stat not in {Stat.K, Stat.W, Stat.ERA, Stat.WHIP, Stat.SV}, s_settings)

    possibles = possible_lineup_totals(lineup, l_settings, fangraphs.hitter_projections())
    best_pa = best_for_stat(lineup, possibles, ScoringSetting(Stat.PA, False))
    threshold = best_pa.stats.value_for_stat(Stat.PA) * 0.95
    candidates = above_threshold_for_stat(possibles, ScoringSetting(Stat.PA, False), threshold)

    num_candidates = len(candidates)
    LOGGER.info(f"found {num_candidates} candidates within 95% of max PA's (above threshold {threshold})")
    best_list = best_lineups(lineup, candidates, hitting_settings)
    most_pas_from_best = best_for_stat(lineup, best_list, ScoringSetting(Stat.PA, False))
    pas = most_pas_from_best.stats.value_for_stat(Stat.PA)
    transitions = lineup.transitions(most_pas_from_best.lineup)
    notifier.notify_set_lineup(espn.team_name(), pas, transitions)
    espn.set_lineup(most_pas_from_best.lineup)


def best_lineups(current, candidates, scoring_settings):
    """
    Returns the best Lineups given a list of candidate LineupTotals and a list of ScoringSettings.
    Picks the Lineups that are within the highest possible percentage threshold of each
    maximum value across all scoring settings.

    :param Lineup current: the currently-set Lineup
    :param list candidates: the LineupTotals from which to choose a Lineup
    :param iter scoring_settings: the ScoringSettings to optimize over
    :return list: the best Lineups from the list
    """
    max_values = list()
    for setting in scoring_settings:
        lt = best_for_stat(current, candidates, setting)
        max_values.append((setting, lt.stats.value_for_stat(setting.stat)))

    threshold = 1.0
    passing = list()
    # while list of passing candidates is empty, decr. threshold by .01 and try again
    while len(passing) == 0:
        threshold -= .01
        LOGGER.debug(f"filtering candidates at threshold value {threshold}")
        passing = candidates_above_threshold(candidates, max_values, threshold)
    num_to_choose = len(passing)
    LOGGER.info(f"{num_to_choose} candidates pass for each stat at {round(threshold, 2)}")
    return passing


def candidates_above_threshold(candidates, maxes, threshold_percentage):
    passing = candidates.copy()
    for (setting, value) in maxes:
        passing = above_threshold_for_stat(passing, setting, value * threshold_percentage)
        if len(passing) == 0:
            LOGGER.debug(f"none pass for {setting.stat} at value {value * threshold_percentage}")
            return list()

    return list(passing)




# def print_lineup_optimization(espn, fangraphs):
#     """
#     Given an ESPN api object, prints the lineup optimization information for today.
#
#     Temporary home for this code until it can be formalized and somehow made into a web app
#     :param EspnApi espn: access to ESPN for a team/league
#     :param FangraphsApi fangraphs: access to Fangraphs to get projections
#     :return:
#     """
#     current_lineup = espn.lineup(espn.team_id)
#     lineup_settings = espn.lineup_settings()
#
#     scoring_settings = espn.scoring_settings()
#
#     proj = fangraphs.hitter_projections()
#
#     max_lineup_for_stats = optimize_lineup(current_lineup, lineup_settings, proj, scoring_settings)
#
#     lineup_maxes = dict()
#     print("CURRENT LINEUP")
#     print(current_lineup)
#     print(stats_with_projections(current_lineup, proj))
#
#     for stat, best_lineup in max_lineup_for_stats.items():
#         cur_bests = lineup_maxes.get(best_lineup.starters(), [best_lineup])
#         cur_bests.append(stat)
#         lineup_maxes[best_lineup.starters()] = cur_bests
#
#     for bests in lineup_maxes.values():
#         lineup = bests[0]
#         stats = stats_with_projections(lineup, proj)
#         transitions = current_lineup.transitions(lineup)
#         print(lineup)
#         for t in transitions:
#             print(t)
#         print(stats)
#         print("Best for:")
#         for best in bests[1:]:
#             print("{}".format(best))
#         print("\n\n\n")
#
#
# def optimize_lineup(lineup, lineup_settings, projections, scoring_settings):
#     """
#     Returns a dictionary mapping stat id to set of starters that has the best value.
#     :param Lineup lineup: the lineup to optimize
#     :param lineup_settings:
#     :param dict projections: mapping of hitter name to Stats
#     :param scoring_settings:
#     :return:
#     """
#     best_lineup_for_stat = dict()
#
#     for lineup in lineup.possible_starting_hitters(lineup_settings):
#         cumulative_stats = LineupTotal.total_from_projections(lineup, projections)
#         for scoring_stat in scoring_settings:
#             cur_starters_value = cumulative_stats.value_for_stat(scoring_stat.stat)
#             if cur_starters_value is None:
#                 continue
#             cur_max = best_lineup_for_stat.get(scoring_stat.stat)
#             if cur_max is None:
#                 best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)
#             else:
#                 (max_value, cur_max_starters) = cur_max
#                 if scoring_stat.is_reverse and max_value > cur_starters_value:
#                     best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)
#                 elif not scoring_stat.is_reverse and max_value < cur_starters_value:
#                     best_lineup_for_stat[scoring_stat.stat] = (cur_starters_value, lineup)
#
#     for stat in best_lineup_for_stat.keys():
#         _, lineup = best_lineup_for_stat[stat]
#         best_lineup_for_stat[stat] = lineup
#
#     return best_lineup_for_stat


def above_threshold_for_stat(totals, scoring_setting, threshold):
    """
    Returns the list of LineupTotals from the given list that exceed the given threshold for
    the given ScoringSetting.
    :param list totals: the list of LineupTotals to filter
    :param ScoringSetting scoring_setting: the ScoringSetting to filter with
    :param float threshold: the value that each LineupTotal must exceed
    :return list: all LineupTotals that pass the test
    """
    comp = operator.lt if scoring_setting.is_reverse else operator.gt
    return list(filter(lambda lt: lt.passes_threshold(scoring_setting.stat, threshold, comp), totals))


def best_for_stat(current, totals, scoring_setting):
    """
    Determines which LineupTotal from a list of LineupTotals is best for a given stat.

    Best is the LineupTotal that produces the maximum (or minimum) for that setting while also
    requiring the minimum transitions from the current lineup.

    :param Lineup current: the currently-set Lineup
    :param list totals: the LineupTotals that are possible from the given Lineup
    :param ScoringSetting scoring_setting: the setting for which to optimize
    :return LineupTotal: the LineupTotal that is best from the givens
    """
    max_total = totals[0]

    for cur_total in totals:
        better_comp = operator.gt if not scoring_setting.is_reverse else operator.lt
        if cur_total.compare(max_total, scoring_setting.stat, better_comp):
            max_total = cur_total
        elif cur_total.compare(max_total, scoring_setting.stat, operator.eq):
            max_transitions = current.transitions(max_total.lineup)
            cur_transitions = current.transitions(cur_total.lineup)
            if len(cur_transitions) < len(max_transitions):
                max_total = cur_total

    return max_total


def possible_lineup_totals(lineup, lineup_settings, projections):
    """
    From a single lineup (with the settings for that league) and the projections,
    produces a list of all possible LineupTotals.
    :param Lineup lineup: the current lineup to examine
    :param LineupSettings lineup_settings: the restrictions of the current league
    :param dict projections: a mapping of Player to projected Stats
    :return: list
    """
    possibles = lineup.possible_starting_hitters(lineup_settings)
    return list(map(lambda l: LineupTotal.total_from_projections(l, projections), possibles))
