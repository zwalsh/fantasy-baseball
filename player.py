from espn.baseball.lineup_slot import LineupSlot


class Player:
    def __init__(self, name, first, last, espn_id, possible_positions, default_position):
        """
        Creates a Player from their name, espn id, primary positions, and possible positions
        :param default_position:
        :param str name: the player's whole name
        :param str first: the player's first name
        :param str last: the player's last name
        :param int espn_id: their id as specified by ESPN
        :param set possible_positions: set of LineupSlots they can play
        :param Position default_position: their typical position
        """
        self.name = name
        self.first = first
        self.last = last
        self.espn_id = espn_id
        self.possible_positions = possible_positions
        self.default_position = default_position

    def __str__(self):
        return f"{self.default_position}\t{self.name}\t{self.espn_id}"

    def can_play(self, slot):
        """
        Checks if this player can play in the given slot,
        where a slot is an array of Positions.
        :param LineupSlot slot: slot to see if the player can play in
        :return: true if one of the player's possible positions matches
        """
        return slot in self.possible_positions

    def __eq__(self, other):
        return self.espn_id == other.espn_id

    def __hash__(self):
        return hash(self.name) + hash(self.espn_id)
