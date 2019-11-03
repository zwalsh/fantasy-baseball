from enum import Enum


class FootballPosition(Enum):
    QUARTER_BACK = 1
    RUNNING_BACK = 2
    WIDE_RECEIVER = 3
    TIGHT_END = 4
    DEFENSE = 16

    def __str__(self):
        names = {
            FootballPosition.QUARTER_BACK: "QB",
            FootballPosition.RUNNING_BACK: "RB",
            FootballPosition.WIDE_RECEIVER: "WR",
            FootballPosition.TIGHT_END: "TE",
            FootballPosition.DEFENSE: "DST",
        }
        return names[self]