import logging
from pathlib import Path
from typing import Dict, List

import requests
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from requests import HTTPError

from dump import load_from_cache
from player import Player
from timing.timed import timed

LOGGER = logging.getLogger("sleeper.api")


def _nfl_players_url():
    return "https://api.sleeper.app/players/nfl"


def _graphql_url():
    return "https://sleeper.app/graphql"


def _login_gql():
    return gql(
        """
query login_query($email_or_phone_or_username: String!, $password: String) {
login(email_or_phone_or_username: $email_or_phone_or_username, password: $password) {
token
avatar
cookies
created
display_name
real_name
email
notifications
phone
user_id
verification
data_updated
}
}
        """
    )


def _update_draft_queue_gql(player_ids, draft_id):
    player_id_str = ""
    for p_id in player_ids:
        player_id_str += f'"{p_id}", '

    gql_str = f"""
        mutation update_draft_queue {{
  update_draft_queue(player_ids: [{player_id_str[:-2]}], draft_id: "{draft_id}")
}}
        """
    return gql(gql_str)


class SleeperApi:
    def __init__(self, username, password, year):
        self.username = username
        self.password = password
        self.year = year
        self.gql_unauthenticated_client = Client(
            transport=RequestsHTTPTransport(_graphql_url()),
            fetch_schema_from_transport=True,
        )
        self.gql_client = Client(
            transport=RequestsHTTPTransport(
                _graphql_url(), headers={"authorization": self._token()}
            ),
            fetch_schema_from_transport=True,
        )

    @timed(LOGGER)
    def _get(self, url):
        return requests.get(url)

    @timed(LOGGER)
    def _post(self, url, payload):
        return requests.post(url, payload)

    def _token(self):
        token_cache = Path("cache/football/sleeper-token.p")
        return load_from_cache(token_cache, lambda: self._login()["login"]["token"])

    def _login(self):
        login_vars = {
            "email_or_phone_or_username": self.username,
            "password": self.password,
        }
        return self.gql_unauthenticated_client.execute(
            _login_gql(), variable_values=login_vars
        )

    def _nfl_info_url(self):
        return f"https://api.sleeper.app/schedule/nfl/regular/{self.year}"

    def players(self) -> Dict[str, int]:
        sleepers_players_cache = Path("cache/football/sleepers-players.p")
        response = load_from_cache(
            sleepers_players_cache, lambda: self._get(_nfl_players_url()).json()
        )
        player_ids = dict()
        for sleeper_id, player_json in response.items():
            if player_json["position"] not in ["QB", "TE", "WR", "RB", "DEF"]:
                continue
            name = player_json["first_name"] + " " + player_json["last_name"]
            player_ids[name] = sleeper_id
        return player_ids

    def _get_player_id(self, ids_by_name: Dict[str, int], name: str) -> int:
        overrides = {
            "Darrell Henderson Jr.": "Darrell Henderson",
            "Allen Robinson II": "Allen Robinson",
            "Odell Beckham Jr.": "Odell Beckham",
            "Travis Etienne Jr.": "Travis Etienne",
            "DJ Chark Jr.": "D.J. Chark",
            "Laviska Shenault Jr.": "Laviska Shenault",
            "Melvin Gordon III": "Melvin Gordon",
            "Ronald Jones II": "Ronald Jones",
            "William Fuller V": "Will Fuller",
            "Marvin Jones Jr.": "Marvin Jones",
            "AJ Dillon": "A.J. Dillon",
            "Michael Pittman Jr.": "Michael Pittman",
            "Irv Smith Jr.": "Irv Smith",
            "Henry Ruggs III": "Henry Ruggs",
            "Terrace Marshall Jr.": "Terrace Marshall",
            "Mark Ingram II": "Mark Ingram",
            "KJ Hamler": "K.J. Hamler",
            "Benny Snell Jr.": "Benny Snell",
            "Jeff Wilson Jr.": "Jeffery Wilson",
        }
        name = overrides.get(name, name)
        return ids_by_name.get(name)

    def update_draft_queue(self, players: List[Player], draft_id: int):
        player_ids = self.players()
        player_ids_ranked = []
        for p in players:
            p_id = self._get_player_id(player_ids, p.name)
            if p_id is None:
                LOGGER.warning(f"Could not find id for {p.name}")
            else:
                player_ids_ranked += [p_id]

        request_gql = _update_draft_queue_gql(player_ids_ranked, draft_id)
        try:
            response = self.gql_client.execute(request_gql)
        except HTTPError as e:
            LOGGER.error("Failed to update draft queue with error", e)
            raise e

        return response
