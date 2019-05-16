from player import Player
from lineup_slot import LineupSlot
from lineup_settings import LineupSettings

espn_slot_to_slot = {
    0: LineupSlot.CATCHER,
    1: LineupSlot.FIRST,
    2: LineupSlot.SECOND,
    3: LineupSlot.THIRD,
    4: LineupSlot.SHORT,
    5: LineupSlot.OUTFIELD,
    6: LineupSlot.MIDDLE_INFIELD,
    7: LineupSlot.CORNER_INFIELD,
    12: LineupSlot.UTIL,
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
    first = player_map['firstName']
    last = player_map['lastName']
    espn_positions = player_map['eligibleSlots']
    possible_positions = set()
    for espn_pos in espn_positions:
        converted = espn_slot_to_slot.get(espn_pos)
        if converted is not None:
            possible_positions.add(converted)
    return Player(name, first, last, player_id, possible_positions)


def lineup_slot_counts_to_lineup_settings(settings):
    """
    Takes an ESPN API dictionary mapping slots (which arrive as strings)
    to counts (which arrive as ints), and converts it into a LineupSettings object
    :param dict settings: mapping of slot to count
    :return LineupSettings: the settings object for the given dictionary
    """
    converted_settings = dict()

    for slot_id, count in settings.items():
        slot = espn_slot_to_slot.get(int(slot_id))
        if slot is not None:
            converted_settings[slot] = count
    return LineupSettings(converted_settings)