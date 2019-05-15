
class EspnTeamConfig:
    def __init__(self, username, league_id, team_id):
        """
        Represents all information needed to access an ESPN fantasy team.
        :param str username: the username of the user whose team this represents
        :param int league_id: the id of the league that the team is in
        :param int team_id: the id of the team within the league
        """
        self.username = username
        self.league_id = league_id
        self.team_id = team_id

    def __str__(self):
        return "{} {} {}".format(self.username, self.league_id, self.team_id)
