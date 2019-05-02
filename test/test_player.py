import unittest
from player import Player
from lineup_slot import LineupSlot


class PlayerTest(unittest.TestCase):
    sanchez = Player("Gary Sanchez", 165412, LineupSlot.catcher())
    muncy = Player("Max Munch", 123531, LineupSlot.first() | LineupSlot.third())
    merrifield = Player("Whit Merrifield", 56263, LineupSlot.second() | LineupSlot.outfield())
    carpenter = Player("Matt Carpenter", 201325, LineupSlot.first() | LineupSlot.third())
    segura = Player("Jean Segura", 25414, LineupSlot.short())
    cano = Player("Robinson Cano", 29071, LineupSlot.second())
    rizzo = Player("Anthony Rizzo", 109123649, LineupSlot.first())
    springer = Player("George Springer", 18946, LineupSlot.outfield())
    rosario = Player("Eddie Rosario", 10934, LineupSlot.outfield())
    braun = Player("Ryan Braun", 97612, LineupSlot.outfield())
    santana = Player("Domingo Santana", 892, LineupSlot.outfield())
    choo = Player("Shin-Soo Choo", 32923, LineupSlot.outfield())
    cabrera = Player("Miguel Cabrera", 723, LineupSlot.first())
    peraza = Player("Jose Peraza", 74395, LineupSlot.second() | LineupSlot.short())
    olson = Player("Matt Olson", 14632718, {LineupSlot.INJURED,
                                            LineupSlot.BENCH})
    jimenez = Player("Eloy Jimenez", 98653429, {LineupSlot.INJURED,
                                                LineupSlot.BENCH})
    degrom = Player("Jacob deGrom", 189346, LineupSlot.pitcher())
    kimbrel = Player("Craig Kimbrel", 3489346, LineupSlot.pitcher())
    morton = Player("Charlie Morton", 469346, LineupSlot.pitcher())
    hill = Player("Rich Hill", 57346, LineupSlot.pitcher())
    arrieta = Player("Jake Arrieta", 189343654, LineupSlot.pitcher())
    glasnow = Player("Tyler Glasnow", 469346, LineupSlot.pitcher())
    barnes = Player("Matt Barnes", 457346, LineupSlot.pitcher())
    stripling = Player("Ross Stripling", 189343423, LineupSlot.pitcher())
    smith = Player("Caleb Smith", 24946, LineupSlot.pitcher())
    paddack = Player("Chris Paddack", 189345, LineupSlot.pitcher())

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
