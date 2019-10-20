from enum import Enum


class BaseballSlot(Enum):
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
    def starting_slots():
        return {ls for ls in BaseballSlot} - {BaseballSlot.BENCH, BaseballSlot.INJURED}

    @staticmethod
    def hitting_slots():
        return {BaseballSlot.CATCHER,
                BaseballSlot.FIRST,
                BaseballSlot.SECOND,
                BaseballSlot.THIRD,
                BaseballSlot.SHORT,
                BaseballSlot.MIDDLE_INFIELD,
                BaseballSlot.CORNER_INFIELD,
                BaseballSlot.OUTFIELD,
                BaseballSlot.UTIL}

    @staticmethod
    def catcher():
        return {BaseballSlot.CATCHER, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def first():
        return {BaseballSlot.FIRST, BaseballSlot.CORNER_INFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def second():
        return {BaseballSlot.SECOND, BaseballSlot.MIDDLE_INFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def third():
        return {BaseballSlot.THIRD, BaseballSlot.CORNER_INFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def short():
        return {BaseballSlot.SHORT, BaseballSlot.MIDDLE_INFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def outfield():
        return {BaseballSlot.OUTFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def pitcher():
        return {BaseballSlot.PITCHER, BaseballSlot.BENCH}
