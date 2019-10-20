import unittest

from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.position import Position
from player import Player


class PlayerTest(unittest.TestCase):
    sanchez = Player("Gary Sanchez", None, None, 165412, BaseballSlot.catcher(), None)
    muncy = Player("Max Muncy", "Max", "Muncy", 123531, BaseballSlot.first() | BaseballSlot.third(), None)
    merrifield = Player("Whit Merrifield", "Whit", "Merrifield", 56263, BaseballSlot.second() | BaseballSlot.outfield(),
                        None)
    carpenter = Player("Matt Carpenter", "Matt", "Carpenter", 201325, BaseballSlot.first() | BaseballSlot.third(), None)
    segura = Player("Jean Segura", None, None, 25414, BaseballSlot.short(), None)
    cano = Player("Robinson Cano", None, None, 29071, BaseballSlot.second(), None)
    rizzo = Player("Anthony Rizzo", None, None, 109123649, BaseballSlot.first(), None)
    springer = Player("George Springer", None, None, 18946, BaseballSlot.outfield(), None)
    rosario = Player("Eddie Rosario", None, None, 10934, BaseballSlot.outfield(), None)
    braun = Player("Ryan Braun", None, None, 97612, BaseballSlot.outfield(), None)
    santana = Player("Domingo Santana", None, None, 892, BaseballSlot.outfield(), None)
    choo = Player("Shin-Soo Choo", None, None, 32923, BaseballSlot.outfield(), None)
    cabrera = Player("Miguel Cabrera", None, None, 723, BaseballSlot.first(), None)
    peraza = Player("Jose Peraza", None, None, 74395, BaseballSlot.second() | BaseballSlot.short(), None)
    olson = Player("Matt Olson", "Matt", "Olson", 14632718, {BaseballSlot.INJURED,
                                                             BaseballSlot.BENCH}, None)
    jimenez = Player("Eloy Jimenez", None, None, 98653429, {BaseballSlot.INJURED,
                                                            BaseballSlot.BENCH}, None)
    degrom = Player("Jacob deGrom", None, None, 189346, BaseballSlot.pitcher(), Position.STARTER)
    kimbrel = Player("Craig Kimbrel", None, None, 3489346, BaseballSlot.pitcher(), Position.RELIEVER)
    morton = Player("Charlie Morton", None, None, 469346, BaseballSlot.pitcher(), Position.STARTER)
    hill = Player("Rich Hill", None, None, 57346, BaseballSlot.pitcher(), Position.STARTER)
    arrieta = Player("Jake Arrieta", None, None, 189343654, BaseballSlot.pitcher(), Position.STARTER)
    glasnow = Player("Tyler Glasnow", None, None, 469346, BaseballSlot.pitcher(), Position.STARTER)
    barnes = Player("Matt Barnes", None, None, 457346, BaseballSlot.pitcher(), Position.RELIEVER)
    stripling = Player("Ross Stripling", None, None, 189343423, BaseballSlot.pitcher(), Position.RELIEVER)
    smith = Player("Caleb Smith", None, None, 24946, BaseballSlot.pitcher(), Position.STARTER)
    paddack = Player("Chris Paddack", None, None, 189345, BaseballSlot.pitcher(), Position.STARTER)

    yelich = Player("Christian Yelich", None, None, 123, {BaseballSlot.OUTFIELD}, None)
    shaw = Player("Travis Shaw", None, None, 456, {BaseballSlot.SECOND,
                                                   BaseballSlot.THIRD,
                                                   BaseballSlot.MIDDLE_INFIELD,
                                                   BaseballSlot.CORNER_INFIELD}, None)

    def test_can_play(self):
        self.assertTrue(self.yelich.can_play(BaseballSlot.OUTFIELD))
        self.assertFalse(self.yelich.can_play(BaseballSlot.FIRST))
        self.assertFalse(self.yelich.can_play(BaseballSlot.MIDDLE_INFIELD))

        self.assertTrue(self.shaw.can_play(BaseballSlot.MIDDLE_INFIELD))
        self.assertTrue(self.shaw.can_play(BaseballSlot.CORNER_INFIELD))
        self.assertTrue(self.shaw.can_play(BaseballSlot.SECOND))
        self.assertTrue(self.shaw.can_play(BaseballSlot.THIRD))
        self.assertFalse(self.shaw.can_play(BaseballSlot.SHORT))
        self.assertFalse(self.shaw.can_play(BaseballSlot.FIRST))
