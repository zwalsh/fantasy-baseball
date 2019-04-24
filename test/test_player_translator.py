import unittest

from espn.player_translator import roster_entry_to_player
from lineup_slot import LineupSlot


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
        self.assertEqual(nolan.possible_positions, {LineupSlot.THIRD,
                                                    LineupSlot.CORNER_INFIELD,
                                                    LineupSlot.BENCH,
                                                    LineupSlot.INJURED})

        travis = roster_entry_to_player(self.travis_shaw_entry)
        self.assertEqual(travis.name, "Travis Shaw")
        self.assertEqual(travis.possible_positions, {
            LineupSlot.SECOND,
            LineupSlot.THIRD,
            LineupSlot.MIDDLE_INFIELD,
            LineupSlot.CORNER_INFIELD,
            LineupSlot.BENCH,
            LineupSlot.INJURED
        })
