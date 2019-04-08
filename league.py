
class League:

    def __init__(self, teams):
        self.teams = teams

    def points(self, scoring_settings):
        """
        Calculates the total points that each team in the league has based on the given scoring settings. Sorts the output of
        each team in each category and assigns the correct number of points to the person at each position.
        :return: point values for each team, {team_id: points}
        """

        point_values = {}
        for team in self.teams:
            point_values[team.team_id] = 0.0

        for scoring_item in scoring_settings:
            team_stats = []
            for team in self.teams:
                val_for_stat = team.stats.stat_dict.get(scoring_item.stat_id)
                pair = (team.team_id, val_for_stat)
                team_stats.append(pair)

            team_stats.sort(key=lambda p: p[1], reverse=scoring_item.is_reverse)

            team_stat_values = list(map(lambda p: p[1], team_stats))
            for (team_id, val_for_stat) in team_stats:
                team_points = League.points_available_for_value(val_for_stat, team_stat_values)
                point_values[team_id] += team_points

        return point_values

    @staticmethod
    def points_available_for_value(value, values):
        points = 0.0
        split = 0
        for i in range(0, len(values)):
            if values[i] == value:
                points += i + 1
                split += 1
        return points / split
