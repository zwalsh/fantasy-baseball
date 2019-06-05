import json
import logging
import time
from pathlib import Path

import requests

from espn.player_translator import roster_entry_to_player, espn_slot_to_slot, lineup_slot_counts_to_lineup_settings, \
    slot_to_slot_id
from espn.stats_translator import stat_id_to_stat, create_stats
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


class LoginException(Exception):
    """
    Exception to throw when Login to ESPN was unsuccessful
    """
    pass


class EspnApi:
    LOGIN_URL = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/guest/login?langPref=en-US"

    def __init__(self, username, password, league_id, team_id):
        self.username = username
        self.password = password
        self.league_id = league_id
        self.team_id = team_id
        self.cache = dict()

    def session_file_name(self):
        return "espn_s2_{u}.txt".format(u=self.username)

    @staticmethod
    def api_key():
        key_url = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/api-key?langPref=en-US"
        resp = requests.post(key_url)
        return "APIKEY " + resp.headers["api-key"]

    @staticmethod
    def session_dir():
        sessions = Path("espn/sessions")
        if not sessions.exists() or not sessions.is_dir():
            sessions.mkdir()
        return sessions

    def user_session_file(self):
        return EspnApi.session_dir() / self.session_file_name()

    def login(self):
        login_payload = {
            "loginValue": self.username,
            "password": self.password
        }
        login_headers = {
            "authorization": EspnApi.api_key(),
            "content-type": "application/json",
        }
        LOGGER.info("logging into ESPN for %(user)s...", {"user": self.username})
        start = time.time()
        resp = requests.post(EspnApi.LOGIN_URL, data=json.dumps(login_payload), headers=login_headers)
        end = time.time()
        if resp.status_code != 200:
            LOGGER.error("could not log into ESPN: %(msg)s", {"msg": resp.reason})
            LOGGER.error(resp.text)
            raise LoginException
        key = resp.json().get('data').get('s2')
        LOGGER.info("logged in for %(user)s after %(time).3fs", {"user": self.username, "time": end - start})

        session = self.user_session_file()
        cache_file = session.open("w+")
        cache_file.truncate()
        cache_file.write(key)
        return key

    def key(self):
        session = self.user_session_file()
        if session.is_file():
            stored_key = session.read_text()
            if len(stored_key) > 0:
                return stored_key
        return self.login()

    def espn_request(self, method, url, payload, headers=None, check_cache=True):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)
        LOGGER.info(f"making {method} request to {url} in league {self.league_id} with headers {headers}")
        start_time = time.time()
        k = self.key()
        cookies = {"espn_s2": k}
        if method == 'GET':
            r = requests.get(url, headers=headers or {}, cookies=cookies)
        if method == 'POST':
            r = requests.post(url, headers=headers or {}, cookies=cookies, json=payload)
        if r.status_code == 401:
            LOGGER.warning("request denied, logging in again.")
            self.login()
            return self.espn_request(method=method, url=url, payload=payload, headers=headers, check_cache=check_cache)
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

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info['settings']['scoringSettings']['scoringItems']
        return list(map(EspnApi.json_to_scoring_setting, scoring_items))

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

    def player(self, player_id):
        """
        Given the ESPN id of a Player, this will return the Player object associated with that Player,
        or None if no such player exists.
        :param int player_id: the id in the ESPN system of the player to be requested
        :return Player: the associated Player object (or None)
        """
        filter_header = {"players": {"filterIds": {"value": [player_id]}}}
        resp = self.espn_get(self.player_url(), {"X-Fantasy-Filter": json.dumps(filter_header)}, check_cache=False)
        player_list = resp.json()["players"]
        if len(player_list) == 0:
            return None
        return roster_entry_to_player(player_list[0]["player"])

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
        url = self.set_lineup_url()
        cur_lineup = self.lineup(self.team_id)
        transitions = cur_lineup.transitions(lineup)
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
