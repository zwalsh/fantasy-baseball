from enum import Enum


class LineupSlot(Enum):
    CATCHER = "C"
    PITCHER = "P"
    FIRST = "1B"
    SECOND = "2B"
    THIRD = "3B"
    SHORT = "SS"
    OUTFIELD = "OF"
    MIDDLE_INFIELD = "2B/SS"
    CORNER_INFIELD = "1B/3B"
    UTIL = "UTIL"
    DH = "DH"
    BENCH = "BE"
    INJURED = "IL"

    def __str__(self):
        return self.value

    @staticmethod
    def catcher():
        return {LineupSlot.CATCHER, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def first():
        return {LineupSlot.FIRST, LineupSlot.CORNER_INFIELD, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def second():
        return {LineupSlot.SECOND, LineupSlot.MIDDLE_INFIELD, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def third():
        return {LineupSlot.THIRD, LineupSlot.CORNER_INFIELD, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def short():
        return {LineupSlot.SHORT, LineupSlot.MIDDLE_INFIELD, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def outfield():
        return {LineupSlot.OUTFIELD, LineupSlot.BENCH, LineupSlot.UTIL}

    @staticmethod
    def pitcher():
        return {LineupSlot.PITCHER, LineupSlot.BENCH}
