import logging

import time
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

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


class NumberFireApi:
    def page(self):
        """
        Gets the daily fantasy projections page from NumberFire
        :return BeautifulSoup: the html on the page
        """
        start_time = time.time()
        LOGGER.info("Fetching daily projections page from Numberfire")
        r = requests.get(
            "http://www.numberfire.com/nba/fantasy/full-fantasy-basketball-projections"
        )
        LOGGER.info(f"Finished after {time.time() - start_time:.3f} seconds")
        return BeautifulSoup(r.content)

    def projections_table(self):
        table_bodies = self.page().find_all("tbody")
        return next(
            filter(
                lambda tbody: tbody.has_attr("class")
                              and "stat-table__body" in tbody["class"],
                table_bodies,
            )
        )

    @staticmethod
    def row_to_projection(row):
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
    def find_with_class(elt, target_class):
        return next(
            filter(lambda a: a.has_attr("class") and target_class in a["class"], elt)
        ).text.strip()

    def projections(self) -> List[PlayerProjection]:
        """
        Returns a list of PlayerProjections for today's slate of games
        :return list: projections for each player with a game today
        """
        return list(
            map(
                NumberFireApi.row_to_projection, self.projections_table().find_all("tr")
            )
        )

    def player_to_points(self) -> Dict[str, float]:
        return {
            NF_NAMES_TO_ESPN_NAMES.get(projection.name, projection.name): projection.fp
            for projection in self.projections()
        }
