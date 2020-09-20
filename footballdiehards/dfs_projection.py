from espn.football.football_position import FootballPosition


class DFSProjection:

    def __init__(self, player: str, position: FootballPosition, salary: int, projection: float):
        self.player = player
        self.position = position
        self.salary = salary
        self.projection = projection

    def value(self):
        return self.projection * 1000 / self.salary

    def __str__(self):
        return f"{self.player:<30} {self.projection:.1f} {self.salary:<5} {self.value():.2f}"
