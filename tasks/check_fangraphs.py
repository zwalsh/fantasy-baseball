import logging

from fangraphs.api import FangraphsApi
from fangraphs.metrics import FangraphsMetrics
from tasks.task import Task

LOGGER = logging.getLogger("tasks.check_fangraphs")


class CheckFangraphs(Task):

    def __init__(self, username, fg_api, fg_metrics):
        self.username = username
        self.api = fg_api
        self.metrics = fg_metrics

    def run(self):
        """
        Downloads the current Fangraphs projections from the API, and checks their
        last-updated date. If that is more recent than the latest update, it saves
        that metric to disk.
        """
        LOGGER.info("checking Fangraphs update timestamp")
        cur_last_updated = self.api.last_updated()
        metrics_last_updated = self.metrics.last_seen_update()
        if cur_last_updated != metrics_last_updated:
            LOGGER.info(f"new time found: {cur_last_updated} old time: {metrics_last_updated}")
            self.metrics.record_update(cur_last_updated)

    @staticmethod
    def create(username):
        return CheckFangraphs(username, FangraphsApi(), FangraphsMetrics())
