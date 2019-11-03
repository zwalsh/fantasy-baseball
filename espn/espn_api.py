import json
import logging
import time
from abc import abstractmethod, ABCMeta

import requests

from espn.sessions.espn_session_provider import EspnSessionProvider
from league import League
from lineup_settings import LineupSettings
from player import Player
from scoring_setting import ScoringSetting
from stats import Stats
from team import Team

LOGGER = logging.getLogger("espn.api")


class EspnApiException(Exception):
    """
    Exception to throw when a request to the ESPN API failed
    """
    pass


class EspnApi(metaclass=ABCMeta):
    def __init__(self, session_provider, league_id, team_id):
        """
        Programmatic access to ESPN's (undocumented) API, caching requests that do not need refreshing,
        and automatically fetching a token for the user/password combination.

        :param EspnSessionProvider session_provider: using a username and password, provides and stores session tokens
        """
        self.session_provider = session_provider
        self.league_id = league_id
        self.team_id = team_id
        self.cache = dict()

    def espn_request(self, method, url, payload, headers=None, check_cache=True, retries=1):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)
        LOGGER.info(f"making {method} request to {url} in with headers {headers}")
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

    @abstractmethod
    def api_url_segment(self):
        """
        Returns the URL segment for this api, e.g. flb, ffb, etc.
        :return:
        """
        pass

    @abstractmethod
    def position(self, position_id):
        pass

    def base_url(self):
        return f"http://fantasy.espn.com/apis/v3/games/{self.api_url_segment()}/seasons/2019/segments/0/leagues/" \
               f"{self.league_id}"

    def scoring_period_info_url(self, scoring_period):
        return f"{self.base_url()}" \
               f"?scoringPeriodId={scoring_period}&view=mRoster"

    def lineup_url(self):
        return f"{self.base_url()}" \
               f"?forTeamId={self.team_id}" \
               f"&scoringPeriodId={self.scoring_period()}" \
               "&view=mRoster"

    def all_lineups_url(self):
        return self.scoring_period_info_url(self.scoring_period())

    def all_info_url(self):
        return f"{self.base_url()}" \
               "?view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions" \
               "&view=mPositionalRatings&view=mSettings&view=mTeam"

    def lineup_settings_url(self):
        return f"{self.base_url()}?view=mSettings"

    @staticmethod
    @abstractmethod
    def player_list_to_lineup(players):
        pass

    def scoring_period(self):
        return self.espn_get(self.base_url()).json()['scoringPeriodId']

    def lineup(self, team_id=None):
        """
        Returns the current lineup of the team with the given team id
        :param int team_id: the id of the team in this league to get the lineup for
        :return Lineup: Lineup the lineup of the given team
        """
        return self.all_lineups()[team_id or self.team_id]

    def all_lineups(self):
        resp = self.espn_get(self.all_lineups_url()).json()
        teams = resp['teams']
        lineup_dict = dict()
        for team in teams:
            roster = team['roster']['entries']
            players = list(map(lambda e:
                               (self.roster_entry_to_player(e["playerPoolEntry"]["player"]),
                                          self.slot_for_id(e['lineupSlotId'])), roster))
            lineup = self.player_list_to_lineup(players)
            lineup_dict[team['id']] = lineup
        return lineup_dict

    def all_info(self):
        return self.espn_get(self.all_info_url())

    def scoring_period_info(self, scoring_period):
        return self.espn_get(self.scoring_period_info_url(scoring_period))

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

    # DATA PARSING
    def roster_entry_to_player(self, player_map):
        """
        Takes an object from the ESPN API that represents a Player
        and converts it into a Player, including all positions
        :param player_map: ESPN api player object
        :return: Player object
        """
        player_id = player_map['id']
        name = player_map['fullName']
        default_position_id = player_map['defaultPositionId']
        eligible_slots = player_map['eligibleSlots']
        position = self.position(default_position_id)
        first = player_map['firstName']
        last = player_map['lastName']
        possible_positions = set()
        for slot in eligible_slots:
            converted = self.slot_for_id(slot)
            if converted is not None:
                possible_positions.add(converted)
        return Player(name, first, last, player_id, possible_positions, position)

    def lineup_slot_counts_to_lineup_settings(self, settings):
        """
        Takes an ESPN API dictionary mapping slots (which arrive as strings)
        to counts (which arrive as ints), and converts it into a LineupSettings object
        :param dict settings: mapping of slot to count
        :return LineupSettings: the settings object for the given dictionary
        """
        converted_settings = dict()

        for slot_id, count in settings.items():
            slot = self.slot_for_id(int(slot_id))
            if slot is not None:
                converted_settings[slot] = count
        return LineupSettings(converted_settings)

    @abstractmethod
    def slot_for_id(self, slot_id):
        """
        Returns the lineup slot for the given espn slot id
        :param int slot_id: the id of the slot
        :return Enum: a member of an Enum representing a Slot
        """
        pass

    @abstractmethod
    def stat_enum(self):
        pass

    def lineup_settings(self):
        url = self.lineup_settings_url()
        settings = self.espn_get(url).json()['settings']['rosterSettings']['lineupSlotCounts']
        return self.lineup_slot_counts_to_lineup_settings(settings)

    def create_stats(self, espn_stats_dict):
        transformed_stats = dict()
        for stat_id_str in espn_stats_dict.keys():
            stat_id = int(stat_id_str)
            stat = self.stat_enum().espn_stat_to_stat(stat_id)
            if stat:
                stat_val = float(espn_stats_dict.get(stat_id_str))
                transformed_stats[stat] = stat_val

        return Stats(transformed_stats, self.stat_enum())

    def year_stats(self):
        """
        Returns a dictionary of all stats for all teams on the year.
        Maps team id to Stats object
        :return: mapping of team id to Stats for the year
        """
        teams = self.all_info().json()['teams']
        team_to_stats = dict()
        for t in teams:
            stats = self.create_stats(t['valuesByStat'])
            team_to_stats[t['id']] = stats
        return team_to_stats

    @abstractmethod
    def is_starting(self, roster_entry):
        """
        Checks if the given roster entry is a starting one
        :param roster_entry:
        :return:
        """
        pass

    def cumulative_stats_from_roster_entries(self, entries, scoring_period_id):
        """
        Takes a list of roster entries and reconstitutes the cumulative stats produced by that roster.
        :param list entries: the entries produced
        :param int scoring_period_id: the scoring period for which stats are being accumulated
        :return Stats: the sum total of stats produced by starters on that roster
        """
        total_stats = Stats({}, self.stat_enum())
        for e in filter(self.is_starting, entries):
            entry_stats_list = e["playerPoolEntry"]["player"]["stats"]
            stats_dict = next(filter(lambda d: d['scoringPeriodId'] == scoring_period_id and d['statSourceId'] == 0, entry_stats_list), None)
            if stats_dict is None:
                name = e["playerPoolEntry"]["player"]["fullName"]
                LOGGER.warning(f"{name} has no stats matching scoring period {scoring_period_id} found in entry {e}")
                continue
            stats = self.create_stats(stats_dict["stats"])
            total_stats += stats
        return total_stats

    def scoring_period_stats(self, scoring_period):
        teams = self.scoring_period_info(scoring_period).json()["teams"]
        team_to_stats = dict()
        for t in teams:
            stats = self.cumulative_stats_from_roster_entries(t["roster"]["entries"], scoring_period)
            team_to_stats[t['id']] = stats
        return team_to_stats

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info['settings']['scoringSettings']['scoringItems']
        return list(map(self.json_to_scoring_setting, scoring_items))

    def json_to_scoring_setting(self, item):
        stat = self.stat_enum().espn_stat_to_stat(item['statId'])
        LOGGER.debug(f"processing {item} = {stat}")
        return ScoringSetting(stat, item['isReverseItem'])

    def player_url(self):
        return f"{self.base_url()}?view=kona_playercard"

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
        return self.roster_entry_to_player(self.player_request(player_id))

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

