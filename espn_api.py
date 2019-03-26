import requests
import json
import os
from player import Player
from lineup import Lineup
from lineup_settings import LineupSettings

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
        return 7  # 2 - Bless the Rains

    def league_id(self):
        # accept as param to object
        return 94862462   # 56491263 - Bless the Rains

    def lineup_url(self):
        league_id = self.league_id()
        team_id = self.team_id()
        scoring_period_id = self.scoring_period()
        return "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/" \
               "{}" \
               "?forTeamId={}" \
               "&scoringPeriodId={}" \
               "&view=mRoster".format(league_id, team_id, scoring_period_id)

    def lineup(self):
        url = self.lineup_url()
        roster = self.espn_get(url, check_cache=False).json()['teams'][0]['roster']['entries']
        players = list(map(lambda e: (EspnApi.roster_entry_to_player(e), e['lineupSlotId']), roster))
        player_dict = dict()
        for (player, slot) in players:
            cur_list = player_dict.get(slot, list())
            cur_list.append(player)
            player_dict[slot] = cur_list
        return Lineup(player_dict)

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

    @staticmethod
    def transition_to_item(transition):
        return {
            "playerId": transition[0].espn_id,
            "type": "LINEUP",
            "fromLineupSlotId": transition[1],
            "toLineupSlotId": transition[2]
        }

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
        cur_lineup = self.lineup()
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
