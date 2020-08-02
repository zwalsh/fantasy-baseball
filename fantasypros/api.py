import logging
import pickle
from datetime import date
from pathlib import Path

from requests_html import HTMLSession

from espn.baseball.baseball_stat import BaseballStat
from stats import Stats
from timing.timed import timed

LOGGER = logging.getLogger("fantasypros.api")


class FantasyProsApi:
    def __init__(self):
        pass

    @staticmethod
    def _path_segment(url):
        if "hitters" in url:
            return "hitters"
        if "pitchers" in url:
            return "pitchers"
        return None

    @timed(LOGGER)
    def page(self, url):
        session = HTMLSession()
        r = session.get(url)
        return r.html

    def table_rows(self, url):
        return self.page(url).find("#data", first=True).find("tr")

    @staticmethod
    def name_from_row(row):
        links = row.find("a")
        player_name_link = next(
            filter(lambda a: "player-name" in a.attrs.get("class", []), links), None
        )
        return player_name_link.text if player_name_link is not None else None

    @staticmethod
    def hitter_stats_from_row(row):
        cells = row.find("td")
        stats_dict = {
            BaseballStat.AB: int(cells[1].text),
            BaseballStat.R: int(cells[2].text),
            BaseballStat.HR: int(cells[3].text),
            BaseballStat.RBI: int(cells[4].text),
            BaseballStat.SB: int(cells[5].text),
            BaseballStat.H: int(cells[8].text),
            BaseballStat.BB: int(cells[11].text),
        }
        # approximate plate appearances as at-bats plus walks
        stats_dict[BaseballStat.PA] = (
            stats_dict[BaseballStat.AB] + stats_dict[BaseballStat.BB]
        )
        return Stats(stats_dict, BaseballStat)

    @staticmethod
    def pitcher_stats_from_row(row):
        cells = row.find("td")
        stats_dict = {
            BaseballStat.OUTS: round(float(cells[1].text) * 3),
            BaseballStat.K: int(cells[2].text),
            BaseballStat.W: int(cells[3].text),
            BaseballStat.SV: int(cells[4].text),
            BaseballStat.ER: int(cells[7].text),
            BaseballStat.P_H: int(cells[8].text),
            BaseballStat.P_BB: int(cells[9].text),
        }
        return Stats(stats_dict, BaseballStat)

    def year_projections(self, url, stats_from_row):
        """
                Scrape the given url for year-long projections, converting with the given function
                :return dict: dictionary of name to Stats object
                """
        today = date.today()
        date_string = str(today)
        LOGGER.debug(f"Using date_str: {date_string}")
        cache_key = f"fantasypros/{FantasyProsApi._path_segment(url)}/{date_string}.p"
        LOGGER.debug(f"Looking in path {cache_key}")
        cache_location = Path(cache_key)
        if cache_location.exists():
            f = cache_location.open("rb")
            return pickle.load(f)

        results = {}
        for tr in self.table_rows(url):
            name = FantasyProsApi.name_from_row(tr)
            if name is None:
                continue
            stats = stats_from_row(tr)
            results[name] = stats

        f = cache_location.open("wb+")
        pickle.dump(results, f)
        return results

    def year_hitter_projections(self):
        """
        Scrape https://www.fantasypros.com/mlb/projections/hitters.php for year-long projections
        :return dict: dictionary of name to Stats object
        """
        return self.year_projections(
            "https://www.fantasypros.com/mlb/projections/hitters.php",
            FantasyProsApi.hitter_stats_from_row,
        )

    def year_pitcher_projections(self):
        return self.year_projections(
            "https://www.fantasypros.com/mlb/projections/pitchers.php",
            FantasyProsApi.pitcher_stats_from_row,
        )
