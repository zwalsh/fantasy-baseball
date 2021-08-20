import logging
import operator

from espn.baseball.baseball_position import BaseballPosition
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from lineup_transition import LineupTransition
from optimize.lineup_total import LineupTotal
from scoring_setting import ScoringSetting

# first - log/notify number of lineups to choose from within 95% of max PA
# then - choose best: first one to appear within some % of max of all categories

LOGGER = logging.getLogger("optimize.optimizer")


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
    LOGGER.info(f"Current lineup: {lineup}")
    l_settings = espn.lineup_settings()
    s_settings = espn.scoring_settings()
    hitting_settings = filter(
        lambda s: s.stat
        not in {
            BaseballStat.K,
            BaseballStat.W,
            BaseballStat.ERA,
            BaseballStat.WHIP,
            BaseballStat.SV,
        },
        s_settings,
    )

    hitter_projections = fangraphs.hitter_projections()
    possibles = possible_lineup_totals(lineup, l_settings, hitter_projections)
    best_pa = best_for_stat(lineup, possibles, ScoringSetting(BaseballStat.PA, False, 0.0))
    threshold = best_pa.stats.value_for_stat(BaseballStat.PA) * 0.95
    candidates = above_threshold_for_stat(
        possibles, ScoringSetting(BaseballStat.PA, False, 0.0), threshold
    )

    num_candidates = len(candidates)
    LOGGER.info(
        f"found {num_candidates} candidates within 95% of max PA's (above threshold {threshold})"
    )
    best_list = best_lineups(lineup, candidates, hitting_settings)
    most_pas_from_best = best_for_stat(
        lineup, best_list, ScoringSetting(BaseballStat.PA, False, 0.0)
    )
    LOGGER.info(f"Using lineup {most_pas_from_best.lineup}")

    hitting_transitions = lineup.transitions(most_pas_from_best.lineup)
    pitching_transitions = optimal_pitching_transitions(lineup, espn)
    notifier.notify_set_lineup(
        espn.team_name(),
        most_pas_from_best,
        hitting_transitions + pitching_transitions,
        s_settings,
    )
    if len(hitting_transitions + pitching_transitions) == 0:
        LOGGER.info("no transitions to execute")
    else:
        espn.execute_transitions(hitting_transitions + pitching_transitions)


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
        threshold -= 0.01
        LOGGER.debug(f"filtering candidates at threshold value {threshold}")
        passing = candidates_above_threshold(candidates, max_values, threshold)
    num_to_choose = len(passing)
    LOGGER.info(
        f"{num_to_choose} candidates pass for each stat at {round(threshold, 2)}"
    )
    return passing


def candidates_above_threshold(candidates, maxes, threshold_percentage):
    passing = candidates.copy()
    for (setting, value) in maxes:
        passing = above_threshold_for_stat(
            passing, setting, value * threshold_percentage
        )
        if len(passing) == 0:
            LOGGER.debug(
                f"none pass for {setting.stat} at value {value * threshold_percentage}"
            )
            return list()

    return list(passing)


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
    return list(
        filter(
            lambda lt: lt.passes_threshold(scoring_setting.stat, threshold, comp),
            totals,
        )
    )


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
    possibles = lineup.possible_lineups(lineup_settings, BaseballSlot.hitting_slots())
    return list(
        map(lambda l: LineupTotal.total_from_projections(l, projections), possibles)
    )


def optimal_pitching_transitions(lineup, espn):
    """
    Optimizes the pitching portion of the lineup, moving all probable pitchers and relievers into
    starting roles, benching a Starter that isn't starting if necessary.
    :param Lineup lineup: the current Lineup to optimize
    :param EspnApi espn: access to ESPN for the lineup being optimized
    """

    must_start = must_start_pitchers(lineup, espn)
    LOGGER.info(f"{len(must_start)} must-start pitchers found")
    for p in must_start:
        LOGGER.info(f"{p}")
    not_started = must_start - lineup.starters()
    LOGGER.info(f"{len(not_started)} not currently started")
    for p in not_started:
        LOGGER.info(f"{p}")

    benchables = benchable_pitchers(lineup, must_start)
    LOGGER.info(f"{len(benchables)} benchable pitchers found")
    for p in benchables:
        LOGGER.info(f"{p}")
    benchables = iter(benchables)

    transitions = []
    for ns in not_started:
        player_to_bench = next(benchables)
        LOGGER.info(f"starting {ns}, benching {player_to_bench}")
        transitions.append(
            LineupTransition(ns, BaseballSlot.BENCH, BaseballSlot.PITCHER)
        )
        transitions.append(
            LineupTransition(player_to_bench, BaseballSlot.PITCHER, BaseballSlot.BENCH)
        )

    return transitions


def must_start_pitchers(lineup, espn):
    """
    Determines all pitchers that are "must-starts" from the given lineup.

    This is any probable pitcher in today's games and any reliever, as all relievers
    could potentially play on any day. Any player currently in an IL slot is excluded.
    :param Lineup lineup: the lineup to get all must-start pitchers from
    :param EspnApi espn: access to ESPN for the given lineup
    :return set: the set of Players that are must-start pitchers today
    """
    players = lineup.players()
    pitchers = list(
        filter(lambda player: player.can_play(BaseballSlot.PITCHER), players)
    )
    probable_pitchers = {p for p in pitchers if espn.is_probable_pitcher(p.espn_id)}
    relievers = {p for p in pitchers if p.default_position == BaseballPosition.RELIEVER}
    return probable_pitchers.union(relievers).difference(lineup.injured())


def benchable_pitchers(lineup, must_start):
    """
    Given a lineup and a set of pitchers that must be started, returns the
    benchable ones.
    :param Lineup lineup: the lineup in which to find benchable pitchers
    :param set must_start: set of pitchers that must be started
    :return set: the group of pitchers that can be safely moved to the bench
    """
    started_pitchers = {
        player
        for player in lineup.starters()
        if player.default_position == BaseballPosition.STARTER
    }
    return started_pitchers - set(must_start)
