import logging

import time

import pickle
from requests_html import HTMLSession

from espn.basketball.basketball_stat import BasketballStat
from stats import Stats

LOGGER = logging.getLogger("fantasysp.api")


class FantasySPApi:
    def __init__(self):
        self.cache = None

    def page(self):
        if self.cache is not None:
            LOGGER.info("Using cached page")
            return self.cache

        start_time = time.time()
        LOGGER.info("Fetching daily projections page from FantasySP")

        session = HTMLSession()
        r = session.get("https://www.fantasysp.com/projections/basketball/daily/")
        LOGGER.info(f"Rendering after {time.time() - start_time:.3f} seconds")
        r.html.render(timeout=20)
        # print(r.cookies)
        #
        # r = requests.post("https://www.fantasysp.com/a_fsp_main.php",
        #                   data="ajax-load=free-projections-ajax&sport=nba&thetype=daily&position=&tehdesc=basketball&ppr=",
        #                   cookies=r.cookies)
        #
        #
        # "crisp-client%2Fsession%2F4a077e48-707b-4d40-ac54-5223bb3c8950"
        # "session_5050d2ec-2399-45e0-b263-7c32a83fc684"

        LOGGER.info(f"Finished after {time.time() - start_time:.3f} seconds")
        self.cache = r.html
        return r.html

    def table(self):
        page = self.page()

        return next(filter(lambda elt: "sortable" in elt.attrs.get("class", list()), page.find("table")))

    def rows(self):
        table = self.table()
        return filter(lambda elt: "projection-player" in elt.attrs.get("class", list()), table.find("tr"))

    def players(self):
        return list(map(FantasySPApi.row_to_player, self.rows()))

    td_class_to_stat = {
        "proj-minutes": BasketballStat.MINUTES,
        "proj-ppg": BasketballStat.POINTS,
        "proj-ast": BasketballStat.ASSISTS,
        "proj-reb": BasketballStat.REBOUNDS,
        "proj-stl": BasketballStat.STEALS,
        "proj-blk": BasketballStat.BLOCKS,
        "proj-to": BasketballStat.TURNOVERS,
        "proj-threepm": BasketballStat.THREES,
        "proj-ftm": BasketballStat.FTM,
        "proj-ftper": BasketballStat.FTPCT,
        "proj-twopm": BasketballStat.TWOS,
        "proj-fgper": BasketballStat.FGPCT,
    }

    @staticmethod
    def row_to_player(row):
        name = row.find("a")[0].text
        tds = row.find("td")
        s = Stats({}, BasketballStat)
        for td in tds:
            for cls in td.attrs.get("class", []):
                stat = FantasySPApi.td_class_to_stat.get(cls)
                if stat:
                    s.stat_dict[stat] = float(td.text)
        return PlayerProjection(name, s)


class PlayerProjection:
    def __init__(self, name, stats):
        self.stats = stats
        self.name = name
