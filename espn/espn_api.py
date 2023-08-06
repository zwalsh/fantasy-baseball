import json
import logging
import time
from abc import abstractmethod, ABCMeta
from typing import Dict, List

import requests

from espn.team_schedule import ProTeamGame
from league import League
from lineup import Lineup
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


def _player_draft_strategy_item(player: Player):
    return {"playerId": player.espn_id}


def _draft_strategy_json(rankings: List[Player]):
    return {
        "draftStrategy": {"draftList": list(map(_player_draft_strategy_item, rankings))}
    }


class EspnApi(metaclass=ABCMeta):
    def __init__(self, session_provider, league_id, team_id, year=2023):
        """
        Programmatic access to ESPN's (undocumented) API, caching requests that do not need
        refreshing, and automatically fetching a token for the user/password combination.

        :param EspnSessionProvider session_provider: using a username and password, provides
        and stores session tokens
        """
        self.session_provider = session_provider
        self.league_id = league_id
        self.team_id = team_id
        self.year = year
        self.cache = dict()

    @abstractmethod
    def _stat_enum(self):
        pass

    @abstractmethod
    def _api_url_segment(self):
        """
        Returns the URL segment for this api, e.g. flb, ffb, etc.
        :return:
        """
        pass

    @abstractmethod
    def _position(self, position_id):
        pass

    @abstractmethod
    def _slot_enum(self):
        pass

    def _all_lineups_url(self, scoring_period):
        return self._scoring_period_info_url(scoring_period)

    def _espn_request(
            self, method, url, payload, headers=None, check_cache=True, retries=1
    ):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)
        LOGGER.info(f"making {method} request to {url} in with headers {headers}")
        start_time = time.time()
        k = self.session_provider.get_session()
        cookies = {"espn_s2": k}
        response = None
        if method == "GET":
            response = requests.get(url, headers=headers or {}, cookies=cookies)
        if method == "POST":
            response = requests.post(
                url, headers=headers or {}, cookies=cookies, json=payload
            )
        if response is None:
            LOGGER.error("Got no response")
            raise EspnApiException(url)
        if response.status_code == 401:
            LOGGER.warning("request denied, logging in again.")
            self.session_provider.refresh_session()
            return self._espn_request(
                method=method,
                url=url,
                payload=payload,
                headers=headers,
                check_cache=check_cache,
            )
        if not response.ok:
            elapsed_time = start_time - time.time()
            LOGGER.error(
                f"received {response.status_code} {response.reason}: {response.text} in "
                f"{elapsed_time :.3f} seconds"
            )
            if retries > 0:
                LOGGER.info("retrying request")
                return self._espn_request(
                    method=method,
                    url=url,
                    payload=payload,
                    headers=headers,
                    check_cache=check_cache,
                    retries=retries - 1,
                )
            raise EspnApiException(url)
        if response.text is None or response.text == "":
            LOGGER.error(
                f"the response was blank after {start_time - time.time():.3f} seconds"
            )
            if retries > 0:
                return self._espn_request(
                    method=method,
                    url=url,
                    payload=payload,
                    headers=headers,
                    check_cache=check_cache,
                    retries=retries - 1,
                )
            raise EspnApiException(url)
        end_time = time.time()
        LOGGER.info("finished after %(time).3fs", {"time": end_time - start_time})
        self.cache[url] = response
        return response

    def _espn_get(self, url, headers=None, check_cache=True):
        return self._espn_request(
            method="GET", url=url, payload={}, headers=headers, check_cache=check_cache
        )

    def _espn_post(self, url, payload, headers=None):
        return self._espn_request(
            method="POST", url=url, payload=payload, headers=headers
        )

    def _base_url_no_league(self):
        return (
            f"http://fantasy.espn.com/apis/v3/games/{self._api_url_segment()}"
            f"/seasons/{self.year}"
        )

    def _base_url(self):
        return (
            f"{self._base_url_no_league()}/segments/0/leagues/"
            f"{self.league_id}"
        )

    def _team_url(self):
        return f"{self._base_url()}" f"/teams/{self.team_id}"

    def _scoring_period_info_url(self, scoring_period):
        return f"{self._base_url()}" f"?scoringPeriodId={scoring_period}&view=mRoster"

    def _lineup_url(self):
        return (
            f"{self._base_url()}"
            f"?forTeamId={self.team_id}"
            f"&scoringPeriodId={self.scoring_period()}"
            "&view=mRoster"
        )

    def _all_info_url(self):
        return (
            f"{self._base_url()}"
            "?view=mLiveScoring&view=mMatchupScore&view=mPendingTransactions"
            "&view=mPositionalRatings&view=mSettings&view=mTeam"
        )

    def _lineup_settings_url(self):
        return f"{self._base_url()}?view=mSettings"

    def _set_lineup_url(self):
        return f"{self._base_url()}/transactions/"

    def scoring_period(self):
        return self._espn_get(self._base_url()).json()["scoringPeriodId"]

    def roster_entry_to_player(self, player_map):
        """
        Takes an object from the ESPN API that represents a Player
        and converts it into a Player, including all positions
        :param player_map: ESPN api player object
        :return: Player object
        """
        player_id = player_map["id"]
        name = player_map["fullName"]
        default_position_id = player_map["defaultPositionId"]
        eligible_slots = player_map["eligibleSlots"]
        position = self._position(default_position_id)
        first = player_map["firstName"]
        last = player_map["lastName"]
        pro_team_id = player_map["proTeamId"]
        possible_positions = set()
        for slot in eligible_slots:
            converted = self._slot_for_id(slot)
            if converted is not None:
                possible_positions.add(converted)
        return Player(name, first, last, player_id, possible_positions, position, pro_team_id)

    def lineup(self, team_id=None):
        """
        Returns the current lineup of the team with the given team id
        :param int team_id: the id of the team in this league to get the lineup for
        :return Lineup: Lineup the lineup of the given team
        """
        return self.all_lineups()[team_id or self.team_id]

    def all_lineups(self, scoring_period=None) -> Dict[int, Lineup]:
        if scoring_period is None:
            scoring_period = self.scoring_period()
        resp = self._espn_get(self._all_lineups_url(scoring_period)).json()
        teams = resp["teams"]
        lineup_dict = dict()
        for team in teams:
            roster = team["roster"]["entries"]
            players = list(
                map(
                    lambda e: (
                        self.roster_entry_to_player(e["playerPoolEntry"]["player"]),
                        self._slot_for_id(e["lineupSlotId"]),
                    ),
                    roster,
                )
            )
            lineup = self._player_list_to_lineup(players)
            lineup_dict[team["id"]] = lineup
        return lineup_dict

    def all_info(self):
        return self._espn_get(self._all_info_url())

    def _scoring_period_info(self, scoring_period):
        return self._espn_get(self._scoring_period_info_url(scoring_period))

    def team_name(self, team_id=None):
        """
        Fetches the name of the team with the given id, or the id of the team tied to this object
        if none is given. The name is the concatenation of the team's "location" and the team's
        "nickname", per ESPN.
        :param int team_id: the id of the team whose name is to be fetched
        :return str: the name fetched from ESPN for the given team
        """
        team_id = team_id or self.team_id
        teams = self.all_info().json()["teams"]
        team = next(filter(lambda t: t["id"] == team_id, teams))
        return f"{team['location']} {team['nickname']}"

    def lineup_slot_counts_to_lineup_settings(self, settings):
        """
        Takes an ESPN API dictionary mapping slots (which arrive as strings)
        to counts (which arrive as ints), and converts it into a LineupSettings object
        :param dict settings: mapping of slot to count
        :return LineupSettings: the settings object for the given dictionary
        """
        converted_settings = dict()

        for slot_id, count in settings.items():
            slot = self._slot_for_id(int(slot_id))
            if slot is not None:
                converted_settings[slot] = count
        return LineupSettings(converted_settings)

    def lineup_settings(self):
        url = self._lineup_settings_url()
        settings = self._espn_get(url).json()["settings"]["rosterSettings"][
            "lineupSlotCounts"
        ]
        return self.lineup_slot_counts_to_lineup_settings(settings)

    def create_stats(self, espn_stats_dict):
        transformed_stats = dict()
        for stat_id_str in espn_stats_dict.keys():
            stat_id = int(stat_id_str)
            stat = self._stat_enum().espn_stat_to_stat(stat_id)
            if stat:
                stat_val = float(espn_stats_dict.get(stat_id_str))
                transformed_stats[stat] = stat_val

        return Stats(transformed_stats, self._stat_enum())

    def year_stats(self):
        """
        Returns a dictionary of all stats for all teams on the year.
        Maps team id to Stats object
        :return: mapping of team id to Stats for the year
        """
        teams = self.all_info().json()["teams"]
        team_to_stats = dict()
        for t in teams:
            stats = self.create_stats(t["valuesByStat"])
            team_to_stats[t["id"]] = stats
        return team_to_stats

    def _cumulative_stats_from_roster_entries(self, entries, scoring_period_id):
        """
        Takes a list of roster entries and reconstitutes the cumulative stats produced by that
        roster.
        :param list entries: the entries produced
        :param int scoring_period_id: the scoring period for which stats are being accumulated
        :return Stats: the sum total of stats produced by starters on that roster
        """
        total_stats = Stats({}, self._stat_enum())
        for e in filter(self.is_starting, entries):
            entry_stats_list = e["playerPoolEntry"]["player"]["stats"]
            stats_dict = next(
                filter(
                    lambda d: d["scoringPeriodId"] == scoring_period_id
                              and d["statSourceId"] == 0
                              and d["statSplitTypeId"] == 5,
                    entry_stats_list,
                ),
                None,
            )
            if stats_dict is None:
                name = e["playerPoolEntry"]["player"]["fullName"]
                LOGGER.warning(
                    f"{name} has no stats matching scoring period {scoring_period_id} "
                    f"found in entry {e}"
                )
                continue
            stats = self.create_stats(stats_dict["stats"])
            total_stats += stats
        return total_stats

    def scoring_period_stats(self, scoring_period):
        teams = self._scoring_period_info(scoring_period).json()["teams"]
        team_to_stats = dict()
        for t in teams:
            stats = self._cumulative_stats_from_roster_entries(
                t["roster"]["entries"], scoring_period
            )
            team_to_stats[t["id"]] = stats
        return team_to_stats

    def _season_stats_from_player_stats_array(self, player_stats) -> Dict[int, Stats]:
        # for stat_dict in player_stats:
        #     LOGGER.info(f"source: {stat_dict['statSourceId']}")
        #     LOGGER.info(f"split: {stat_dict['statSplitTypeId']}")
        #     LOGGER.info(f"scoringPd: {stat_dict['scoringPeriodId']}")

        relevant_stats = filter(
            lambda s: s["statSourceId"] == 0
                      and s["statSplitTypeId"] == 1
                      and s["seasonId"] == self.year,
            player_stats,
        )
        return {
            stat_dict["scoringPeriodId"]: self.create_stats(stat_dict["stats"])
            for stat_dict in relevant_stats
        }

    def player_stats(self) -> Dict[Player, Dict[int, Stats]]:
        """
        Return all players' stats in all scoring periods.

        Expensive! Requires a separate HTTP request for each individual player.
        :return dict: Dictionary mapping player to all of their stats, keyed by scoring period
        """
        player_stats = {}
        players = self._all_players()
        LOGGER.info(f"Parsing stats for {len(players)} players")
        for player_obj in players:
            try:
                full_player_obj = self._player_request(player_obj["id"])
                player = self.roster_entry_to_player(full_player_obj)
                player_stats[player] = self._season_stats_from_player_stats_array(
                    full_player_obj["stats"]
                )
            except ValueError:
                LOGGER.error(f"Could not parse player from {player_obj['player']}")
        return player_stats

    def scoring_settings(self):
        info = self.all_info().json()
        scoring_items = info["settings"]["scoringSettings"]["scoringItems"]
        return list(map(self._json_to_scoring_setting, scoring_items))

    def points_per_stat(self):
        return {setting.stat: setting.points for setting in self.scoring_settings()}

    def _json_to_scoring_setting(self, item):
        stat = self._stat_enum().espn_stat_to_stat(item["statId"])
        points = item["pointsOverrides"].get(16, item["points"])
        return ScoringSetting(stat, item["isReverseItem"], points)

    def _player_url(self):
        return f"{self._base_url()}?view=kona_player_info"

    def _all_players_url(self):
        return f"{self._base_url()}?view=kona_player_info"

    def _player_request(self, player_id):
        """
        Makes the request to ESPN for the player with the player id and returns the raw response
        (parsed from JSON).
        :param int player_id: the id of the player to make the request about
        :return dict: the parsed response from ESPN
        """
        filter_header = {
            "players": {
                "filterIds": {"value": [player_id]},
                "filterStatsForTopScoringPeriodIds": {
                    "value": 16,
                    "additionalValue": [
                        "002020",
                        "102020",
                        "002019",
                        "1120207",
                        "022020",
                    ],
                },
            }
        }
        resp = self._espn_get(
            self._player_url(),
            {"X-Fantasy-Filter": json.dumps(filter_header)},
            check_cache=False,
        )
        return resp.json()["players"][0]["player"]

    def _all_players(self):
        filter_header = {
            "players": {
                "limit": 400,
                "sortPercOwned": {"sortPriority": 2, "sortAsc": False},
            }
        }
        resp = self._espn_get(
            self._player_url(),
            {"X-Fantasy-Filter": json.dumps(filter_header)},
            check_cache=False,
        )
        players_json_array = resp.json()["players"]
        return players_json_array

    def player(self, player_id):
        """
        Given the ESPN id of a Player, this will return the Player object associated with that
        Player, or None if no such player exists.
        :param int player_id: the id in the ESPN system of the player to be requested
        :return Player: the associated Player object (or None)
        """
        return self.roster_entry_to_player(self._player_request(player_id))

    def all_players_sorted(self):
        players_json_array = self._all_players()
        players_list = list(
            map(
                lambda p: (
                    p["player"],
                    p.get("player", {})
                        .get("draftRanksByRankType", {})
                        .get("STANDARD", {})
                        .get("rank", 9999),
                ),
                players_json_array,
            )
        )
        relevant_players = filter(lambda p: p[1] not in {0, 9999}, players_list)
        sorted_list = sorted(relevant_players, key=lambda tup: tup[1])
        return list(map(lambda tup: self.roster_entry_to_player(tup[0]), sorted_list))

    def players_by_name(self) -> Dict[str, Player]:
        players = self.all_players_sorted()
        players_by_name = {p.name: p for p in players}
        return players_by_name

    def league(self):
        """
        Fetches the whole league, including each team's current lineup and yearly stats
        :return: League - the whole league
        """
        stats = self.year_stats()
        teams = []
        for team_id, lineup in stats.items():
            t = Team(team_id, lineup, stats.get(team_id))
            teams.append(t)
        return League(teams)

    def _player_list_to_lineup(self, players):
        player_dict = dict()
        for (player, slot) in players:
            cur_list = player_dict.get(slot, list())
            cur_list.append(player)
            player_dict[slot] = cur_list
        return Lineup(player_dict, self._slot_enum())

    def _slot_for_id(self, slot_id):
        return self._slot_enum().espn_slot_to_slot(slot_id)

    def is_starting(self, roster_entry):
        slot_id = roster_entry["lineupSlotId"]
        slot = self._slot_for_id(slot_id)
        return slot in self._slot_enum().starting_slots()

    def member_id(self):
        return "{84C1CD19-5E2C-4D5D-81CD-195E2C4D5D75}"

    def _set_lineup_payload(self, transitions):
        payload = {
            "isLeagueManager": False,
            "teamId": self.team_id,
            "type": "ROSTER",
            "memberId": self.member_id(),
            "scoringPeriodId": self.scoring_period(),
            "executionType": "EXECUTE",
            "items": list(map(self._transition_to_item, transitions)),
        }
        return payload

    def _transition_to_item(self, transition):
        """
        Creates the ESPN API item for a transition out of a LineupTransition object.
        :param LineupTransition transition:
        :return:
        """
        return {
            "playerId": transition.player.espn_id,
            "type": "LINEUP",
            "fromLineupSlotId": self._slot_enum().slot_to_slot_id(transition.from_slot),
            "toLineupSlotId": self._slot_enum().slot_to_slot_id(transition.to_slot),
        }

    def execute_transitions(self, transitions):
        """
        Executes the given transitions, moving players as specified.
        :param list transitions: the list of LineupTransitions to execute
        :return: the response returned from the POST request
        """
        url = self._set_lineup_url()
        for t in transitions:
            LOGGER.info(f"executing transition {t}")
        payload = self._set_lineup_payload(transitions)
        return self._espn_post(url, payload)

    def set_lineup(self, lineup):
        cur_lineup = self.lineup(self.team_id)
        transitions = cur_lineup.transitions(lineup)
        return self.execute_transitions(transitions)

    def set_draft_strategy(self, rankings: List[Player]):
        draft_strategy_url = self._team_url()
        payload = _draft_strategy_json(rankings)
        return self._espn_post(draft_strategy_url, payload)

    def _pro_schedule_url(self):
        return f"{self._base_url_no_league()}?view=proTeamSchedules_wl"

    def _pro_game_from_entry(self, entry):
        return ProTeamGame(
            home_team=entry["homeProTeamId"],
            away_team=entry["awayProTeamId"],
            game_id=entry["id"]
        )

    def pro_team_schedule(self) -> Dict[int, Dict[int, List[ProTeamGame]]]:
        """
        Returns the complete schedule of professional team games.

        :return: Map of team id to games, keyed by scoring period. Note a team can have double-headers
        """
        pro_schedule_response = self._espn_get(self._pro_schedule_url()).json()
        pro_teams = pro_schedule_response["settings"]["proTeams"]

        schedule = {}
        for team_entry in pro_teams:
            team_id = team_entry["id"]
            team_schedule = {}
            for scoring_period, pro_games in team_entry["proGamesByScoringPeriod"].items():
                games = list(map(self._pro_game_from_entry, pro_games))
                team_schedule[int(scoring_period)] = games
            schedule[team_id] = team_schedule

        return schedule
