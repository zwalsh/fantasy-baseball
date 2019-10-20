import logging

from espn.baseball.baseball_slot import BaseballSlot
from stats import Stat, Stats

espn_stat_to_stat = {
    0: Stat.AB,
    1: Stat.H,
    2: Stat.AVG,
    5: Stat.HR,
    10: Stat.BB,
    16: Stat.PA,
    17: Stat.OBP,
    20: Stat.R,
    21: Stat.RBI,
    23: Stat.SB,
    34: Stat.OUTS,  # can derive IP
    35: Stat.BATTERS,
    36: Stat.PITCHES,
    37: Stat.P_H,
    39: Stat.P_BB,
    41: Stat.WHIP,
    42: Stat.HBP,
    44: Stat.P_R,
    45: Stat.ER,
    46: Stat.P_HR,
    47: Stat.ERA,
    48: Stat.K,
    53: Stat.W,
    54: Stat.L,
    57: Stat.SV,
    99: Stat.STARTER,
}

LOGGER = logging.getLogger("espn.stats_translator")

def stat_id_to_stat(stat_id):
    return espn_stat_to_stat[stat_id]


def create_stats(espn_stats_dict):
    transformed_stats = dict()
    for stat_id_str in espn_stats_dict.keys():
        stat_id = int(stat_id_str)
        stat = espn_stat_to_stat.get(stat_id)
        if stat:
            stat_val = float(espn_stats_dict.get(stat_id_str))
            transformed_stats[stat] = stat_val

    return Stats(transformed_stats)


def is_starting(roster_entry):
    """
    Checks if the given roster entry is a starting one
    :param roster_entry:
    :return:
    """
    slot_id = roster_entry["lineupSlotId"]
    slot = BaseballSlot.espn_slot_to_slot(slot_id)
    return slot not in {BaseballSlot.BENCH, BaseballSlot.INJURED}


def cumulative_stats_from_roster_entries(entries, scoring_period_id):
    """
    Takes a list of roster entries and reconstitutes the cumulative stats produced by that roster.
    :param list entries: the entries produced
    :param int scoring_period_id: the scoring period for which stats are being accumulated
    :return Stats: the sum total of stats produced by starters on that roster
    """
    total_stats = Stats({})
    for e in filter(is_starting, entries):
        entry_stats_list = e["playerPoolEntry"]["player"]["stats"]
        stats_dict = next(filter(lambda d: d['scoringPeriodId'] == scoring_period_id, entry_stats_list), None)
        if stats_dict is None:
            name = e["playerPoolEntry"]["player"]["fullName"]
            LOGGER.warning(f"{name} has no stats matching scoring period {scoring_period_id} found in entry {e}")
            continue
        stats = create_stats(stats_dict["stats"])
        total_stats += stats
    return total_stats
