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

    @staticmethod
    def slot_id_to_slot():
        return {
            0: BaseballSlot.CATCHER,
            1: BaseballSlot.FIRST,
            2: BaseballSlot.SECOND,
            3: BaseballSlot.THIRD,
            4: BaseballSlot.SHORT,
            5: BaseballSlot.OUTFIELD,
            6: BaseballSlot.MIDDLE_INFIELD,
            7: BaseballSlot.CORNER_INFIELD,
            12: BaseballSlot.UTIL,
            13: BaseballSlot.PITCHER,
            16: BaseballSlot.BENCH,
            17: BaseballSlot.INJURED,
        }

    @staticmethod
    def espn_slot_to_slot(slot):
        return BaseballSlot.slot_id_to_slot().get(slot)

    def slot_id(self):
        return {v: k for k, v in BaseballSlot.slot_id_to_slot().items()}[self]

    def __str__(self):
        return self.value

    @staticmethod
    def starting_slots():
        return {ls for ls in BaseballSlot} - {BaseballSlot.BENCH, BaseballSlot.INJURED}

    @staticmethod
    def hitting_slots():
        return {
            BaseballSlot.CATCHER,
            BaseballSlot.FIRST,
            BaseballSlot.SECOND,
            BaseballSlot.THIRD,
            BaseballSlot.SHORT,
            BaseballSlot.MIDDLE_INFIELD,
            BaseballSlot.CORNER_INFIELD,
            BaseballSlot.OUTFIELD,
            BaseballSlot.UTIL,
        }

    @staticmethod
    def catcher():
        return {BaseballSlot.CATCHER, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def first():
        return {
            BaseballSlot.FIRST,
            BaseballSlot.CORNER_INFIELD,
            BaseballSlot.BENCH,
            BaseballSlot.UTIL,
        }

    @staticmethod
    def second():
        return {
            BaseballSlot.SECOND,
            BaseballSlot.MIDDLE_INFIELD,
            BaseballSlot.BENCH,
            BaseballSlot.UTIL,
        }

    @staticmethod
    def third():
        return {
            BaseballSlot.THIRD,
            BaseballSlot.CORNER_INFIELD,
            BaseballSlot.BENCH,
            BaseballSlot.UTIL,
        }

    @staticmethod
    def short():
        return {
            BaseballSlot.SHORT,
            BaseballSlot.MIDDLE_INFIELD,
            BaseballSlot.BENCH,
            BaseballSlot.UTIL,
        }

    @staticmethod
    def outfield():
        return {BaseballSlot.OUTFIELD, BaseballSlot.BENCH, BaseballSlot.UTIL}

    @staticmethod
    def pitcher():
        return {BaseballSlot.PITCHER, BaseballSlot.BENCH}

    @staticmethod
    def slot_to_slot_id(slot):
        return {v: k for k, v in BaseballSlot.slot_id_to_slot().items()}[slot]
