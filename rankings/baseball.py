import logging
from typing import Dict

from espn.baseball.baseball_api import BaseballApi
from fantasypros.api import FantasyProsApi
from player import Player

LOGGER = logging.getLogger("rankings.baseball")


def set_predraft_rankings(fantasypros: FantasyProsApi, baseball: BaseballApi):
    rankings = fantasypros.baseball_draft_rankings()
    LOGGER.info("Pulled fantasypros rankings:")
    for rank, name in enumerate(rankings):
        LOGGER.info(f"{rank + 1:03}: {name}")

    all_players = baseball.players_by_name()

    ranked_players = map(lambda n: _player_obj_from_name(n, all_players), rankings)
    ranked_players = filter(lambda p: p is not None, ranked_players)

    baseball.set_draft_strategy(list(ranked_players))


OVERRIDDEN_NAMES = {
    'Cedric Mullins II': 'Cedric Mullins',
    # 'Ramon Laureano':
    'Kike Hernandez': 'Enrique Hernandez',
    'Wil Myers': '',
}


def _player_obj_from_name(name: str, all_players: Dict[str, Player]) -> Player:
    overridden_name = OVERRIDDEN_NAMES.get(name, name)
    player = all_players.get(overridden_name)
    if player is None:
        LOGGER.warning(f"Could not get Player with name {overridden_name}")
    return player
