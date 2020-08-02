from enum import Enum


class FootballSlot(Enum):
    QUARTER_BACK = "QB"
    RUNNING_BACK = "RB"
    WIDE_RECEIVER = "WR"
    TIGHT_END = "TE"
    FLEX = "FLX"
    DEFENSE = "DST"
    BENCH = "BE"
    INJURED = "IR"

    def __str__(self):
        return self.value

    @staticmethod
    def slot_id_to_slot_map():
        return {
            0: FootballSlot.QUARTER_BACK,
            2: FootballSlot.RUNNING_BACK,
            4: FootballSlot.WIDE_RECEIVER,
            6: FootballSlot.TIGHT_END,
            16: FootballSlot.DEFENSE,
            20: FootballSlot.BENCH,
            21: FootballSlot.INJURED,
            23: FootballSlot.FLEX,
        }

    @staticmethod
    def starting_slots():
        return {ls for ls in FootballSlot} - {FootballSlot.BENCH, FootballSlot.INJURED}

    @staticmethod
    def espn_slot_to_slot(slot_id):
        return FootballSlot.slot_id_to_slot_map().get(slot_id)
