
class LineupSettings:

    def __init__(self, slot_counts):
        """
        Maps LineupSlots to the number of players that may fill
        that slot in some Lineup
        :param dict slot_counts:
        """
        self.slot_counts = slot_counts
