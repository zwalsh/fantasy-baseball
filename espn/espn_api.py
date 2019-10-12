import json
import logging
import time

import requests

from espn.player_translator import roster_entry_to_player, espn_slot_to_slot, lineup_slot_counts_to_lineup_settings, \
    slot_to_slot_id
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
LOGGER = logging.getLogger("espn.api")


class EspnApiException(Exception):
    """
    Exception to throw when a request to the ESPN API failed
    """
    pass


class EspnApi:
    LOGIN_URL = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/guest/login?langPref=en-US"

    def __init__(self, session_provider, league_id, team_id):
        """
        Programmatic access to ESPN's (undocumented) API, caching requests that do not need refreshing,
        and automatically fetching a token for the user/password combination.

        :param EspnSessionProvider session_provider: using a username and password, provides and stores session tokens
        :param int league_id: the league to access
        :param int team_id: the team to access
        """
        self.session_provider = session_provider
        self.league_id = league_id
        self.team_id = team_id
        self.cache = dict()

    def espn_request(self, method, url, payload, headers=None, check_cache=True, retries=1):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)
        LOGGER.info(f"making {method} request to {url} in league {self.league_id} with headers {headers}")
        start_time = time.time()
        k = self.session_provider.get_session()
        cookies = {"espn_s2": k}
        if method == 'GET':
            r = requests.get(url, headers=headers or {}, cookies=cookies)
        if method == 'POST':
            r = requests.post(url, headers=headers or {}, cookies=cookies, json=payload)
        if r.status_code == 401:
            LOGGER.warning("request denied, logging in again.")
            self.session_provider.refresh_session()
            return self.espn_request(method=method, url=url, payload=payload, headers=headers, check_cache=check_cache)
        if not r.ok:
            LOGGER.error(f"received {r.status_code} {r.reason}: {r.text} in {start_time - time.time():.3f} seconds")
            if retries > 0:
                LOGGER.info(f"retrying request")
                return self.espn_request(method=method, url=url, payload=payload, headers=headers,
                                         check_cache=check_cache, retries=retries - 1)
            else:
                raise EspnApiException(url)
        if r.text is None or r.text == "":
            LOGGER.error(f"the response was blank after {start_time - time.time():.3f} seconds")
            if retries > 0:
                return self.espn_request(method=method, url=url, payload=payload, headers=headers,
                                         check_cache=check_cache, retries=retries - 1)
            else:
                raise EspnApiException(url)
        else:
            end_time = time.time()
            LOGGER.info("finished after %(time).3fs", {"time": end_time - start_time})
        self.cache[url] = r
        return r

    def espn_get(self, url, headers=None, check_cache=True):
        return self.espn_request(method='GET', url=url, payload={}, headers=headers, check_cache=check_cache)

    def espn_post(self, url, payload, headers=None):
        return self.espn_request(method='POST', url=url, payload=payload, headers=headers)

    def scoring_period(self):
        url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/{}".format(self.league_id)
        return self.espn_get(url).json()['scoringPeriodId']

    def member_id(self):
        return "{84C1CD19-5E2C-4D5D-81CD-195E2C4D5D75}"  # todo fetch when logging in, persist?

    def lineup_url(self):
        scoring_period_id = self.scoring_period()
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?forTeamId={}" \
               "&scoringPeriodId={}" \
               "&view=mRoster".format(self.league_id, self.team_id, scoring_period_id)

    def lineup(self, team_id=None):
        """
        Returns the current lineup of the team with the given team id
        :param int team_id: the id of the team in this league to get the lineup for
        :return Lineup: Lineup the lineup of the given team
        """
        return self.all_lineups()[team_id or self.team_id]

    def scoring_period_info_url(self, scoring_period):
        return f"http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               f"{self.league_id}?scoringPeriodId={scoring_period}&view=mRoster"

    def all_lineups_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?view=mRoster" \
               "&scoringPeriodId={}".format(self.league_id, self.scoring_period())

    # { team_id: Lineup, ...}
    def all_lineups(self):
        resp = self.espn_get(self.all_lineups_url()).json()
        teams = resp['teams']
        lineup_dict = dict()
        for team in teams:
            roster = team['roster']['entries']
            players = list(map(lambda e: (roster_entry_to_player(e["playerPoolEntry"]["player"]),
                                          espn_slot_to_slot.get(e['lineupSlotId'])), roster))
            lineup = EspnApi.player_list_to_lineup(players)
            lineup_dict[team['id']] = lineup
        return lineup_dict

    def all_info_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions" \
               "&view=mPositionalRatings&view=mSettings&view=mTeam".format(self.league_id)

    def all_info(self):
        return self.espn_get(self.all_info_url())

    def scoring_period_info(self, scoring_period):
        return self.espn_get(self.scoring_period_info_url(scoring_period))

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info['settings']['scoringSettings']['scoringItems']
        return list(map(EspnApi.json_to_scoring_setting, scoring_items))

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

    def lineup_settings_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}?view=mSettings".format(self.league_id)

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

    def team_name(self, team_id=None):
        """
        Fetches the name of the team with the given id, or the id of the team tied to this object
        if none is given. The name is the concatenation of the team's "location" and the team's
        "nickname", per ESPN.
        :param int team_id: the id of the team whose name is to be fetched
        :return str: the name fetched from ESPN for the given team
        """
        team_id = team_id or self.team_id
        teams = self.all_info().json()['teams']
        team = next(filter(lambda t: t['id'] == team_id, teams))
        return f"{team['location']} {team['nickname']}"

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
            "items": list(map(EspnApi.transition_to_item, transitions))
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
