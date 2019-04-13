
class Stats:
    stat_names = dict({
        0: "AB",
        1: "H",
        2: "AVG",
        5: "HR",
        10: "BB",
        16: "PA",
        17: "OBP",
        20: "R",
        21: "RBI",
        23: "SB",
        34: "OUTS",  # can derive IP
        35: "BATTERS FACED",
        36: "PITCHES",
        37: "H",
        39: "BB",
        41: "WHIP",
        42: "HBP",
        44: "R",
        45: "ER",
        46: "HR",
        47: "ERA",
        48: "K",
        53: "W",
        54: "L",
        57: "SV",
        99: "STARTER",  # maybe?
    })

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
            34: innings * 3,
            37: hits,
            39: walks,
            41: (walks + hits) / innings,
            45: component_era,
            46: homers,
            48: strikeouts,
            53: wins,
        }
        return Stats(stats_dict)

    @staticmethod
    def hitter_stats(pa, h, hr, r, rbi, sb, bb):
        ab = pa - bb
        stats_dict = {
            0: ab,
            1: h,
            2: h / ab,
            5: hr,
            10: bb,
            16: pa,
            17: (h + bb) / pa,
            20: r,
            21: rbi,
            23: sb,
        }
        return Stats(stats_dict)

    # self.stat_dict: { id: val, ...} where id is an int, val is an
    def __init__(self, stat_dict):
        self.stat_dict = dict()
        for k, v in stat_dict.items():
            self.stat_dict[int(k)] = float(v)

    def __str__(self):
        s = ""
        for k, v in self.stat_dict.items():
            s += "{}\t{}\n".format(self.stat_names.get(k, k), v)
        return s

    def average(self):
        return round(self.stat_dict.get(2, self.stat_dict.get(1) / self.stat_dict.get(0)), 3)

    # note - adjust calculation to include not just walks + hits but also HBP, etc.
    def obp(self):
        return round(self.stat_dict.get(17, (self.stat_dict.get(1) + self.stat_dict.get(10)) / self.stat_dict.get(16)), 3)

    def runs(self):
        return self.stat_dict.get(20, 0)

    def home_runs(self):
        return self.stat_dict.get(5, 0)

    def steals(self):
        return self.stat_dict.get(23, 0)

    def strikeouts(self):
        return self.stat_dict.get(48, 0)

    def wins(self):
        return self.stat_dict.get(53, 0)

    def saves(self):
        return self.stat_dict.get(57, 0)

    def era(self):
        total = self.stat_dict.get(47)
        if total:
            return round(total, 3)

        earned_runs = self.stat_dict.get(45, 0)
        outs = self.stat_dict.get(34, 1.0)

        return round(earned_runs * 27.0 / outs, 3)

    def whip(self):
        total = self.stat_dict.get(41)
        if total:
            return round(total, 3)

        hits = self.stat_dict.get(37, 0)
        walks = self.stat_dict.get(39, 0)
        outs = self.stat_dict.get(34, 1.0)

        return round((walks + hits) / outs * 3.0, 3)
