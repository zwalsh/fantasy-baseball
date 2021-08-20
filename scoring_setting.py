class ScoringSetting:
    def __init__(self, stat, is_reverse, points):
        """
        Represents a Scoring setting in a fantasy league, based on a Stat
        where teams are ranked on that stat. The boolean says if the rankings
        are in reverse order or not
        :param points: the number of points received for this Stat, if applicable
        :param Stat stat: the Stat that this setting is for
        :param bool is_reverse: the order of the standings
        """
        self.stat = stat
        self.is_reverse = is_reverse
        self.points = points
