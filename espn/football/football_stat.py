from enum import Enum


class FootballStat(Enum):
    YDS_PASS = "PASS YDS"
    TD_PASS = "PASS TD"
    TWOPT_PASS = "PASS 2PT"
    INT_PASS = "INT"

    YDS_RUSH = "RUSH YDS"
    TD_RUSH = "RUSH TD"
    TWOPT_RUSH = "RUSH 2PT"

    REC = "REC"
    YDS_REC = "REC YDS"
    TD_REC = "REC TD"
    TWOPT_REC = "REC 2PT"

    FUML = "FUML"

    PT_0 = "PT 0"
    PT_6 = "PT 1-6"
    PT_13 = "PT 7-13"
    PT_17 = "PT 14-17"
    PT_34 = "PT 28-34"
    PT_45 = "PT 35-45"

    YA_199 = "YA 100-199"
    YA_299 = "YA 200-299"
    YA_399 = "YA 350-399"
    YA_449 = "YA 400-449"
    YA_499 = "YA 450-499"
    YA_549 = "YA 500-549"
    YA_550 = "YA >550"

    BLK_TD = "BLOCK TD"
    INT_DEF = "INT DEF"
    FUMR = "FUM REC"
    BLK = "BLOCK"
    SFT = 'SAFETY'
    SK = "SACK"

    KR_TD = "KR TD"
    PR_TD = "PR TD"
    FR_TD = "FR TD"
    INT_TD = "INT TD"


    @staticmethod
    def sum_stats():
        return {s for s in FootballStat}

    def num_rounding_digits(self):
        return 0

    @staticmethod
    def espn_stat_to_stat(stat_id):
        return {
            3: FootballStat.YDS_PASS,
            4: FootballStat.TD_PASS,
            19: FootballStat.TWOPT_PASS,
            24: FootballStat.YDS_RUSH,
            25: FootballStat.TD_RUSH,
            26: FootballStat.TWOPT_RUSH,
            42: FootballStat.YDS_REC,
            43: FootballStat.TD_REC,
            44: FootballStat.TWOPT_REC,
            53: FootballStat.REC,
            72: FootballStat.FUML,
            89: FootballStat.PT_0,
            90: FootballStat.PT_6,
            91: FootballStat.PT_13,
            92: FootballStat.PT_17,
            93: FootballStat.BLK_TD,
            95: FootballStat.INT_DEF,
            96: FootballStat.FUMR,
            97: FootballStat.BLK,
            98: FootballStat.SFT,
            99: FootballStat.SK,
            101: FootballStat.KR_TD,
            102: FootballStat.PR_TD,
            103: FootballStat.FR_TD,
            104: FootballStat.INT_TD,
            123: FootballStat.PT_34,
            124: FootballStat.PT_45,
            129: FootballStat.YA_199,
            130: FootballStat.YA_299,
            132: FootballStat.YA_399,
            133: FootballStat.YA_449,
            134: FootballStat.YA_499,
            135: FootballStat.YA_549,
            136: FootballStat.YA_550,
        }.get(stat_id)
