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
