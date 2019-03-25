

class Player:

    def __init__(self, name, espn_id, position, possible_positions):
        self.name = name
        self.espn_id = espn_id
        self.position = position
        self.possible_positions = possible_positions

    def __str__(self):
        return self.name + ", " + self.espn_id


