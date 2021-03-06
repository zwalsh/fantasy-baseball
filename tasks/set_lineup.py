import logging
from pathlib import Path

from config import team_reader, password_reader, notifier_config
from espn.baseball.baseball_api import BaseballApi
from fangraphs.api import FangraphsApi
from optimize.lineup_optimizer import optimize_lineup
from tasks.task import Task

LOGGER = logging.getLogger("tasks.set_lineup")


class SetLineup(Task):
    def __init__(self, username, password, configs, notifier, fangraphs):
        super().__init__(username)
        self.password = password
        self.configs = configs
        self.notifier = notifier
        self.fangraphs = fangraphs

    def run(self):
        for team_config in self.configs:
            LOGGER.info(
                f"setting lineup for team {team_config.team_id} in league {team_config.league_id}"
            )

            espn = (
                BaseballApi.Builder()
                .username(self.username)
                .password(self.password)
                .league_id(team_config.league_id)
                .team_id(team_config.team_id)
                .build()
            )
            optimize_lineup(espn, self.fangraphs, self.notifier)

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs/baseball")
        notifier = notifier_config.current_notifier(username)
        return SetLineup(username, password, configs, notifier, FangraphsApi())
