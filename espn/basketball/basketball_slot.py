from enum import Enum


class BasketballSlot(Enum):
    POINT_GUARD = "PG"
    SHOOTING_GUARD = "SG"
    SMALL_FORWARD = "SF"
    POWER_FORWARD = "PF"
    CENTER = "C"
    GUARD = "G"
    FORWARD = "F"
    UTIL = "UTIL"
    BENCH = "BE"
    INJURED = "INJ"

    def __str__(self):
        return self.value

    @staticmethod
    def slot_id_to_slot_map():
        return {
            0: BasketballSlot.POINT_GUARD,
            1: BasketballSlot.SHOOTING_GUARD,
            2: BasketballSlot.SMALL_FORWARD,
            3: BasketballSlot.POWER_FORWARD,
            4: BasketballSlot.CENTER,
            5: BasketballSlot.GUARD,
            6: BasketballSlot.FORWARD,
            11: BasketballSlot.UTIL,
            12: BasketballSlot.BENCH,
        }

    @staticmethod
    def starting_slots():
        return {ls for ls in BasketballSlot} - {
            BasketballSlot.BENCH,
            BasketballSlot.INJURED,
        }

    @staticmethod
    def espn_slot_to_slot(slot_id):
        return BasketballSlot.slot_id_to_slot_map().get(slot_id)

    @staticmethod
    def slot_to_slot_id(slot):
        return {v: k for k, v in BasketballSlot.slot_id_to_slot_map().items()}[slot]
