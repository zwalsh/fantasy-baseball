import requests
import json
import os
from player import Player

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

    def espn_request(self, url, check_cache=True):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)

        k = self.key()
        r = requests.get(url, cookies={"espn_s2": k})
        if r.status_code == 401:
            self.login()
            return self.espn_request(url)
        self.cache[url] = r
        return r

    def scoring_period(self):
        url = "http://fantasy.espn.com/apis/v3/games/flb/seasons/2019/segments/0/leagues/{}".format(self.league_id())
        return self.espn_request(url).json()['scoringPeriodId']

    def team_id(self):
        # use above lineup + display name to calc
        return 2  # hard-coded for

    def league_id(self):
        # accept as param to object
        return 56491263

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
        roster = self.espn_request(url).json()['teams'][0]['roster']['entries']
        return list(map(lambda e: (EspnApi.roster_entry_to_player(e), e['lineupSlotId']), roster))

    @staticmethod
    def roster_entry_to_player(entry):
        player_id = entry['playerId']
        player_map = entry['playerPoolEntry']['player']
        name = player_map['fullName']
        position = player_map['defaultPositionId']
        possible_positions = player_map['eligibleSlots']
        return Player(name, player_id, position, possible_positions)