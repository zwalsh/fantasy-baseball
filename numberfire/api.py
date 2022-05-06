import logging

from datetime import date
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from dump import load_from_cache
from espn.baseball.baseball_stat import BaseballStat
from stats import Stats
from timing.timed import timed

LOGGER = logging.getLogger("numberfire.api")


class PlayerProjection:
    def __init__(self, name, fp, mins, pts, reb, ast, stl, blk, to):
        self.to = to
        self.blk = blk
        self.stl = stl
        self.ast = ast
        self.reb = reb
        self.pts = pts
        self.mins = mins
        self.fp = fp
        self.name = name

    def __str__(self):
        return (
            f"{self.name:<30}min:{float(self.mins):.1f}  "
            f"fp:{float(self.fp):.1f}  pts:{float(self.pts):.1f}"
        )


# Maps names as returned from numberfire to the espn equivalent
NF_NAMES_TO_ESPN_NAMES = {
    'C.J. McCollum': 'CJ McCollum'
}


class NumberFireApiException(Exception):
    """
    Raise this exception when something unexpected happens with the NumberFire API
    """
    pass


class NumberFireApi:

    def __init__(self):
        self._cache_dir = Path("cache/numberfire/")
        if not self._cache_dir.exists():
            self._cache_dir.mkdir()

        # use a session to store cookies that affect the returned projections
        self._session = requests.Session()

    baseball_url = "https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections/batters"

    def _cache_key(self, sport):
        today = date.today()
        date_string = str(today)
        sport_dir = self._cache_dir / sport
        if not sport_dir.exists():
            sport_dir.mkdir()
        return sport_dir / f"{date_string}.p"

    @timed(LOGGER)
    def _page(self, projections_url):
        """
        Gets the daily fantasy projections page from NumberFire
        :return BeautifulSoup: the html on the page
        """
        r = self._session.get(projections_url)
        return BeautifulSoup(r.content)

    def _get_dropdown_option(self, input_option_key, option_matcher):
        """
        Gets a data-value for a particular option based on the input and some matcher.
        :param input_option_key:
        :param option_matcher:
        :return:
        """
        inputs = self._page(self.baseball_url).find_all("input")
        site_picker_input = next(
            filter(
                lambda i: i.get('data-option-key', '') == input_option_key,
                inputs
            )
        )
        options = site_picker_input.find_next_sibling("ul").find_all("li")
        matched_option = next(
            filter(
                lambda li: option_matcher in li.text,
                options
            )
        )
        return matched_option['data-value']

    def get_yahoo_dfs_site_id(self) -> int:
        LOGGER.info("Getting Yahoo site id")
        site_id = self._get_dropdown_option(input_option_key='site', option_matcher='Yahoo')
        LOGGER.info(f"Yahoo site id is {site_id}")
        return site_id

    def _get_fd_all_day_slate_id(self) -> int:
        # NumberFire has "slates" of available players
        # we want the 'All Day' slate, but...
        # The slate id for the 'All Day' slate changes every day
        LOGGER.info("Getting FanDuel 'All Day' slate id from numberfire")
        all_day_slate = self._get_dropdown_option('slate_id', 'All Day')
        LOGGER.info(f"All Day slate id is {all_day_slate}")
        return all_day_slate

    def _get_yahoo_all_day_slate_id(self) -> int:
        LOGGER.info("Getting the 'SAME_DAY' slate id for yahoo from Numberfire.")
        slate_id = self._get_dropdown_option('slate_id', 'SAME_DAY')
        LOGGER.info(f"Yahoo SAME_DAY slate_id is {slate_id}")
        return slate_id

    def _set_slate(self, slate_id):
        form_data = {
            'slate_id': slate_id
        }
        self._session.post("https://www.numberfire.com/mlb/daily-fantasy/set-slate", data=form_data)

    def _set_site(self, site_id):
        form_data = {
            'site': site_id
        }
        self._session.post("https://www.numberfire.com/mlb/daily-fantasy/set-dfs-site",
                           data=form_data)

    @staticmethod
    def _projections_table(page):
        table_bodies = page.find_all("tbody")
        return next(
            filter(
                lambda tbody: tbody.has_attr("class") and "stat-table__body" in tbody["class"],
                table_bodies,
            )
        )

    @staticmethod
    def row_to_projection_basketball(row):
        links = row.find_all("a")
        tds = row.find_all("td")
        name = NumberFireApi.find_with_class(links, "full")
        fp = float(NumberFireApi.find_with_class(tds, "fp"))
        mins = NumberFireApi.find_with_class(tds, "min")
        pts = NumberFireApi.find_with_class(tds, "pts")
        reb = NumberFireApi.find_with_class(tds, "reb")
        ast = NumberFireApi.find_with_class(tds, "ast")
        stl = NumberFireApi.find_with_class(tds, "stl")
        blk = NumberFireApi.find_with_class(tds, "blk")
        to = NumberFireApi.find_with_class(tds, "to")
        return PlayerProjection(name, fp, mins, pts, reb, ast, stl, blk, to)

    @staticmethod
    def row_to_projection_baseball(row) -> (str, Stats):
        links = row.find_all("a")
        tds = row.find_all("td")
        name = NumberFireApi.find_with_class(links, "full")

        plate_appearances = float(NumberFireApi.find_with_class(tds, "pa"))
        walks = float(NumberFireApi.find_with_class(tds, "bb"))
        singles = float(NumberFireApi.find_with_class(tds, "1b"))
        doubles = float(NumberFireApi.find_with_class(tds, "2b"))
        triples = float(NumberFireApi.find_with_class(tds, "3b"))
        homers = float(NumberFireApi.find_with_class(tds, "hr"))
        hits = singles + doubles + triples + homers
        at_bats = plate_appearances - walks

        projection_dict = {
            BaseballStat.PA: plate_appearances,
            BaseballStat.BB: walks,
            BaseballStat.AB: at_bats,
            BaseballStat.H: hits,
            BaseballStat.HR: homers,
            BaseballStat.R: float(NumberFireApi.find_with_class(tds, "r")),
            BaseballStat.RBI: float(NumberFireApi.find_with_class(tds, "rbi")),
            BaseballStat.SB: float(NumberFireApi.find_with_class(tds, "sb"))
        }

        return name, Stats(projection_dict, BaseballStat)

    @staticmethod
    def find_with_class(elt, target_class):
        return next(
            filter(lambda a: a.has_attr("class") and target_class in a["class"], elt)
        ).text.strip()

    def projections(self) -> List[PlayerProjection]:
        """
        Returns a list of PlayerProjections for today's slate of games
        :return list: projections for each player with a game today
        """
        basketball_url = "http://www.numberfire.com/nba/fantasy/full-fantasy-basketball-projections"
        basketball_page = self._page(basketball_url)
        return list(
            map(
                NumberFireApi.row_to_projection_basketball,
                self._projections_table(basketball_page).find_all("tr")
            )
        )

    def player_to_points(self) -> Dict[str, float]:
        return {
            NF_NAMES_TO_ESPN_NAMES.get(projection.name, projection.name): projection.fp
            for projection in self.projections()
        }

    def _get_hitter_projections_from_current_page(self) -> Dict[str, Stats]:
        projections_rows = self._projections_table(self._page(self.baseball_url)).find_all("tr")
        if len(projections_rows) == 0:
            message = "Attempting to find projections from NumberFire and found none."
            raise NumberFireApiException(message)

        LOGGER.info(f"Found {len(projections_rows)} hitter projections.")
        return {
            name: stats for name, stats in
            map(NumberFireApi.row_to_projection_baseball, projections_rows)
        }

    def _baseball_hitter_projections_yahoo(self) -> Dict[str, Stats]:
        yahoo_site_id = self.get_yahoo_dfs_site_id()
        self._set_site(yahoo_site_id)
        all_day_slate_id = self._get_yahoo_all_day_slate_id()
        self._set_slate(all_day_slate_id)
        return self._get_hitter_projections_from_current_page()

    def _baseball_hitter_projections_fanduel(self) -> Dict[str, Stats]:
        self._set_slate(self._get_fd_all_day_slate_id())
        return self._get_hitter_projections_from_current_page()

    def _baseball_hitter_projections(self) -> Dict[str, Stats]:
        try:
            return self._baseball_hitter_projections_fanduel()
        # pylint: disable=broad-except
        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error("Failed to get Fanduel projections - falling back to Yahoo projections")
        try:
            return self._baseball_hitter_projections_yahoo()
        # pylint: disable=broad-except
        except Exception as e:
            LOGGER.exception(e)
            LOGGER.error("Failed to get Yahoo projections - no further fallbacks")
            raise e

    def baseball_hitter_projections(self) -> Dict[str, Stats]:
        projections = load_from_cache(
            self._cache_key("baseball"),
            self._baseball_hitter_projections
        )
        return projections
