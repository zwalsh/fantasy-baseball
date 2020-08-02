from typing import List
from unittest import TestCase

from minimax.game_info import GameInfo
from minimax.game_state import GameState
from minimax.max_n import max_n
from minimax.state_evaluator import StateEvaluator


class BasicGame(GameState):
    def __init__(self, values, children):
        super().__init__()
        self.values = values
        self.children_list = children

    def children(self) -> List["GameState"]:
        return self.children_list

    def is_terminal(self) -> bool:
        return len(self.children()) == 0


class BasicStateEvaluator(StateEvaluator):
    def heuristic(self, game_state: BasicGame, game_info: GameInfo):
        return game_state.values

    def terminal_state_value(self, game_state: BasicGame, game_info: GameInfo):
        return game_state.values


class ExplodingGame(GameState):
    def children(self) -> List["GameState"]:
        raise ValueError

    def is_terminal(self) -> bool:
        raise ValueError


"""
example from: https://www.cc.gatech.edu/~thad/6601-gradAI-fall2015/Korf_Multi-player-Alpha-beta-Pruning.pdf
example tree, one layer per player 0, 1, 2
                        a
            b           f           h
        c   d   e     g x x       i x x
"""
state_x = ExplodingGame()

# bottom layer - player 2's choice
state_c = BasicGame([3, 3, 3], [])
state_d = BasicGame([4, 2, 3], [])
state_e = BasicGame([3, 1, 5], [])

state_g = BasicGame([1, 7, 1], [])

state_i = BasicGame([1, 6, 2], [])

# middle layer - player 1's choice
state_b = BasicGame(
    [], [state_c, state_d, state_e]
)  # effective values = [3,3,3] from c
state_f = BasicGame(
    [], [state_g, state_x, state_x]
)  # effective values = [1,7,1] from g, state_x pruned
state_h = BasicGame(
    [], [state_i, state_x, state_x]
)  # effective values = [1,6,2] from i, state_x pruned

# top layer - player 0's choice
state_a = BasicGame(
    [], [state_b, state_f, state_h]
)  # effective values = [3,3,3] from b


class Test(TestCase):
    game_info = GameInfo(3, 9)
    state_evaluator = BasicStateEvaluator()

    def test_max_n_no_children(self):
        vals_c = max_n(state_c, 2, 9, self.game_info, self.state_evaluator, 0).values
        self.assertEqual(state_c.values, vals_c)
        vals_g = max_n(state_g, 2, 9, self.game_info, self.state_evaluator, 0).values
        self.assertEqual(state_g.values, vals_g)
        vals_i = max_n(state_i, 2, 9, self.game_info, self.state_evaluator, 0).values
        self.assertEqual(state_i.values, vals_i)

    def test_max_n_no_prune(self):
        vals_b = max_n(state_b, 1, 9, self.game_info, self.state_evaluator, 0).values
        self.assertEqual([3, 3, 3], vals_b)

    def test_max_n_pruning(self):
        # f should stop evaluating after the first child, where 7 (from state_g) >= 6 (upper bound)
        vals_f = max_n(state_f, 1, 6, self.game_info, self.state_evaluator, 0).values
        self.assertEqual([1, 7, 1], vals_f)

    def test_max_n_prune_from_top(self):
        # f and h should both prune based on the values from b
        vals_a = max_n(state_a, 0, 9, self.game_info, self.state_evaluator, 0).values
        self.assertEqual([3, 3, 3], vals_a)

    def test_uses_heuristic(self):
        vals_a = max_n(
            state_a, 0, 9, self.game_info, self.state_evaluator, 0, lambda x: True
        ).values
        self.assertEqual([], vals_a)
