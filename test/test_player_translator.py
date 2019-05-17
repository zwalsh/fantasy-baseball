import unittest

from espn.player_translator import roster_entry_to_player, slot_to_slot_id
from espn.player_translator import lineup_slot_counts_to_lineup_settings
from lineup_slot import LineupSlot
from lineup_settings import LineupSettings


class Test(unittest.TestCase):
    nolan_arenado_entry = {
        "playerId": 31261,
        "playerPoolEntry": {
            "player": {
                "defaultPositionId": 5,
                "eligibleSlots": [
                    3,
                    7,
                    19,
                    12,
                    16,
                    17
                ],
                "fullName": "Nolan Arenado",
                "firstName": "Nolan",
                "lastName": "Arenado",
                "id": 31261,
            }
        }
    }

    travis_shaw_entry = {'injuryStatus': 'NORMAL',
                         'lineupSlotId': 2,
                         'pendingTransactionIds': None,
                         'playerId': 32890,
                         'playerPoolEntry': {'id': 32890,
                                             'lineupLocked': True,
                                             'player': {
                                                 'active': True,
                                                 'eligibleSlots': [2, 3, 6, 7, 19, 12, 16, 17],
                                                 'fullName': 'Travis Shaw',
                                                 "firstName": "Travis",
                                                 "lastName": "Shaw",
                                                 'injured': False,
                                                 'injuryStatus': 'ACTIVE'
                                             },
                                             'rosterLocked': True,
                                             'status': 'ONTEAM',
                                             'tradeLocked': False},
                         'status': 'NORMAL'}

    def test_conversion(self):
        nolan = roster_entry_to_player(self.nolan_arenado_entry)
        self.assertEqual(nolan.name, "Nolan Arenado")
        self.assertEqual(nolan.possible_positions, LineupSlot.third() | {LineupSlot.INJURED})

        travis = roster_entry_to_player(self.travis_shaw_entry)
        self.assertEqual(travis.name, "Travis Shaw")
        self.assertEqual(travis.first, "Travis")
        self.assertEqual(travis.last, "Shaw")
        self.assertEqual(travis.possible_positions, LineupSlot.second() | LineupSlot.third() | {LineupSlot.INJURED})

    lineup_slot_response = {'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 5, '6': 1, '7': 1, '8': 0, '9': 0, '10': 0,
                            '11': 0, '12': 1, '13': 9, '14': 0, '15': 0, '16': 3, '17': 2, '19': 0}

    def test_convert_lineup_slot_counts(self):
        settings = {
            LineupSlot.CATCHER: 1,
            LineupSlot.FIRST: 1,
            LineupSlot.SECOND: 1,
            LineupSlot.THIRD: 1,
            LineupSlot.SHORT: 1,
            LineupSlot.MIDDLE_INFIELD: 1,
            LineupSlot.CORNER_INFIELD: 1,
            LineupSlot.OUTFIELD: 5,
            LineupSlot.UTIL: 1,
            LineupSlot.PITCHER: 9,
            LineupSlot.BENCH: 3,
            LineupSlot.INJURED: 2,
        }
        self.assertEqual(lineup_slot_counts_to_lineup_settings(self.lineup_slot_response).slot_counts,
                         LineupSettings(settings).slot_counts)

    def test_slot_to_slot_id(self):
        self.assertEqual(slot_to_slot_id(LineupSlot.CATCHER), 0)
        self.assertEqual(slot_to_slot_id(LineupSlot.UTIL), 12)
