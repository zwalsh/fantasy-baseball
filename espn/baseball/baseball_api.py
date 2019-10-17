import json
import logging

from espn.espn_api import EspnApi
from espn.player_translator import roster_entry_to_player, lineup_slot_counts_to_lineup_settings, \
    slot_to_slot_id
from espn.sessions.espn_session_provider import EspnSessionProvider
from espn.stats_translator import stat_id_to_stat, create_stats, cumulative_stats_from_roster_entries
from league import League
from lineup import Lineup
from scoring_setting import ScoringSetting
from team import Team

"""
http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>
- members[i].displayName == "zcwalsh" 
    -> id == ownerId
- scoringPeriodId



url that is hit on page load:
"http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>?view=mMatchupScore" \
              "&view=mLiveScoring"

"""
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

    def api_url_segment(self):
        return "flb"

    def member_id(self):
        return "{84C1CD19-5E2C-4D5D-81CD-195E2C4D5D75}"  # todo fetch when logging in, persist?

    # { team_id: Lineup, ...}

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info['settings']['scoringSettings']['scoringItems']
        return list(map(BaseballApi.json_to_scoring_setting, scoring_items))

    def scoring_period_stats(self, scoring_period):
        teams = self.scoring_period_info(scoring_period).json()["teams"]
        team_to_stats = dict()
        for t in teams:
            stats = cumulative_stats_from_roster_entries(t["roster"]["entries"], scoring_period)
            team_to_stats[t['id']] = stats
        return team_to_stats

    def year_stats(self):
        """
        Returns a dictionary of all stats for all teams on the year.
        Maps team id to Stats object
        :return: mapping of team id to Stats for the year
        """
        teams = self.all_info().json()['teams']
        team_to_stats = dict()
        for t in teams:
            stats = create_stats(t['valuesByStat'])
            team_to_stats[t['id']] = stats
        return team_to_stats

    def lineup_settings(self):
        url = self.lineup_settings_url()
        settings = self.espn_get(url).json()['settings']['rosterSettings']['lineupSlotCounts']
        return lineup_slot_counts_to_lineup_settings(settings)

    def set_lineup_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}/transactions/".format(self.league_id)

    def league(self):
        """
        Fetches the whole league, including each team's current lineup and yearly stats
        :return: League - the whole league
        """
        stats = self.year_stats()
        lineups = self.all_lineups()
        teams = []
        for team_id in stats.keys():
            t = Team(team_id, lineups.get(team_id), stats.get(team_id))
            teams.append(t)
        return League(teams)

    def player_url(self):
        return f"http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               f"{self.league_id}?view=kona_playercard"

    def player_request(self, player_id):
        """
        Makes the request to ESPN for the player with the player id and returns the raw response (parsed from JSON)
        :param int player_id: the id of the player to make the request about
        :return dict: the parsed response from ESPN
        """
        filter_header = {"players": {"filterIds": {"value": [player_id]}}}
        resp = self.espn_get(self.player_url(), {"X-Fantasy-Filter": json.dumps(filter_header)}, check_cache=False)
        return resp.json()["players"][0]["player"]

    def player(self, player_id):
        """
        Given the ESPN id of a Player, this will return the Player object associated with that Player,
        or None if no such player exists.
        :param int player_id: the id in the ESPN system of the player to be requested
        :return Player: the associated Player object (or None)
        """
        return roster_entry_to_player(self.player_request(player_id))

    def is_probable_pitcher(self, player_id):
        """
        Checks if the Player with the given player id is a probable starting pitcher today.
        :param int player_id: the ESPN id of the player to check
        :return bool: whether or not the player is pitching today
        """
        player_resp = self.player_request(player_id)
        name = player_resp["fullName"]
        LOGGER.debug(f"checking start status for {name}")
        stats = player_resp["stats"]
        starter_split = next(filter(lambda s: s["statSplitTypeId"] == 5, stats), {}).get("stats", {})
        is_starter = starter_split.get("99", None) == 1.0
        LOGGER.debug(f"starting? {is_starter}")
        return is_starter

    """
    {"bidAmount":0,
    "executionType":"EXECUTE",
    "id":"e2d156d6-94c3-4fa0-9cac-4aaacbce1444",
    "isActingAsTeamOwner":false,
    "isLeagueManager":false,
    "isPending":false,
    "items":[{"fromLineupSlotId":-1,
                "fromTeamId":0,
                "isKeeper":false,
                "overallPickNumber":0,
                "playerId":35983,
                "toLineupSlotId":-1,
                "toTeamId":7,
                "type":"ADD"},
                {"fromLineupSlotId":-1,
                "fromTeamId":7,
                "isKeeper":false,
                "overallPickNumber":0,
                "playerId":32620,
                "toLineupSlotId":-1,
                "toTeamId":0,
                "type":"DROP"}],
    "memberId":"{84C1CD19-5E2C-4D5D-81CD-195E2C4D5D75}",
    "proposedDate":1553703820851,
    "rating":0,
    "scoringPeriodId":8,
    "skipTransactionCounters":false,
    "status":"EXECUTED",
    "subOrder":0,
    "teamId":7,
    "type":"FREEAGENT"}
    """

    def set_lineup_payload(self, transitions):
        payload = {
            "isLeagueManager": False,
            "teamId": self.team_id,
            "type": "ROSTER",
            "memberId": self.member_id(),
            "scoringPeriodId": self.scoring_period(),
            "executionType": "EXECUTE",
            "items": list(map(BaseballApi.transition_to_item, transitions))
        }
        return payload

    # this will not work at the moment - need to translate LineupSlots back to espn
    # lineup ids
    def set_lineup(self, lineup):
        cur_lineup = self.lineup(self.team_id)
        transitions = cur_lineup.transitions(lineup)
        return self.execute_transitions(transitions)

    def execute_transitions(self, transitions):
        """
        Executes the given transitions, moving players as specified.
        :param list transitions: the list of LineupTransitions to execute
        :return: the response returned from the POST request
        """
        url = self.set_lineup_url()
        for t in transitions:
            LOGGER.info(f"executing transition {t}")
        payload = self.set_lineup_payload(transitions)
        return self.espn_post(url, payload)

    @staticmethod
    def player_list_to_lineup(players):
        player_dict = dict()
        for (player, slot) in players:
            cur_list = player_dict.get(slot, list())
            cur_list.append(player)
            player_dict[slot] = cur_list
        return Lineup(player_dict)

    @staticmethod
    def json_to_scoring_setting(item):
        stat = stat_id_to_stat(item['statId'])
        return ScoringSetting(stat, item['isReverseItem'])

    @staticmethod
    def transition_to_item(transition):
        """
        Creates the ESPN API item for a transition out of a LineupTransition object.
        :param LineupTransition transition:
        :return:
        """
        return {
            "playerId": transition.player.espn_id,
            "type": "LINEUP",
            "fromLineupSlotId": slot_to_slot_id(transition.from_slot),
            "toLineupSlotId": slot_to_slot_id(transition.to_slot)
        }

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
            return BaseballApi(EspnSessionProvider(self.__username, self.__password), self.__league_id,
                               self.__team_id)
