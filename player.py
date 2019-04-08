

class Player:

    def __init__(self, name, espn_id, position, possible_positions):
        self.name = name
        self.espn_id = espn_id
        self.position = position
        self.possible_positions = possible_positions

    def __str__(self):
        return "{}\t{}".format(self.name, self.espn_id)

    def can_play(self, slot_id):
        return slot_id in self.possible_positions

    def __eq__(self, other):
        return self.espn_id == other.espn_id

    def __hash__(self):
        return hash(self.name) + hash(self.espn_id)
