import datetime
import logging
from pathlib import Path

LOGGER = logging.getLogger("fangraphs.metrics")


class FangraphsMetrics:
    @staticmethod
    def last_update_file():
        """
        The Path to the file that stores the last-updated times for the Fangraphs projections.
        Each line in this file is a time that the projections were updated, in standard format
        (as seen when printing a datetime object)
        :return Path: the path to the last-updated metrics file
        """
        updated = Path("fangraphs/updated.txt")
        if not (updated.exists() and updated.is_file()):
            LOGGER.info("last update file does not exist, creating it now")
            f = updated.open("w+")
            f.close()
        return updated

    @staticmethod
    def last_seen_update():
        """
        Returns the datetime of the last update that was recorded.

        :return datetime: the datetime of the last update, or None if there have been none recorded
        """
        f = FangraphsMetrics.last_update_file()
        text = f.read_text()
        lines = text.splitlines()
        if len(lines) == 0:
            return None
        last = lines[len(lines) - 1]
        return datetime.datetime.strptime(last, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def record_update(update):
        """
        Stores the update event on disk.
        :param datetime update: the update timestamp to record
        """
        f = FangraphsMetrics.last_update_file()
        LOGGER.info(f"writing Fangraphs projections update {update} to disk")
        fo = f.open("a")
        fo.write(str(update) + "\n")
