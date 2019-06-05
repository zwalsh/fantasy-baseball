import unittest
from player import Player
from lineup_slot import LineupSlot


class PlayerTest(unittest.TestCase):
    sanchez = Player("Gary Sanchez", None, None, 165412, LineupSlot.catcher())
    muncy = Player("Max Muncy", "Max", "Muncy", 123531, LineupSlot.first() | LineupSlot.third())
    merrifield = Player("Whit Merrifield", "Whit", "Merrifield", 56263, LineupSlot.second() | LineupSlot.outfield())
    carpenter = Player("Matt Carpenter", "Matt", "Carpenter", 201325, LineupSlot.first() | LineupSlot.third())
    segura = Player("Jean Segura", None, None, 25414, LineupSlot.short())
    cano = Player("Robinson Cano", None, None, 29071, LineupSlot.second())
    rizzo = Player("Anthony Rizzo", None, None, 109123649, LineupSlot.first())
    springer = Player("George Springer", None, None, 18946, LineupSlot.outfield())
    rosario = Player("Eddie Rosario", None, None, 10934, LineupSlot.outfield())
    braun = Player("Ryan Braun", None, None, 97612, LineupSlot.outfield())
    santana = Player("Domingo Santana", None, None, 892, LineupSlot.outfield())
    choo = Player("Shin-Soo Choo", None, None, 32923, LineupSlot.outfield())
    cabrera = Player("Miguel Cabrera", None, None, 723, LineupSlot.first())
    peraza = Player("Jose Peraza", None, None, 74395, LineupSlot.second() | LineupSlot.short())
    olson = Player("Matt Olson", "Matt", "Olson", 14632718, {LineupSlot.INJURED,
                                                        LineupSlot.BENCH})
    jimenez = Player("Eloy Jimenez", None, None, 98653429, {LineupSlot.INJURED,
                                                            LineupSlot.BENCH})
    degrom = Player("Jacob deGrom", None, None, 189346, LineupSlot.pitcher())
    kimbrel = Player("Craig Kimbrel", None, None, 3489346, LineupSlot.pitcher())
    morton = Player("Charlie Morton", None, None, 469346, LineupSlot.pitcher())
    hill = Player("Rich Hill", None, None, 57346, LineupSlot.pitcher())
    arrieta = Player("Jake Arrieta", None, None, 189343654, LineupSlot.pitcher())
    glasnow = Player("Tyler Glasnow", None, None, 469346, LineupSlot.pitcher())
    barnes = Player("Matt Barnes", None, None, 457346, LineupSlot.pitcher())
    stripling = Player("Ross Stripling", None, None, 189343423, LineupSlot.pitcher())
    smith = Player("Caleb Smith", None, None, 24946, LineupSlot.pitcher())
    paddack = Player("Chris Paddack", None, None, 189345, LineupSlot.pitcher())

    yelich = Player("Christian Yelich", None, None, 123, {LineupSlot.OUTFIELD})
    shaw = Player("Travis Shaw", None, None, 456, {LineupSlot.SECOND,
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
