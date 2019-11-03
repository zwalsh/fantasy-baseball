from enum import Enum


class BasketballPosition(Enum):
    POINT_GUARD = 1
    SHOOTING_GUARD = 2
    SMALL_FORWARD = 3
    POWER_FORWARD = 4
    CENTER = 5

    def __str__(self):
        names = {
            BasketballPosition.POINT_GUARD: "PG",
            BasketballPosition.SHOOTING_GUARD: "SG",
            BasketballPosition.SMALL_FORWARD: "SF",
            BasketballPosition.POWER_FORWARD: "PF",
            BasketballPosition.CENTER: "C",
        }
        return names[self]

