from player import Player
from lineup_slot import LineupSlot

espn_slot_to_slot = {
    0: LineupSlot.CATCHER,
    1: LineupSlot.FIRST,
    2: LineupSlot.SECOND,
    3: LineupSlot.THIRD,
    4: LineupSlot.SHORT,
    6: LineupSlot.MIDDLE_INFIELD,
    7: LineupSlot.CORNER_INFIELD,
    5: LineupSlot.OUTFIELD,
    13: LineupSlot.PITCHER,
    16: LineupSlot.BENCH,
    17: LineupSlot.INJURED
}


def roster_entry_to_player(entry):
    """
    Takes an object from the ESPN API that represents a Player
    and converts it into a Player, including all positions
    :param entry: ESPN api player object
    :return: Player object
    """
    player_id = entry['playerId']
    player_map = entry['playerPoolEntry']['player']
    name = player_map['fullName']
    espn_positions = player_map['eligibleSlots']
    possible_positions = set()
    for espn_pos in espn_positions:
        converted = espn_slot_to_slot.get(espn_pos)
        if converted is not None:
            possible_positions.add(converted)
    return Player(name, player_id, possible_positions)
