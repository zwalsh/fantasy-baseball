class LineupTransition:
    def __init__(self, player, from_slot, to_slot):
        """
        Represents the transition of a Player in a Lineup from one slot to another.
        :param Player player: the Player that is moving
        :param LineupSlot from_slot: the LineupSlot they are moving from
        :param LineupSlot to_slot: the LineupSlot they are moving to
        """
        self.player = player
        self.from_slot = from_slot
        self.to_slot = to_slot

    def __eq__(self, other):
        return (
            self.player == other.player
            and self.from_slot == other.from_slot
            and self.to_slot == other.to_slot
        )

    def __hash__(self):
        return hash(self.player) + hash(self.from_slot) + hash(self.to_slot)

    def __str__(self):
        return "{}\t{}\t{}".format(self.player, self.from_slot, self.to_slot)
