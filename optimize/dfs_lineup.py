from typing import List, Dict, Optional, Set

from espn.football.football_position import FootballPosition
from espn.football.football_slot import FootballSlot
from footballdiehards.dfs_projection import DFSProjection

"""
1. Start with top x at each position, see if lineup is possible?
2. expand by 1 player each time, forcing that player into lineup?
3. expand adding next top player by value?
"""

"""
player pool:
Dict[position, List[projection]] - players sorted by proj. points

search space:
Dict[Position, count] - starting with strictly max possible of each using flex

gen all rosters using those params, filter down to possible with salary cap

"""


def _filtered_and_sorted_projections(projections: List[DFSProjection], position: FootballPosition):
    return list(
        sorted(
            filter(
                lambda dfs_proj: dfs_proj.position == position,
                projections
            ),
            key=lambda proj: proj.projection,
            reverse=True
        )
    )


def player_pool(projections: List[DFSProjection]) -> Dict[FootballPosition, List[DFSProjection]]:
    return {
        pos: _filtered_and_sorted_projections(projections, pos)
        for pos in FootballPosition
    }


def expand_search_space(search_space: Dict[FootballPosition, int],
                        pool: Dict[FootballPosition, List[DFSProjection]]) -> \
        Dict[FootballPosition, int]:
    nexts = []
    for pos in FootballPosition:
        next_up = search_space[pos] + 1
        proj = pool[pos][next_up]
        nexts.append(proj)
    pos_to_expand = max(nexts, key=lambda proj: proj.value()).position
    next_space = search_space.copy()
    next_space[pos_to_expand] += 1
    return next_space


def restricted_pool(pool: Dict[FootballPosition, List[DFSProjection]],
                    search_space: Dict[FootballPosition, List[DFSProjection]]) -> \
        Dict[FootballPosition, List[DFSProjection]]:
    return {
        pos: pool[pos][:count]
        for pos, count in search_space.items()
    }


def all_lineups(pool: Dict[FootballPosition, List[DFSProjection]],
                slots: Dict[FootballSlot, int]) -> List[Set[DFSProjection]]:
    return _all_lineups(pool, set(), slots)


def _all_lineups(pool: Dict[FootballPosition, List[DFSProjection]],
                 candidate: Set[DFSProjection],
                 slots: Dict[FootballSlot, int]) -> List[Set[DFSProjection]]:
    if sum(slots.values()) == 0:
        return [candidate]
    next_slot, count_left = next(filter(lambda i: i[1] > 0, slots.items()))
    new_lineups = []
    for pos in positions_for_slot[next_slot]:
        players = filter(lambda p: p not in candidate, pool[pos])
        for player in players:
            new_candidate = candidate.copy()
            new_candidate.add(player)
            new_slots = slots.copy()
            new_slots[next_slot] -= 1
            new_lineups += _all_lineups(pool, new_candidate, new_slots)
    return new_lineups


positions_for_slot: Dict[FootballSlot, List[FootballPosition]] = {
    FootballSlot.QUARTER_BACK: [FootballPosition.QUARTER_BACK],
    FootballSlot.RUNNING_BACK: [FootballPosition.RUNNING_BACK],
    FootballSlot.WIDE_RECEIVER: [FootballPosition.WIDE_RECEIVER],
    FootballSlot.TIGHT_END: [FootballPosition.TIGHT_END],
    FootballSlot.DEFENSE: [FootballPosition.DEFENSE],
    FootballSlot.FLEX: [FootballPosition.RUNNING_BACK, FootballPosition.WIDE_RECEIVER,
                        FootballPosition.TIGHT_END]
}


def _is_under_salary(lineup: Set[DFSProjection], salary: int) -> bool:
    return sum(map(lambda p: p.salary, lineup)) <= salary
