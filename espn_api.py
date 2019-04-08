import requests
import json
import os
import pickle
from player import Player
from lineup import Lineup
from team import Team
from league import League
from lineup_settings import LineupSettings
from scoring_setting import ScoringSetting
from stats import Stats

"""
http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>
- members[i].displayName == "zcwalsh" 
    -> id == ownerId
- scoringPeriodId



url that is hit on page load:
"http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/<LEAGUE_ID>?view=mMatchupScore" \
              "&view=mLiveScoring"

"""


class EspnApi:
    LOGIN_URL = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/guest/login?langPref=en-US"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cache = dict()

    def session_file_name(self):
        return "espn_s2_{u}.txt".format(u=self.username)

    @staticmethod
    def api_key():
        key_url = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/api-key?langPref=en-US"
        resp = requests.post(key_url)
        return "APIKEY " + resp.headers["api-key"]

    def login(self):
        login_payload = {
            "loginValue": self.username,
            "password": self.password
        }
        login_headers = {
            "authorization": EspnApi.api_key(),
            "content-type": "application/json",
        }
        print("Logging in...")
        resp = requests.post(EspnApi.LOGIN_URL, data=json.dumps(login_payload), headers=login_headers)
        key = resp.json().get('data').get('s2')
        print("Logged in.")
        cache_file = open(self.session_file_name(), "w+")
        cache_file.truncate()
        cache_file.write(key)
        return key

    def key(self):
        if os.path.isfile(self.session_file_name()):
            with open(self.session_file_name(), "r") as file:
                stored_key = file.read()
                if len(stored_key) > 0:
                    return stored_key
        return self.login()

    def espn_request(self, method, url, payload, check_cache=True):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)

        k = self.key()
        cookies = {"espn_s2": k}
        if method == 'GET':
            r = requests.get(url, cookies=cookies)
        if method == 'POST':
            r = requests.post(url, cookies=cookies, json=payload)
        if r.status_code == 401:
            self.login()
            return self.espn_request(method=method, url=url, payload=payload, check_cache=check_cache)
        self.cache[url] = r
        return r

    def espn_get(self, url, check_cache=True):
        return self.espn_request(method='GET', url=url, payload={}, check_cache=check_cache)

    def espn_post(self, url, payload):
        return self.espn_request(method='POST', url=url, payload=payload)

    def scoring_period(self):
        url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/{}".format(self.league_id())
        return self.espn_get(url).json()['scoringPeriodId']

    def member_id(self):
        return "{84C1CD19-5E2C-4D5D-81CD-195E2C4D5D75}"  # todo fetch when logging in, persist?

    def team_id(self):
        # use above lineup + display name to calc
        return 2  # - Bless the Rains

    def league_id(self):
        # accept as param to object
        return 56491263  # Bless the Rains

    def lineup_url(self):
        league_id = self.league_id()
        team_id = self.team_id()
        scoring_period_id = self.scoring_period()
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?forTeamId={}" \
               "&scoringPeriodId={}" \
               "&view=mRoster".format(league_id, team_id, scoring_period_id)

    # team_id -> Lineup
    def lineup(self, team_id):
        return self.all_lineups()[team_id]

    def all_lineups_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?view=mRoster" \
               "&scoringPeriodId={}".format(self.league_id(), self.scoring_period())

    # { team_id: Lineup, ...}
    def all_lineups(self):
        resp = self.espn_get(self.all_lineups_url()).json()
        teams = resp['teams']
        lineup_dict = dict()
        for team in teams:
            roster = team['roster']['entries']
            players = list(map(lambda e: (EspnApi.roster_entry_to_player(e), e['lineupSlotId']), roster))
            lineup = EspnApi.player_list_to_lineup(players)
            lineup_dict[team['id']] = lineup
        return lineup_dict

    def all_info_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions" \
               "&view=mPositionalRatings&view=mSettings&view=mTeam".format(self.league_id())

    def all_info(self):
        return self.espn_get(self.all_info_url())

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info['settings']['scoringSettings']['scoringItems']
        return list(map(EspnApi.json_to_scoring_setting, scoring_items))

    def year_stats(self):
        teams = self.all_info().json()['teams']
        team_to_stats = dict()
        for t in teams:
            stats = Stats(t['valuesByStat'])
            team_to_stats[t['id']] = stats
        return team_to_stats

    def lineup_settings_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}?view=mSettings".format(self.league_id())

    def lineup_settings(self):
        url = self.lineup_settings_url()
        settings = self.espn_get(url).json()['settings']['rosterSettings']['lineupSlotCounts']
        return LineupSettings(settings)

    def set_lineup_url(self):
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}/transactions/".format(self.league_id())

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
            "teamId": self.team_id(),
            "type": "ROSTER",
            "memberId": self.member_id(),
            "scoringPeriodId": self.scoring_period(),
            "executionType": "EXECUTE",
            "items": list(map(EspnApi.transition_to_item, transitions))
        }
        return payload

    def set_lineup(self, lineup):
        url = self.set_lineup_url()
        cur_lineup = self.lineup(self.team_id())
        transitions = cur_lineup.transitions(lineup)
        payload = self.set_lineup_payload(transitions)
        return self.espn_post(url, payload)

    @staticmethod
    def roster_entry_to_player(entry):
        player_id = entry['playerId']
        player_map = entry['playerPoolEntry']['player']
        name = player_map['fullName']
        position = player_map['defaultPositionId']
        possible_positions = player_map['eligibleSlots']
        return Player(name, player_id, position, possible_positions)

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
        return ScoringSetting(item['statId'], item['isReverseItem'])

    @staticmethod
    def transition_to_item(transition):
        return {
            "playerId": transition[0].espn_id,
            "type": "LINEUP",
            "fromLineupSlotId": transition[1],
            "toLineupSlotId": transition[2]
        }
