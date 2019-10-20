import unittest

from espn.baseball.baseball_api import BaseballApi
from espn.baseball.baseball_slot import BaseballSlot
from espn.baseball.baseball_position import BaseballPosition
from lineup_settings import LineupSettings


class Test(unittest.TestCase):
    bb_api = BaseballApi(None, 0, 0)

    nolan_arenado_entry = {
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

    travis_shaw_entry = {
        "defaultPositionId": 3,
        'id': 32890,
        'active': True,
        'eligibleSlots': [2, 3, 6, 7, 19, 12, 16, 17],
        'fullName': 'Travis Shaw',
        "firstName": "Travis",
        "lastName": "Shaw",
        'injured': False,
        'injuryStatus': 'ACTIVE'
    }

    def test_conversion(self):
        nolan = Test.bb_api.roster_entry_to_player(self.nolan_arenado_entry)
        self.assertEqual(nolan.name, "Nolan Arenado")
        self.assertEqual(nolan.possible_positions, BaseballSlot.third() | {BaseballSlot.INJURED})
        self.assertEqual(nolan.default_position, BaseballPosition.THIRD)

        travis = Test.bb_api.roster_entry_to_player(self.travis_shaw_entry)
        self.assertEqual(travis.name, "Travis Shaw")
        self.assertEqual(travis.first, "Travis")
        self.assertEqual(travis.last, "Shaw")
        self.assertEqual(travis.possible_positions, BaseballSlot.second() | BaseballSlot.third() | {BaseballSlot.INJURED})
        self.assertEqual(travis.default_position, BaseballPosition.FIRST)

    lineup_slot_response = {'0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 5, '6': 1, '7': 1, '8': 0, '9': 0, '10': 0,
                            '11': 0, '12': 1, '13': 9, '14': 0, '15': 0, '16': 3, '17': 2, '19': 0}

    def test_convert_lineup_slot_counts(self):
        settings = {
            BaseballSlot.CATCHER: 1,
            BaseballSlot.FIRST: 1,
            BaseballSlot.SECOND: 1,
            BaseballSlot.THIRD: 1,
            BaseballSlot.SHORT: 1,
            BaseballSlot.MIDDLE_INFIELD: 1,
            BaseballSlot.CORNER_INFIELD: 1,
            BaseballSlot.OUTFIELD: 5,
            BaseballSlot.UTIL: 1,
            BaseballSlot.PITCHER: 9,
            BaseballSlot.BENCH: 3,
            BaseballSlot.INJURED: 2,
        }
        self.assertEqual(Test.bb_api.lineup_slot_counts_to_lineup_settings(self.lineup_slot_response).slot_counts,
                         LineupSettings(settings).slot_counts)

    def test_slot_to_slot_id(self):
        self.assertEqual(BaseballSlot.CATCHER.slot_id(), 0)
        self.assertEqual(BaseballSlot.UTIL.slot_id(), 12)
