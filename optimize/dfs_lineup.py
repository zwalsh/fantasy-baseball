import logging
from typing import List, Dict, Optional, Set

from espn.football.football_position import FootballPosition
from espn.football.football_slot import FootballSlot
from footballdiehards.dfs_projection import DFSProjection

# 1. Start with top x at each position, see if lineup is possible?
# 2. expand by 1 player each time, forcing that player into lineup?
# 3. expand adding next top player by value?

# player pool:
# Dict[position, List[projection]] - players sorted by proj. points
#
# search space:
# Dict[Position, count] - starting with strictly max possible of each using flex
#
# gen all rosters using those params, filter down to possible with salary cap

LOGGER = logging.getLogger('optimize.dfs_lineup')

positions_for_slot: Dict[FootballSlot, List[FootballPosition]] = {
    FootballSlot.QUARTER_BACK: [FootballPosition.QUARTER_BACK],
    FootballSlot.RUNNING_BACK: [FootballPosition.RUNNING_BACK],
    FootballSlot.WIDE_RECEIVER: [FootballPosition.WIDE_RECEIVER],
    FootballSlot.TIGHT_END: [FootballPosition.TIGHT_END],
    FootballSlot.DEFENSE: [FootballPosition.DEFENSE],
    FootballSlot.FLEX: [FootballPosition.RUNNING_BACK, FootballPosition.WIDE_RECEIVER,
                        FootballPosition.TIGHT_END]
}
slots_for_position = {
    FootballPosition.QUARTER_BACK: FootballSlot.QUARTER_BACK,
    FootballPosition.RUNNING_BACK: FootballSlot.RUNNING_BACK,
    FootballPosition.WIDE_RECEIVER: FootballSlot.WIDE_RECEIVER,
    FootballPosition.TIGHT_END: FootballSlot.TIGHT_END,
    FootballPosition.DEFENSE: FootballSlot.DEFENSE
}


class PlayerPool:

    def __init__(self, player_dict: Dict[FootballPosition, List[DFSProjection]]):
        self.player_dict = player_dict

    def top_n_at_position(self, n: int, pos: FootballPosition) -> List[DFSProjection]:
        return self.player_dict[pos][:n]

    def players_for_slot(self, slot: FootballSlot) -> List[DFSProjection]:
        players = []
        for pos in positions_for_slot[slot]:
            players.extend(self.player_dict[pos])
        return players

    def player_at_rank(self, position: FootballPosition, rank: int) -> Optional[DFSProjection]:
        player_list = self.player_dict[position]
        return None if len(player_list) <= rank else player_list[rank]


class Lineup:

    def __init__(self, player_set: Set[DFSProjection]):
        self.player_set = player_set

    def total_salary(self):
        return sum(map(lambda p: p.salary, self.player_set))

    def total_points(self):
        return sum(map(lambda p: p.projection, self.player_set))


value_thresholds = {
    FootballPosition.QUARTER_BACK: 1.8,
    FootballPosition.RUNNING_BACK: 1.5,
    FootballPosition.WIDE_RECEIVER: 1.1,
    FootballPosition.TIGHT_END: 1.2,
    FootballPosition.DEFENSE: 0.15
}


def _filtered_and_sorted_projections(projections: List[DFSProjection], position: FootballPosition):
    return list(
        sorted(
            filter(
                lambda dfs_proj: dfs_proj.position == position and
                                 dfs_proj.value() > value_thresholds[dfs_proj.position],
                projections
            ),
            key=lambda proj: proj.projection,
            reverse=True
        )
    )


def player_pool(projections: List[DFSProjection]) -> PlayerPool:
    pool = PlayerPool({
        pos: _filtered_and_sorted_projections(projections, pos)
        for pos in FootballPosition
    })
    for pos in FootballPosition:
        LOGGER.info(f"Pool includes {len(pool.player_dict[pos])} at {pos}")

    return pool


def expand_search_space(search_space: Dict[FootballPosition, int],
                        pool: PlayerPool) -> \
        (Dict[FootballPosition, int], DFSProjection):
    nexts = []
    for pos in FootballPosition:
        next_up = search_space[pos] + 1
        proj = pool.player_at_rank(pos, next_up)
        if proj is not None:
            nexts.append(proj)
    player = max(nexts, key=lambda proj: proj.value())
    next_space = search_space.copy()
    next_space[player.position] += 1
    return next_space, player


def restricted_pool(pool: PlayerPool,
                    search_space: Dict[FootballPosition, List[DFSProjection]]) -> \
        PlayerPool:
    return PlayerPool({
        pos: pool.top_n_at_position(count, pos)
        for pos, count in search_space.items()
    })


starting_space = {
    FootballPosition.QUARTER_BACK: 2,
    FootballPosition.RUNNING_BACK: 4,
    FootballPosition.WIDE_RECEIVER: 5,
    FootballPosition.TIGHT_END: 2,
    FootballPosition.DEFENSE: 4
}


def best_lineup(pool: PlayerPool, slots: Dict[FootballSlot, int], salary: int) -> Lineup:
    space = starting_space
    # small_pool = restricted_pool(pool, space)
    lineups = []
    while len(lineups) == 0:
        space, player = expand_search_space(space, pool)
        LOGGER.info(f"Expanding search space, now includes {player.player}")
        small_pool = restricted_pool(pool, space)
        slots_with_player = slots.copy()
        slot = slots_for_position[player.position]
        slots_with_player[slot] -= 1
        lineups = valid_lineups(small_pool, slots_with_player, salary, {player})
    lineups.sort(key=lambda l: l.total_points(), reverse=True)
    LOGGER.info(f"Found {len(lineups)} possible lineups.")
    return lineups[0]


def valid_lineups(pool: PlayerPool, slots: Dict[FootballSlot, int], salary: int,
                  starting_candidate=None) -> List[Lineup]:
    if starting_candidate is None:
        starting_candidate = set()
    generated_lineups = all_lineups(pool, slots, starting_candidate)
    LOGGER.info(f"Generated {len(generated_lineups)} lineups")
    return [lineup for lineup in generated_lineups if lineup.total_salary() <= salary]


def all_lineups(pool: PlayerPool,
                slots: Dict[FootballSlot, int],
                starting_candidate: Set) -> List[Lineup]:
    return _all_lineups(pool, starting_candidate, slots)


def _all_lineups(pool: PlayerPool,
                 candidate: Set[DFSProjection],
                 slots: Dict[FootballSlot, int]) -> List[Lineup]:
    if sum(slots.values()) == 0:
        return [Lineup(candidate)]
    next_slot, _ = next(filter(lambda i: i[1] > 0, slots.items()))
    new_lineups = []
    for player in filter(lambda p: p not in candidate, pool.players_for_slot(next_slot)):
        new_candidate = candidate.copy()
        new_candidate.add(player)
        new_slots = slots.copy()
        new_slots[next_slot] -= 1
        new_lineups += _all_lineups(pool, new_candidate, new_slots)
    return new_lineups


def _is_under_salary(lineup: Set[DFSProjection], salary: int) -> bool:
    return sum(map(lambda p: p.salary, lineup)) <= salary
