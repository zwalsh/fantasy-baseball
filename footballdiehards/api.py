import logging
from typing import List

from requests_html import HTMLSession

from espn.football.football_position import position_from_text
from footballdiehards.dfs_projection import DFSProjection
from timing.timed import timed

LOGGER = logging.getLogger("footballdiehards.api")


class FbDieHardsApi:

    @timed(LOGGER)
    def page(self, url):
        session = HTMLSession()
        r = session.get(url)
        return r.html

    def players(self) -> List[DFSProjection]:
        page = self.page(
            "https://www.footballdiehards.com/fantasyfootball/dailygames/FanDuel-Salary-data.cfm"
        )
        rows = page.find('tr')
        results = []
        for r in rows[2:]:
            cells = r.find('td')
            if cells[5].text != "-":
                results.append(DFSProjection(cells[0].text,
                                             position_from_text(cells[1].text),
                                             int(cells[4].text[1:]),
                                             float(cells[5].text)))
        return results
