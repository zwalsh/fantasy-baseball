from enum import Enum


class FootballSlot(Enum):
    BENCH = "BE"
    INJURED = "IR"

    @staticmethod
    def starting_slots():
        return {ls for ls in FootballSlot} - {FootballSlot.BENCH, FootballSlot.INJURED}
