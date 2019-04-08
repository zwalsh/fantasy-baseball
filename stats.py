
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
        41: "WHIP",
        42: "HBP",
        44: "R",
        45: "ER",
        46: "HR",
        47: "ERA",
        48: "K",
        53: "W",
        54: "L",
        99: "STARTER",  # maybe?
    })

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