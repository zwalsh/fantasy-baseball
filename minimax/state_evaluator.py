from minimax.game_info import GameInfo
from minimax.game_state import GameState


class StateEvaluator:
    def heuristic(self, game_state: GameState, game_info: GameInfo):
        pass

    def terminal_state_value(self, game_state: GameState, game_info: GameInfo):
        pass
