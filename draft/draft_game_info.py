from minimax.game_info import GameInfo


class DraftGameInfo(GameInfo):
    def __init__(self, total_players, max_value, lineup_settings):
        super().__init__(total_players, max_value)
        self.lineup_settings = lineup_settings
