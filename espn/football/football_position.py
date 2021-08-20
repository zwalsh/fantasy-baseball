from enum import Enum


def position_from_text(text):
    return POSITIONS[text]


class FootballPosition(Enum):
    QUARTER_BACK = 1
    RUNNING_BACK = 2
    WIDE_RECEIVER = 3
    TIGHT_END = 4
    DEFENSE = 16

    def __str__(self):
        return NAMES[self]


NAMES = {
    FootballPosition.QUARTER_BACK: "QB",
    FootballPosition.RUNNING_BACK: "RB",
    FootballPosition.WIDE_RECEIVER: "WR",
    FootballPosition.TIGHT_END: "TE",
    FootballPosition.DEFENSE: "DST",
}

POSITIONS = {
    "QB": FootballPosition.QUARTER_BACK,
    "RB": FootballPosition.RUNNING_BACK,
    "WR": FootballPosition.WIDE_RECEIVER,
    "TE": FootballPosition.TIGHT_END,
    "DST": FootballPosition.DEFENSE,
    "D": FootballPosition.DEFENSE
}
