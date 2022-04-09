import logging
from pathlib import Path

from config import team_reader, password_reader, notifier_config
from espn.baseball.baseball_api import BaseballApi
from fantasypros.api import FantasyProsApi
from rankings.baseball import set_predraft_rankings
from tasks.task import Task

LOGGER = logging.getLogger("tasks.set_predraft_rankings")


class SetPredraftRankings(Task):
    """
    Use this once before the draft to import fantasypros rankings into ESPN
    """

    def __init__(self, username, password, configs, fantasypros):
        super().__init__(username)
        self.password = password
        self.configs = configs
        self.fantasypros = fantasypros

    def run(self):
        for team_config in self.configs:
            LOGGER.info(
                f"setting pre-draft rankings for team {team_config.team_id} in league {team_config.league_id}"
            )

            espn = (
                BaseballApi.Builder()
                    .username(self.username)
                    .password(self.password)
                    .league_id(team_config.league_id)
                    .team_id(team_config.team_id)
                    .build()
            )
            set_predraft_rankings(self.fantasypros, espn)

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs/baseball")
        return SetPredraftRankings(username, password, configs, FantasyProsApi())
