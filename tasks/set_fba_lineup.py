import logging
from pathlib import Path

from config import password_reader, team_reader, notifier_config
from espn.basketball.basketball_api import BasketballApi
from fantasysp.api import FantasySPApi
from numberfire.api import NumberFireApi
from optimize.optimize_fp import optimize_fp, player_to_fp
from tasks.task import Task

LOGGER = logging.getLogger("tasks.set_fba_lineup")

USE_NF = True


class SetFbaLineup(Task):
    def __init__(self, username, password, configs, notifier, fantasysp, numberfire: NumberFireApi,
                 year=2022):
        super().__init__(username)
        self.password = password
        self.configs = configs
        self.notifier = notifier
        self.fantasysp = fantasysp
        self.numberfire = numberfire
        self.year = year

    def run(self):
        for team_config in self.configs:
            LOGGER.info(
                f"setting lineup for team {team_config.team_id} in league {team_config.league_id}"
            )

            espn = (
                BasketballApi.Builder()
                    .username(self.username)
                    .password(self.password)
                    .league_id(team_config.league_id)
                    .team_id(team_config.team_id)
                    .year(self.year)
                    .build()
            )
            if USE_NF:
                nf_projections = self.numberfire.projections()
                player_to_points = {pp.name: pp.fp for pp in nf_projections}
            else:
                player_to_points = player_to_fp(self.fantasysp, espn)
            optimize_fp(espn, player_to_points, self.notifier)

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs/basketball")
        notifier = notifier_config.current_notifier(username)
        return SetFbaLineup(username, password, configs, notifier, FantasySPApi())
