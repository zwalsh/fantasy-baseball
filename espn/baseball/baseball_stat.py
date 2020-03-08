from enum import Enum


class BaseballStat(Enum):
    AB = "AB"
    H = "H"
    AVG = "AVG"
    HR = "HR"
    BB = "BB"
    PA = "PA"
    OBP = "OBP"
    R = "R"
    RBI = "RBI"
    SB = "SB"
    OUTS = "OUTS"
    BATTERS = "BATTERS"
    PITCHES = "PITCHES"
    P_H = "P_H"
    P_BB = "P_BB"
    WHIP = "WHIP"
    HBP = "HBP"
    P_R = "P_R"
    ER = "ER"
    P_HR = "P_HR"
    ERA = "ERA"
    K = "K"
    W = "W"
    L = "L"
    SV = "SV"
    STARTER = "STARTER"

    def is_hitting_stat(self):
        return self in {
            BaseballStat.AB,
            BaseballStat.H,
            BaseballStat.AVG,
            BaseballStat.HR,
            BaseballStat.BB,
            BaseballStat.PA,
            BaseballStat.OBP,
            BaseballStat.R,
            BaseballStat.RBI,
            BaseballStat.SB,
        }

    def num_rounding_digits(self):
        if self in {BaseballStat.AVG, BaseballStat.OBP}:
            return 3
        else:
            return 2

    @staticmethod
    def sum_stats():
        return sum_stats_set

    @staticmethod
    def espn_stat_to_stat(stat_id):
        return {
            0: BaseballStat.AB,
            1: BaseballStat.H,
            2: BaseballStat.AVG,
            5: BaseballStat.HR,
            10: BaseballStat.BB,
            16: BaseballStat.PA,
            17: BaseballStat.OBP,
            20: BaseballStat.R,
            21: BaseballStat.RBI,
            23: BaseballStat.SB,
            34: BaseballStat.OUTS,  # can derive IP
            35: BaseballStat.BATTERS,
            36: BaseballStat.PITCHES,
            37: BaseballStat.P_H,
            39: BaseballStat.P_BB,
            41: BaseballStat.WHIP,
            42: BaseballStat.HBP,
            44: BaseballStat.P_R,
            45: BaseballStat.ER,
            46: BaseballStat.P_HR,
            47: BaseballStat.ERA,
            48: BaseballStat.K,
            53: BaseballStat.W,
            54: BaseballStat.L,
            57: BaseballStat.SV,
            99: BaseballStat.STARTER,
        }.get(stat_id)


sum_stats_set = {
    BaseballStat.AB,
    BaseballStat.H,
    BaseballStat.HR,
    BaseballStat.BB,
    BaseballStat.PA,
    BaseballStat.R,
    BaseballStat.RBI,
    BaseballStat.SB,
    BaseballStat.OUTS,
    BaseballStat.BATTERS,
    BaseballStat.PITCHES,
    BaseballStat.P_H,
    BaseballStat.P_BB,
    BaseballStat.HBP,
    BaseballStat.P_R,
    BaseballStat.ER,
    BaseballStat.P_HR,
    BaseballStat.K,
    BaseballStat.W,
    BaseballStat.L,
    BaseballStat.SV
}