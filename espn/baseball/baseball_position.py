from enum import Enum


class BaseballPosition(Enum):
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
            BaseballPosition.STARTER: "SP",
            BaseballPosition.CATCHER: "C",
            BaseballPosition.FIRST: "1B",
            BaseballPosition.SECOND: "2B",
            BaseballPosition.THIRD: "3B",
            BaseballPosition.SHORT: "SS",
            BaseballPosition.LEFT: "LF",
            BaseballPosition.CENTER: "CF",
            BaseballPosition.RIGHT: "RF",
            BaseballPosition.DH: "DH",
            BaseballPosition.RELIEVER: "RP"
        }
        return names[self]
