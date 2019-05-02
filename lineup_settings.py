
class LineupSettings:

    def __init__(self, slot_counts):
        """
        Maps LineupSlots to the number of players that may fill
        that slot in some Lineup
        :param dict slot_counts:
        """
        self.slot_counts = slot_counts

    def total_for_slots(self, slots):
        """
        Says how many players can play across all of the given slots under these
        LineupSettings
        :param list slots: the slots for which to sum all counts
        :return int: the number of players that can use these slots
        """
        total = 0
        for s in slots:
            total += self.slot_counts[s]
        return total
