import logging

from espn.baseball.baseball_position import BaseballPosition
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_stat import BaseballStat
from espn.espn_api import EspnApi
from espn.sessions.espn_session_provider import EspnSessionProvider


# http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>
# - members[i].displayName == "zcwalsh"
#     -> id == ownerId
# - scoringPeriodId
#
#
#
# url that is hit on page load:
# "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>
# ?view=mMatchupScore" \
#               "&view=mLiveScoring"


LOGGER = logging.getLogger("espn.baseball.api")


class BaseballApi(EspnApi):
    def __init__(self, session_provider, league_id, team_id):
        """
        Provides programmatic access to ESPN's fantasy baseball API for the given league and team,
        making calls to the underlying ESPN object
        :param EspnApi espn: authenticated access to ESPN
        :param int league_id: the league to access
        :param int team_id: the team to access
        """
        super().__init__(session_provider, league_id, team_id)

    def _api_url_segment(self):
        return "flb"

    # { team_id: Lineup, ...}

    def is_probable_pitcher(self, player_id):
        """
        Checks if the Player with the given player id is a probable starting pitcher today.
        :param int player_id: the ESPN id of the player to check
        :return bool: whether or not the player is pitching today
        """
        player_resp = self._player_request(player_id)
        name = player_resp["fullName"]
        LOGGER.debug(f"checking start status for {name}")
        stats = player_resp["stats"]
        starter_split = next(
            filter(lambda s: s["statSplitTypeId"] == 5, stats), {}
        ).get("stats", {})
        is_starter = starter_split.get("99", None) == 1.0
        LOGGER.debug(f"starting? {is_starter}")
        return is_starter

    def _slot_enum(self):
        return BaseballSlot

    def _stat_enum(self):
        return BaseballStat

    def _position(self, position_id):
        return BaseballPosition(position_id)

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
            return BaseballApi(
                EspnSessionProvider(self.__username, self.__password),
                self.__league_id,
                self.__team_id,
            )
