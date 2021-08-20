# Generate pre-draft rankings based on value above replacement level
import logging
from datetime import date
from math import ceil
from pathlib import Path
from typing import Dict, List

from dump import load_from_cache
from espn.football.football_api import FootballApi
from espn.football.football_position import FootballPosition
from fantasypros.api import FantasyProsApi
from player import Player

LOGGER = logging.getLogger("rankings.rankings")


def roster_count_of_all_lineups(football: FootballApi):
    """
    Look at all scoring periods and return the average rostered player count.
    :param football: API
    :return: count of positions on each team at any point
    """
    all_scoring_periods = range(1, 17)
    rostered_count = dict()
    for p in FootballPosition:
        rostered_count[p] = 0

    for sp in all_scoring_periods:
        lineups = football.all_lineups(sp)
        for l in lineups.values():
            for p in l.players():
                rostered_count[p.default_position] = (
                    rostered_count[p.default_position] + 1
                )
    num_lineups = len(all_scoring_periods) * len(football.league().teams)
    LOGGER.info(f"number of total lineups all year: {num_lineups}")
    avg_count = dict()
    for p, ct in rostered_count.items():
        avg_num_for_pos = ct / num_lineups
        avg_count[p] = avg_num_for_pos
    return avg_count


def replacement_level(
    avg_rostered_count: Dict[FootballPosition, float], team_count: int
) -> Dict[FootballPosition, int]:
    """
    Calculate the ranking of player at each position that should be considered replacement level,
    based on the given average rostered player count per team.

    :param avg_rostered_count: how many of each position does the average team roster?
    :param team_count: the number of teams in the league
    :return: for each position, which rank of player is available at any time?
    """
    replacement = dict()
    for pos, count in avg_rostered_count.items():
        if pos == FootballPosition.RUNNING_BACK:
            count = (
                count - 0.9
            )  # adjusting based on new year w/ 10 teams but 1 fewer roster spot
        if pos == FootballPosition.WIDE_RECEIVER:
            count = count + 0.1
        if pos == FootballPosition.TIGHT_END:
            count = count - 0.2
        # if pos == FootballPosition.QUARTER_BACK:
        #     count = count
        replacement[pos] = ceil(count * team_count)

    return replacement


# players whose names may have different spellings in different places
OVERRIDES = {
    "Patrick Mahomes II": "Patrick Mahomes",
    "Darrell Henderson": "Darrell Henderson Jr.",
    "Travis Etienne": "Travis Etienne Jr.",
    "D.K. Metcalf": "DK Metcalf",
    "D.J. Moore": "DJ Moore",
    "D.J. Chark Jr.": "DJ Chark Jr.",
    "Will Fuller V": "William Fuller V",
    "Keelan Cole Sr.": "Keelan Cole",
}


def _get_player_with_overrides(name, players_by_name):
    if name in OVERRIDES.keys():
        name = OVERRIDES[name]
    return players_by_name.get(name)


def _players_by_name(football: FootballApi):
    players = load_from_cache(
        Path(f"cache/football/players-{football.year}.p"), football.all_players_sorted
    )
    players_by_name = {p.name: p for p in players}
    return players_by_name


def _cached_projections_by_name(fantasy_pros: FantasyProsApi):
    today = date.today()
    date_string = str(today)
    return load_from_cache(
        Path(f"cache/fp-proj-{date_string}.p"), fantasy_pros.week_football_projections
    )


def projections_by_player(
    football: FootballApi, fantasy_pros: FantasyProsApi
) -> Dict[Player, float]:
    """
    Returns the projected points that each player is likely to score, pulling from
    https://www.fantasypros.com/nfl/projections
    """
    points_map = football.points_per_stat()
    projections = _cached_projections_by_name(fantasy_pros)
    players = _players_by_name(football)
    projected_points = dict()
    for name, stats in projections.items():
        points = stats.points(points_map)
        player = _get_player_with_overrides(name, players)
        if player is None and points > 75:
            LOGGER.warning(f"Could not find player obj for name {name}")
        elif player is not None:
            projected_points[player] = points
    return projected_points


def ranked_by_position(
    projections: Dict[Player, float]
) -> Dict[FootballPosition, List[Player]]:
    """
    Sorts all players, sliced by default position, ranking by projection.
    """
    ranked_by_pos = dict()
    for pos in FootballPosition:
        # pylint: disable=cell-var-from-loop
        players = list(
            filter(lambda p: p.default_position == pos, iter(projections.keys()))
        )
        projections_at_pos = {
            player: projection
            for player, projection in projections.items()
            if player in players
        }
        ranked = sorted(
            projections_at_pos.items(), key=lambda tup: tup[1], reverse=True
        )
        ranked_by_pos[pos] = ranked
    return ranked_by_pos


def replacement_level_points(
    replacement: Dict[FootballPosition, int], ranked_by_pos
) -> Dict[FootballPosition, float]:
    """

    :return: how many points is "replacement level" at each position?
    """
    replacement_values = dict()
    for pos, rep in replacement.items():
        if pos == FootballPosition.DEFENSE:
            continue
        LOGGER.info(f"Replacement level at {pos} is {pos}{rep}")
        ranked = ranked_by_pos[pos]
        replacement_player, points = ranked[rep - 1]
        LOGGER.info(
            f"{pos}{rep} is projected to be {replacement_player.name} scoring {points:<.1f}"
        )
        replacement_values[pos] = points
    return replacement_values


def _player_values(
    projections: Dict[Player, float], replacement_values: Dict[FootballPosition, float]
):
    values = dict()
    for player, points in projections.items():
        value = points - replacement_values[player.default_position]
        values[player] = value
    return values


def rank_all_players(
    last_year: FootballApi, football: FootballApi, fantasy_pros: FantasyProsApi
) -> List[Player]:
    avg_count_cache = Path(
        f"cache/football/roster-count-{last_year.league_id}-{last_year.year}.p"
    )
    avg_count = load_from_cache(
        avg_count_cache, lambda: roster_count_of_all_lineups(last_year)
    )
    replacement_rank = replacement_level(avg_count, 10)
    projections = projections_by_player(football, fantasy_pros)

    ranked_by_pos = ranked_by_position(projections)
    replacement_values = replacement_level_points(replacement_rank, ranked_by_pos)

    values = _player_values(projections, replacement_values)

    sorted_by_value = sorted(values.items(), key=lambda tup: tup[1], reverse=True)

    LOGGER.info("RNK PRNK PLAYER                   VALUE POINTS")
    for rank, (player, value) in list(enumerate(sorted_by_value))[:200]:
        position_rankings = enumerate(
            map(lambda tup: tup[0], ranked_by_pos[player.default_position])
        )
        player_rank_at_position = (
            next(p_rank for (p_rank, p) in position_rankings if p == player) + 1
        )
        LOGGER.info(
            f"{rank + 1:<3} {player.default_position}{player_rank_at_position:<2} {player.name:<24} {value:5.1f} {projections[player]:5.1f}"
        )
    return list(map(lambda tup: tup[0], sorted_by_value))
