class ProTeamGame:
    """
    Represents a real, professional game between two teams
    """

    def __init__(self, home_team: int, away_team: int, game_id: int):
        self.home_team = home_team
        self.away_team = away_team
        self.game_id = game_id
