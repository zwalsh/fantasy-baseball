import logging
from pathlib import Path

from config import team_reader, password_reader, notifier_config
from espn.espn_api import EspnApi
from espn.sessions.espn_session_provider import EspnSessionProvider
from fangraphs.api import FangraphsApi
from optimize.lineup_optimizer import optimize_lineup
from tasks.task import Task

LOGGER = logging.getLogger("tasks.set_lineup")


class SetLineup(Task):

    def __init__(self, username, password, configs, notifier, fangraphs):
        self.username = username
        self.password = password
        self.configs = configs
        self.notifier = notifier
        self.fangraphs = fangraphs

    def run(self):
        for team_config in self.configs:
            LOGGER.info(f"setting lineup for team {team_config.team_id} in league {team_config.league_id}")
            espn = EspnApi(EspnSessionProvider(self.username, self.password), team_config.league_id, team_config.team_id)
            optimize_lineup(espn, self.fangraphs, self.notifier)

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs")
        notifier = notifier_config.current_notifier(username)
        return SetLineup(username, password, configs, notifier, FangraphsApi())
