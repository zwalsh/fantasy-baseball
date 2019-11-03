import logging
import re
from pathlib import Path

import pickle

LOGGER = logging.getLogger("espn.stat_store")


class StatStore:

    def __init__(self, league_id, year):
        """
        Interface to a store of stats on disk for an ESPN league in a given year.

        Stats are Stats objects, pickled and stored in the following format:

        /espn/{year}/{league_id}/{team_id}/{scoring-period}-stats.p

        :param int league_id: the league that this Store accesses
        :param int year: the year that this StatStore is working in
        """
        self.league_id = league_id
        self.year = year
        self.stat_cache = {}

    @staticmethod
    def check_dir(path):
        """
        Checks that the given Path is an existing directory, creating it if necessary.
        :param Path path: the path that should be a directory
        :return Path: the created directory
        """
        if not (path.exists() and path.is_dir()):
            LOGGER.info(f"{path} does not exist, creating it now")
            path.mkdir()
        return path

    def stat_dir(self, team_id):
        """
        Returns the Path to the directory containing stats for the given team in this store.

        Guaranteed to be an existing directory after this call.
        :param int team_id: returns the directory for this team.
        :return Path: the Path to this team's stats
        """
        stats_home = self.check_dir(Path("espn/stats"))
        year_dir = self.check_dir(stats_home / str(self.year))
        league_dir = self.check_dir(year_dir / str(self.league_id))
        team_dir = self.check_dir(league_dir / str(team_id))
        return team_dir

    def check_cache(self, file_name):
        return self.stat_cache.get(file_name)

    def retrieve_stats(self, team_id):
        """
        Retrieves all stored stats for the given team, returning them as a dictionary
        keyed by scoring period.
        :param int team_id: the team for which to retrieve stats
        :return dict: a dictionary mapping scoring period to Stats
        """
        all_stats = dict()
        team_stat_dir = self.stat_dir(team_id)
        for file in team_stat_dir.iterdir():
            file_name = file.parts[-1]
            match = re.search("([0-9]*)-stats.p", file_name)
            scoring_period = int(match.group(1))

            cached = self.stat_cache.get(str(file))
            if cached:
                LOGGER.info(f"using cached stats for {file}")
                all_stats[scoring_period] = cached
            else:
                LOGGER.info(f"unpickling stats located at {file}")
                unpickled_stats = pickle.load(file.open("rb"))
                self.stat_cache[str(file)] = unpickled_stats
                all_stats[scoring_period] = unpickled_stats
        return all_stats

    def store_stats(self, stats, team_id, scoring_period):
        """
        Stores the given Stats for the team with the given scoring period, pickling the Stats
        object and placing it on disk at the location indicated by the given info.

        Overwrites any existing Stats.
        :param Stats stats: the Stats to write to disk
        :param int team_id: the team to store the stats for
        :param int scoring_period: the scoring period that these Stats occurred in
        """
        team_stats_dir = self.stat_dir(team_id)
        file_name = f"{scoring_period}-stats.p"
        stats_file = team_stats_dir / file_name
        LOGGER.info(f"storing stats in file {file_name}")
        stats_file.write_bytes(pickle.dumps(stats))
