import logging

from espn.espn_api import EspnApi
from espn.football.football_position import FootballPosition
from espn.football.football_slot import FootballSlot
from espn.football.football_stat import FootballStat
from espn.sessions.espn_session_provider import EspnSessionProvider

LOGGER = logging.getLogger("espn.football.api")


class FootballApi(EspnApi):
    def _slot_enum(self):
        return FootballSlot

    def _stat_enum(self):
        return FootballStat

    def _position(self, position_id):
        return FootballPosition(position_id)

    def _api_url_segment(self):
        return "ffl"

    class Builder:
        def __init__(self):
            """
            Builds a BaseballApi instance, creating the EspnSessionProvider objects under the hood
            """
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

        def build(self):
            return FootballApi(
                EspnSessionProvider(self.__username, self.__password),
                self.__league_id,
                self.__team_id,
            )
