import unittest
from player import Player
from lineup_slot import LineupSlot


class Test(unittest.TestCase):
    yelich = Player("Christian Yelich", 123, {LineupSlot.OUTFIELD})
    shaw = Player("Travis Shaw", 456, {LineupSlot.SECOND,
                                       LineupSlot.THIRD,
                                       LineupSlot.MIDDLE_INFIELD,
                                       LineupSlot.CORNER_INFIELD})

    def test_can_play(self):
        self.assertTrue(self.yelich.can_play(LineupSlot.OUTFIELD))
        self.assertFalse(self.yelich.can_play(LineupSlot.FIRST))
        self.assertFalse(self.yelich.can_play(LineupSlot.MIDDLE_INFIELD))

        self.assertTrue(self.shaw.can_play(LineupSlot.MIDDLE_INFIELD))
        self.assertTrue(self.shaw.can_play(LineupSlot.CORNER_INFIELD))
        self.assertTrue(self.shaw.can_play(LineupSlot.SECOND))
        self.assertTrue(self.shaw.can_play(LineupSlot.THIRD))
        self.assertFalse(self.shaw.can_play(LineupSlot.SHORT))
        self.assertFalse(self.shaw.can_play(LineupSlot.FIRST))
