from enum import Enum


class Position(Enum):
    STARTER = 1
    CATCHER = 2
    FIRST = 3
    SECOND = 4
    THIRD = 5
    SHORT = 6
    LEFT = 7
    CENTER = 8
    RIGHT = 9
    DH = 10
    RELIEVER = 11

    def __str__(self):
        names = {
            Position.STARTER: "SP",
            Position.CATCHER: "C",
            Position.FIRST: "1B",
            Position.SECOND: "2B",
            Position.THIRD: "3B",
            Position.SHORT: "SS",
            Position.LEFT: "LF",
            Position.CENTER: "CF",
            Position.RIGHT: "RF",
            Position.DH: "DH",
            Position.RELIEVER: "RP"
        }
        return names[self]
