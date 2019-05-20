from enum import Enum


class Stat(Enum):
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
            Stat.AB,
            Stat.H,
            Stat.AVG,
            Stat.HR,
            Stat.BB,
            Stat.PA,
            Stat.OBP,
            Stat.R,
            Stat.RBI,
            Stat.SB,
        }


class Stats:
    stat_functions = {
        Stat.AVG: lambda s: s.average(),
        Stat.OBP: lambda s: s.obp(),
        Stat.WHIP: lambda s: s.whip(),
        Stat.ERA: lambda s: s.era(),
    }

    sum_stats = {
        Stat.AB,
        Stat.H,
        Stat.HR,
        Stat.BB,
        Stat.PA,
        Stat.R,
        Stat.RBI,
        Stat.SB,
        Stat.OUTS,
        Stat.BATTERS,
        Stat.PITCHES,
        Stat.P_H,
        Stat.P_BB,
        Stat.HBP,
        Stat.P_R,
        Stat.ER,
        Stat.P_HR,
        Stat.K,
        Stat.W,
        Stat.L,
        Stat.SV
    }

    @staticmethod
    def pitcher_stats(wins, innings, batters, hits, homers, walks, strikeouts):
        # component era calculation from Bill James https://en.wikipedia.org/wiki/Component_ERA
        # pitcher_total_bases = 0.89 * (1.255 * (hits - homers) + 4 * homers) + 0.475 * walks
        # unadjusted_comp_era = 9 * ((hits + walks) * pitcher_total_bases) / (batters * innings)
        # component_era = unadjusted_comp_era - 0.56
        # if component_era < 2.24:
        #     component_era = unadjusted_comp_era * 0.75
        component_era = 3.00 + (13 * homers + 3 * walks - 2 * strikeouts) / innings

        stats_dict = {
            Stat.OUTS: innings * 3,
            Stat.P_H: hits,
            Stat.P_BB: walks,
            Stat.WHIP: (walks + hits) / innings,
            Stat.ERA: component_era,
            Stat.P_HR: homers,
            Stat.K: strikeouts,
            Stat.W: wins,
        }
        return Stats(stats_dict)

    @staticmethod
    def hitter_stats(pa, h, hr, r, rbi, sb, bb):
        ab = pa - bb
        stats_dict = {
            Stat.AB: ab,
            Stat.H: h,
            Stat.AVG: h / ab,
            Stat.HR: hr,
            Stat.BB: bb,
            Stat.PA: pa,
            Stat.OBP: (h + bb) / pa,
            Stat.R: r,
            Stat.RBI: rbi,
            Stat.SB: sb,
        }
        return Stats(stats_dict)

    def __init__(self, stat_dict):
        """
        Accepts a dictionary from Stat to float
        :param stat_dict: mapping of a stat to its float value
        """
        self.stat_dict = stat_dict

    def __add__(self, other):
        combined = dict()
        my_keys = set(self.stat_dict.keys()).intersection(Stats.sum_stats)
        for k in my_keys:
            combined[k] = self.stat_dict.get(k) + other.stat_dict.get(k, 0.0)

        other_keys = set(other.stat_dict.keys() - my_keys).intersection(Stats.sum_stats)
        for k in other_keys:
            combined[k] = other.stat_dict[k]
        return Stats(combined)

    def __str__(self):
        print_pairs = list()
        for stat in Stats.sum_stats:
            val = self.value_for_stat(stat)
            if val:
                print_pairs.append((stat, val))
        print_pairs.append((Stat.AVG, self.average()))
        print_pairs.append((Stat.OBP, self.obp()))
        print_pairs.append((Stat.ERA, self.era()))
        print_pairs.append((Stat.WHIP, self.whip()))
        s = ""
        for (name, stat) in print_pairs:
            if stat:
                s += "{}\t{}\n".format(name, stat)
        return s

    def average(self):
        return round(self.stat_dict.get(Stat.AVG, self.stat_dict.get(Stat.H) / self.stat_dict.get(Stat.AB)), 3)

    # note - adjust calculation to include not just walks + hits but also HBP, etc.
    def obp(self):
        exact_obp = self.stat_dict.get(Stat.OBP)
        if exact_obp is None:
            reached_base = self.stat_dict[Stat.H] + self.stat_dict[Stat.BB]
            exact_obp = reached_base / self.stat_dict[Stat.PA]
        return round(exact_obp, 3)

    def runs(self):
        return self.stat_dict.get(Stat.R, 0)

    def home_runs(self):
        return self.stat_dict.get(Stat.HR, 0)

    def steals(self):
        return self.stat_dict.get(Stat.SB, 0)

    def strikeouts(self):
        return self.stat_dict.get(Stat.K, 0)

    def wins(self):
        return self.stat_dict.get(Stat.W, 0)

    def saves(self):
        return self.stat_dict.get(Stat.SV, 0)

    def era(self):
        total = self.stat_dict.get(Stat.ERA)
        if total:
            return round(total, 3)

        earned_runs = self.stat_dict.get(Stat.ER, 0)
        outs = self.stat_dict.get(Stat.OUTS, 1.0)

        return round(earned_runs * 27.0 / outs, 3)

    def whip(self):
        total = self.stat_dict.get(Stat.WHIP)
        if total:
            return round(total, 3)

        hits = self.stat_dict.get(Stat.P_H, 0)
        walks = self.stat_dict.get(Stat.P_BB, 0)
        outs = self.stat_dict.get(Stat.OUTS, 1.0)

        return round((walks + hits) / outs * 3.0, 3)

    def unrounded_value_for_stat(self, stat):
        if stat in Stats.sum_stats:
            return self.stat_dict.get(stat)
        elif stat in Stats.stat_functions:
            return Stats.stat_functions.get(stat)(self)

    def value_for_stat(self, stat):
        val = self.unrounded_value_for_stat(stat)
        if val is not None:
            return round(val, 2)
        else:
            return val
