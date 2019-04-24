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
