import logging
from pathlib import Path

from config import password_reader, team_reader
from espn.baseball.baseball_api import BaseballApi
from tasks.archive_daily_stats import ArchiveDailyStats
from tasks.task import Task

LOGGER = logging.getLogger("tasks.archive_year_stats")


class ArchiveYearlyStats(Task):
    def __init__(self, username, password, configs, cur_period):
        self.username = username
        self.all_days = [
            ArchiveDailyStats(username, password, configs, pd)
            for pd in range(0, cur_period)
        ]

    def run(self):
        for day in self.all_days:
            day.execute()

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs/baseball")
        scoring_period = (
            BaseballApi.Builder()
            .username(username)
            .password(password)
            .league_id(configs[0].league_id)
            .team_id(configs[0].team_id)
            .build()
            .scoring_period()
            - 1
        )
        return ArchiveYearlyStats(username, password, configs, scoring_period)
