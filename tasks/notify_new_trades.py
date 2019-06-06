import logging
from pathlib import Path

from config import team_reader, password_reader, notifier_config
from espn.espn_api import EspnApi
from espn import trade_finder
from espn.trade_store import TradeStore
from tasks.task import Task

LOGGER = logging.getLogger("tasks.notify_new_trades")


class NotifyNewTrades(Task):

    def __init__(self, username, password, configs, notifier):
        self.username = username
        self.password = password
        self.configs = configs
        self.notifier = notifier

    @staticmethod
    def create(username):
        password = password_reader.password(username, Path.cwd() / "config/passwords")
        configs = team_reader.all_teams(Path.cwd() / "config/team_configs")
        notifier = notifier_config.current_notifier(username)
        return NotifyNewTrades(username, password, configs, notifier)

    def run(self):
        for config in self.configs:
            self.check_for_trades(config)

    def check_for_trades(self, config):
        LOGGER.info(f"searching for new trades in league {config.league_id}")
        espn = EspnApi(self.username, self.password, config.league_id, config.team_id)
        trade_store = TradeStore(config.league_id)
        cur_trades = trade_finder.all_current_trades(espn)
        stored_trades = trade_store.retrieve_trades()
        if cur_trades != stored_trades:
            self.notify_new(stored_trades, cur_trades)
            LOGGER.info(f"new trades found in league {config.league_id}")
            trade_store.store_trades(cur_trades)
        else:
            LOGGER.info(f"no new trades found in league {config.league_id}")

    def notify_new(self, old_trades, new_trades):
        """
        Notifies the notifier of each trade that appears in the new trades, but not
        the old trades.
        :param set old_trades: the set of trades that used to be current
        :param set new_trades: the set of trades that is now current
        """
        for trade in new_trades - old_trades:
            self.notifier.notify_new_trade(trade)
