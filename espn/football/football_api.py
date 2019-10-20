from espn.espn_api import EspnApi
from espn.sessions.espn_session_provider import EspnSessionProvider


class FootballApi(EspnApi):

    @staticmethod
    def possible_slots():
        return []  # todo fill in with all slots

    @staticmethod
    def player_list_to_lineup(players):
        return None

    def api_url_segment(self):
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
            return FootballApi(EspnSessionProvider(self.__username, self.__password), self.__league_id,
                               self.__team_id)
