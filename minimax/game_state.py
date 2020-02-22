from typing import List


class GameState(object):

    def __init__(self):
        return

    def children(self) -> List['GameState']:
        pass

    def is_terminal(self) -> bool:
        pass
