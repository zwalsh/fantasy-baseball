import logging
from pathlib import Path

from config import password_reader, team_reader
from espn.espn_api import EspnApi
from espn.espn_session_provider import EspnSessionProvider
from espn.stat_store import StatStore
from tasks.task import Task

LOGGER = logging.getLogger("tasks.archive_daily_stats")


class ArchiveDailyStats(Task):

    def __init__(self, username, password, team_configs, scoring_period):
        """
        Archives the stats accumulated by all users accessible via the given ESPN API access object
        :param str username: the username of the user in the league where stats are being archived
        :param str password: the password of the user
        :param list team_configs: all the teams for which to archive stats
        :param int scoring_period: the scoring period for which to archive stats
        """
        self.username = username
        self.password = password
        self.team_configs = team_configs
        self.scoring_period = scoring_period

    def run(self):
        for cfg in self.team_configs:
            espn = EspnApi(EspnSessionProvider(self.username, self.password), cfg.league_id, cfg.team_id)
            LOGGER.info(f"archiving for league {cfg.league_id} in period {self.scoring_period}")
            self.archive(espn, cfg)

    def archive(self, espn, config):
        """
        Archives the stats found with the given EspnApi object.
        :param EspnApi espn: access to ESPN's API
        :param TeamConfig config: the config currently being used to archive
        """
        period_stats = espn.scoring_period_stats(self.scoring_period)
        LOGGER.info(f"storing {len(period_stats)} teams' stats")
        store = StatStore(config.league_id, 2019)
        for team, stats in period_stats.items():
            store.store_stats(stats, team, self.scoring_period)

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs")
        scoring_period = EspnApi(EspnSessionProvider(username, password), configs[0].league_id, configs[0].team_id).scoring_period() - 1
        return ArchiveDailyStats(username, password, configs, scoring_period)
