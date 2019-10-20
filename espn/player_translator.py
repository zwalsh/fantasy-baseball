from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.position import Position
from lineup_settings import LineupSettings
from player import Player

espn_slot_to_slot = {
    0: BaseballSlot.CATCHER,
    1: BaseballSlot.FIRST,
    2: BaseballSlot.SECOND,
    3: BaseballSlot.THIRD,
    4: BaseballSlot.SHORT,
    5: BaseballSlot.OUTFIELD,
    6: BaseballSlot.MIDDLE_INFIELD,
    7: BaseballSlot.CORNER_INFIELD,
    12: BaseballSlot.UTIL,
    13: BaseballSlot.PITCHER,
    16: BaseballSlot.BENCH,
    17: BaseballSlot.INJURED
}


def slot_to_slot_id(slot):
    """
    Converts a LineupSlot back to an ESPN slot id
    :param BaseballSlot slot: the slot to convert
    :return int: the corresponding slot id
    """
    slot_to_espn_slot = {v: k for k, v in espn_slot_to_slot.items()}
    return slot_to_espn_slot[slot]


def roster_entry_to_player(player_map):
    """
    Takes an object from the ESPN API that represents a Player
    and converts it into a Player, including all positions
    :param player_map: ESPN api player object
    :return: Player object
    """
    player_id = player_map['id']
    name = player_map['fullName']
    position = Position(player_map['defaultPositionId'])
    first = player_map['firstName']
    last = player_map['lastName']
    espn_positions = player_map['eligibleSlots']
    possible_positions = set()
    for espn_pos in espn_positions:
        converted = espn_slot_to_slot.get(espn_pos)
        if converted is not None:
            possible_positions.add(converted)
    return Player(name, first, last, player_id, possible_positions, position)


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
