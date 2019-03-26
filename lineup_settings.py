
class LineupSettings:

    def __init__(self, slot_counts):
        counts = dict()
        for k in slot_counts.keys():
            counts[int(k)] = int(slot_counts.get(k))
        self.slot_counts = counts
