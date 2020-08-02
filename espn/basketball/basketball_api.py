from espn.basketball.basketball_position import BasketballPosition
from espn.basketball.basketball_slot import BasketballSlot
from espn.basketball.basketball_stat import BasketballStat
from espn.espn_api import EspnApi

from espn.sessions.espn_session_provider import EspnSessionProvider


class BasketballApi(EspnApi):
    def slot_enum(self):
        return BasketballSlot

    def stat_enum(self):
        return BasketballStat

    def api_url_segment(self):
        return "fba"

    def position(self, position_id):
        return BasketballPosition(position_id)

    class Builder:
        def __init__(self):
            """
            Builds a BaseballApi instance, creating the EspnSessionProvider objects under the hood
            """
            self.__year = 2020
            self.__username = ""
            self.__password = ""
            self.__league_id = 0
            self.__team_id = 0

        def username(self, username):
            self.__username = username
            return self

        def password(self, password):
            self.__password = password
            return self

        def league_id(self, league_id):
            self.__league_id = league_id
            return self

        def team_id(self, team_id):
            self.__team_id = team_id
            return self

        def year(self, year):
            self.__year = year
            return self

        def build(self):
            return BasketballApi(
                EspnSessionProvider(self.__username, self.__password),
                self.__league_id,
                self.__team_id,
                self.__year,
            )
