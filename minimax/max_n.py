import logging
from typing import List

from minimax.game_info import GameInfo
from minimax.game_state import GameState
from minimax.state_evaluator import StateEvaluator

LOGGER = logging.getLogger("minimax.max_n")


class MaxNResult:
    def __init__(self, result_node, values: List[int]):
        self.result_node = result_node
        self.values = values


max_n_total_nodes = 0


def max_n(
    node: GameState,
    player: int,
    upper_bound: int,
    game_info: GameInfo,
    state_evaluator: StateEvaluator,
    depth,
    answer_now=lambda depth: False,
) -> MaxNResult:
    """
    Runs the MAX^N algorithm (expansion of minimax) to determine the value of the given game state
    when it is the given player's turn.

    Returns a list of values, where each player has an entry for their value in their index in the list.

    Takes two functions over GameState:
        - one returns the value of a terminal state
        - one is a heuristic to be used for ordering or to answer immediately

    When answer_now returns True, the game state should be evaluated using the heuristic.

    :param depth: the current depth of the call stack
    :param node: the current GameState to evaluate
    :param player: the player who is currently choosing a move
    :param upper_bound: the maximum value that this player can obtain given the rest of the tree
    :param game_info: the rules that this game uses, including total players, etc.
    :param state_evaluator: collection of functions to evaluate game states
    :param answer_now: whether to use the heuristic to rapidly determine an approximate answer
    :return: a tuple with a value for every player in the game, given the state and whose turn it is
    """
    global max_n_total_nodes
    max_n_total_nodes += 1
    if max_n_total_nodes % 1000 == 0:
        LOGGER.info(f"Processed {max_n_total_nodes} nodes")
    if node.is_terminal():
        return MaxNResult(node, state_evaluator.terminal_state_value(node, game_info))
    if answer_now(depth):
        return MaxNResult(node, state_evaluator.heuristic(node, game_info))

    children = node.children()
    next_player_index = (player + 1) % game_info.total_players
    best = max_n(
        children[0],
        next_player_index,
        game_info.max_value,
        game_info,
        state_evaluator,
        depth + 1,
        answer_now,
    )
    for i, child in enumerate(children[1:]):
        if best.values[player] >= upper_bound:
            LOGGER.info(f"Pruned {i} at depth {depth}")
            return best
        current = max_n(
            child,
            next_player_index,
            game_info.max_value - best.values[player],
            game_info,
            state_evaluator,
            depth + 1,
            answer_now,
        )
        if current.values[player] > best.values[player]:
            best = current
    return best
