import logging
import pickle
from datetime import date
from pathlib import Path
from typing import Dict, List

from requests_html import HTMLSession

from espn.baseball.baseball_stat import BaseballStat
from espn.football.football_position import FootballPosition
from espn.football.football_stat import FootballStat
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
        page = self.page(url)
        data_table = page.find("tbody", first=True)
        return data_table.find("tr")

    @staticmethod
    def name_from_row(row):
        links = row.find("a")
        player_name_link = next(
            filter(lambda a: "player-name" in a.attrs.get("class", []), links), None
        )
        return player_name_link.text if player_name_link is not None else None

    @staticmethod
    def _rank_from_row(row) -> int:
        # overall rank is in the third td element
        cells = row.find("td")
        rank_cell = cells[2]
        return int(rank_cell.text) if rank_cell is not None and rank_cell.text != '' else None

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

    def _hitter_draft_rankings(self):
        return self._baseball_draft_rankings("https://www.fantasypros.com/mlb/rankings/hitters.php?eligibility=E")

    def _pitcher_draft_rankings(self):
        return self._baseball_draft_rankings("https://www.fantasypros.com/mlb/rankings/pitchers.php?eligibility=E")

    def _baseball_draft_rankings(self, url) -> Dict[str, int]:
        """

        :return: map of name to overall rank
        """
        rows = self.table_rows(url)
        rankings = filter(
            lambda r: True,
            rows
        )

        name_to_overall = dict()
        for row in rankings:
            player_name = self.name_from_row(row)
            rank = self._rank_from_row(row)
            if rank is not None:
                name_to_overall[player_name] = rank

        return name_to_overall

    def baseball_draft_rankings(self) -> List[str]:
        pitcher_rankings = self._pitcher_draft_rankings()
        hitter_rankings = self._hitter_draft_rankings()

        combined_rankings = {}
        combined_rankings.update(pitcher_rankings)
        combined_rankings.update(hitter_rankings)

        top_300 = filter(lambda p: p[1] <= 300, combined_rankings.items())

        top_300_sorted = sorted(list(top_300), key=lambda p: p[1])

        return list(map(lambda p: p[0], top_300_sorted))


    def _qb_stats_for_row(self, row):
        cells = row.find("td")
        return Stats(
            {
                FootballStat.YDS_PASS: float(cells[3].text.replace(",", "")),
                FootballStat.TD_PASS: float(cells[4].text),
                FootballStat.INT_PASS: float(cells[5].text),
                FootballStat.YDS_RUSH: float(cells[7].text),
                FootballStat.TD_RUSH: float(cells[8].text),
                FootballStat.FUML: float(cells[9].text),
                FootballStat.FP: float(cells[10].text),
            },
            FootballStat,
        )

    def _rb_stats_for_row(self, row):
        cells = row.find("td")
        return Stats(
            {
                FootballStat.YDS_RUSH: float(cells[2].text.replace(",", "")),
                FootballStat.TD_RUSH: float(cells[3].text),
                FootballStat.REC: float(cells[4].text),
                FootballStat.YDS_REC: float(cells[5].text.replace(",", "")),
                FootballStat.TD_REC: float(cells[6].text),
                FootballStat.FUML: float(cells[7].text),
                FootballStat.FP: float(cells[8].text),
            },
            FootballStat,
        )

    def _wr_stats_for_row(self, row):
        cells = row.find("td")
        return Stats(
            {
                FootballStat.REC: float(cells[1].text),
                FootballStat.YDS_REC: float(cells[2].text.replace(",", "")),
                FootballStat.TD_REC: float(cells[3].text),
                FootballStat.YDS_RUSH: float(cells[5].text.replace(",", "")),
                FootballStat.TD_RUSH: float(cells[6].text),
                FootballStat.FUML: float(cells[7].text),
                FootballStat.FP: float(cells[8].text),
            },
            FootballStat,
        )

    def _te_stats_for_row(self, row):
        cells = row.find("td")
        return Stats(
            {
                FootballStat.REC: float(cells[1].text),
                FootballStat.YDS_REC: float(cells[2].text.replace(",", "")),
                FootballStat.TD_REC: float(cells[3].text),
                FootballStat.FUML: float(cells[4].text),
                FootballStat.FP: float(cells[5].text),
            },
            FootballStat,
        )

    def _dst_stats_for_row(self, row):
        cells = row.find("td")
        return Stats({FootballStat.FP: float(cells[9].text)}, FootballStat)

    def _fb_player_stats_from_row(self, row, position):
        # pylint: disable=unnecessary-lambda
        return {
            FootballPosition.QUARTER_BACK: lambda r: self._qb_stats_for_row(r),
            FootballPosition.RUNNING_BACK: lambda r: self._rb_stats_for_row(r),
            FootballPosition.WIDE_RECEIVER: lambda r: self._wr_stats_for_row(r),
            FootballPosition.TIGHT_END: lambda r: self._te_stats_for_row(r),
            FootballPosition.DEFENSE: lambda r: self._dst_stats_for_row(r),
        }[position](row)

    def _week_football_projections(
        self, position: FootballPosition
    ) -> Dict[str, Stats]:
        """
        Grabs projections for the week for the given position.

        GETs the URL below, substituting in position_str, and scrapes the rows.

        https://www.fantasypros.com/nfl/projections/<position_str>.php

        :param position_str: the position for which to load the page and get stats.
        :return: dictionary of name to Stat
        """
        projections = dict()
        rows = self.table_rows(
            f"https://www.fantasypros.com/nfl/projections/{str(position).lower()}.php?scoring=HALF"
        )
        players = [r for r in rows if "mpb-player" in r.attrs.get("class", [""])[0]]
        for p in players:
            name = FantasyProsApi.name_from_row(p)
            proj = self._fb_player_stats_from_row(p, position)
            projections[name] = proj
        return projections

    def week_football_projections(self) -> Dict[str, Stats]:
        """
        Scrapes the weekly projections pages at FantasyPros to get the best projections for
        players at all projections.
        :return: dictionary of all players' names to projected stats
        """
        projections = dict()
        for position in FootballPosition:
            projections.update(self._week_football_projections(position))
        return projections
