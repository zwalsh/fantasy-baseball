import logging
from pathlib import Path

import pickle

LOGGER = logging.getLogger("espn.trade_store")


class TradeStore:

    def __init__(self, league_id):
        """
        Interface to an underlying store of current Trades in an ESPN league.
        Stores and accesses trades for the given league id.
        """
        self.league_id = league_id

    def current_trades_path(self):
        """
        Returns the Path to the file storing trades for this league
        :return Path: the file path
        """
        trades_dir = Path("espn/trades")
        if not trades_dir.exists() or not trades_dir.is_dir():
            LOGGER.info("directory for trades does not exist, creating it now")
            trades_dir.mkdir()
        return trades_dir / f"trades-{self.league_id}.p"

    def store_trades(self, trades):
        """
        Stores the given set of trades on disk as a pickled set. Overwrites the existing
        trades, if any.
        :param set trades: the trades to store on disk for this league
        """
        trades_file = self.current_trades_path()
        fo = trades_file.open("wb")
        LOGGER.info(f"storing {len(trades)} trades on disk for league {self.league_id}")
        pickle.dump(trades, fo)

    def retrieve_trades(self):
        """
        Accesses and de-pickles the set of trades currently stored on disk for this league.
        :return set: the set of trades currently stored on disk, or None
        """
        trades_file = self.current_trades_path()
        if not trades_file.exists():
            LOGGER.info(f"no trades stored for league {self.league_id}")
            return None
        fo = trades_file.open("rb")
        return pickle.load(fo)
