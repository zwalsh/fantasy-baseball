from espn.baseball.baseball_stat import BaseballStat


class Stats:
    stat_functions = {  # todo should figure out a way to pull these out into the enum
        BaseballStat.AVG: lambda s: s.average(),
        BaseballStat.OBP: lambda s: s.obp(),
        BaseballStat.WHIP: lambda s: s.whip(),
        BaseballStat.ERA: lambda s: s.era(),
    }

    def __init__(self, stat_dict, stat_enum):
        """
        Accepts a dictionary from Stat to float
        :param stat_dict: mapping of a stat to its float value
        :param stat_enum: the enum of Stats that can be in this Stat object
        """
        self.stat_dict = stat_dict
        self.stat_enum = stat_enum

    def __add__(self, other):
        combined = dict()
        my_keys = set(self.stat_dict.keys()).intersection(self.stat_enum.sum_stats())
        for k in my_keys:
            combined[k] = self.stat_dict.get(k) + other.stat_dict.get(k, 0.0)

        other_keys = set(other.stat_dict.keys() - my_keys).intersection(self.stat_enum.sum_stats())
        for k in other_keys:
            combined[k] = other.stat_dict[k]
        return Stats(combined, self.stat_enum)

    def __str__(self):
        print_pairs = list()
        for stat in self.stat_enum.sum_stats():
            val = self.value_for_stat(stat)
            if val:
                print_pairs.append((stat, val))
        # print_pairs.append((BaseballStat.AVG, self.average()))
        # print_pairs.append((BaseballStat.OBP, self.obp()))
        # print_pairs.append((BaseballStat.ERA, self.era()))
        # print_pairs.append((BaseballStat.WHIP, self.whip()))
        s = ""
        for (name, stat) in print_pairs:
            if stat:
                s += "{}\t{}\n".format(name, stat)
        return s

    def average(self):
        return round(self.stat_dict.get(BaseballStat.AVG, self.stat_dict.get(BaseballStat.H) / self.stat_dict.get(
            BaseballStat.AB)), 3)

    # note - adjust calculation to include not just walks + hits but also HBP, etc.
    def obp(self):
        exact_obp = self.stat_dict.get(BaseballStat.OBP)
        if exact_obp is None:
            reached_base = self.stat_dict[BaseballStat.H] + self.stat_dict[BaseballStat.BB]
            exact_obp = reached_base / self.stat_dict[BaseballStat.PA]
        return round(exact_obp, 3)

    def runs(self):
        return self.stat_dict.get(BaseballStat.R, 0)

    def home_runs(self):
        return self.stat_dict.get(BaseballStat.HR, 0)

    def steals(self):
        return self.stat_dict.get(BaseballStat.SB, 0)

    def strikeouts(self):
        return self.stat_dict.get(BaseballStat.K, 0)

    def wins(self):
        return self.stat_dict.get(BaseballStat.W, 0)

    def saves(self):
        return self.stat_dict.get(BaseballStat.SV, 0)

    def era(self):
        total = self.stat_dict.get(BaseballStat.ERA)
        if total:
            return round(total, 3)

        earned_runs = self.stat_dict.get(BaseballStat.ER, 0)
        outs = self.stat_dict.get(BaseballStat.OUTS, 1.0)

        return round(earned_runs * 27.0 / outs, 3)

    def whip(self):
        total = self.stat_dict.get(BaseballStat.WHIP)
        if total:
            return round(total, 3)

        hits = self.stat_dict.get(BaseballStat.P_H, 0)
        walks = self.stat_dict.get(BaseballStat.P_BB, 0)
        outs = self.stat_dict.get(BaseballStat.OUTS, 1.0)

        return round((walks + hits) / outs * 3.0, 3)

    def unrounded_value_for_stat(self, stat):
        if stat in self.stat_enum.sum_stats():
            return self.stat_dict.get(stat)
        elif stat in Stats.stat_functions:
            return Stats.stat_functions.get(stat)(self)

    def value_for_stat(self, stat):
        val = self.unrounded_value_for_stat(stat)
        if val is not None:
            return round(val, stat.num_rounding_digits())
        else:
            return val
