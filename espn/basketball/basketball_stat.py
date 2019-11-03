from enum import Enum


class BasketballStat(Enum):
    MINUTES = "MIN"
    FGM = "FGM"
    FGA = "FGA"
    FGPCT = "FG%"
    FTM = "FTM"
    FTA = "FTA"
    FTPCT = "FT%"
    THREES = "3PT"
    REBOUNDS = "REB"
    ASSISTS = "AST"
    STEALS = "STL"
    BLOCKS = "BLK"
    POINTS = "PTS"

    @staticmethod
    def sum_stats():
        return {
            BasketballStat.MINUTES,
            BasketballStat.FGM,
            BasketballStat.FGA,
            BasketballStat.FTM,
            BasketballStat.FTA,
            BasketballStat.THREES,
            BasketballStat.REBOUNDS,
            BasketballStat.ASSISTS,
            BasketballStat.STEALS,
            BasketballStat.BLOCKS,
            BasketballStat.POINTS,
        }

    def num_rounding_digits(self):
        return 0 if self in BasketballStat.sum_stats() else 3

    @staticmethod
    def espn_stat_to_stat(stat_id):
        return {
            0: BasketballStat.POINTS,
            1: BasketballStat.BLOCKS,
            2: BasketballStat.STEALS,
            3: BasketballStat.ASSISTS,
            6: BasketballStat.REBOUNDS,
            13: BasketballStat.FGM,
            14: BasketballStat.FGA,
            15: BasketballStat.FTM,
            16: BasketballStat.FTA,
            17: BasketballStat.THREES,
            19: BasketballStat.FGPCT,
            20: BasketballStat.FTPCT,
            40: BasketballStat.MINUTES,
        }.get(stat_id)
