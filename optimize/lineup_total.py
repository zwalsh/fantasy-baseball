from stats import Stats


class LineupTotal:
    def __init__(self, lineup, stats):
        """
        Represents a total of how a lineup will perform on a given day. Pairs a Lineup
        with a Stats object that holds their cumulative, total stats.
        :param Lineup lineup: the lineup accruing the stats
        :param Stats stats: the stats they are projected to accrue
        """
        self.lineup = lineup
        self.stats = stats

    @staticmethod
    def total_from_projections(lineup, projections):
        """
        Calculates the accumulated statistics of this set of starters, based on the given projections
        for each player
        :param Lineup lineup: the lineup of players that are starting
        :param dict projections: the projected stats that those players will accrue
        :return Stats: a Stats object holding their cumulative totals
        """
        stats = Stats({})

        for starter in lineup.starters():
            projection = projections.get(starter.name)
            if projection is not None:
                stats += projection

        for stat, value in stats.stat_dict.items():
            stats.stat_dict[stat] = round(value, 2)

        return LineupTotal(lineup, stats)

    def compare(self, other, stat, comparator):
        """
        Checks if this LineupTotal's value for the given Stat satisfies the comparator
        when compared to the given LineupTotal's value
        :param LineupTotal other: the LineupTotal to compare against
        :param Stat stat: the stat to compare with
        :param fun comparator: a function that compares two values and returns a boolean
        :return bool: true if this one's value for the stat is >= the value for the given total
        """
        stat_val = self.stats.value_for_stat(stat)
        other_val = other.stats.value_for_stat(stat)

        return comparator(stat_val, other_val)

    def passes_threshold(self, stat, threshold, comparator):
        """
        Checks if this LineupTotal passes some threshold value for the given Stat.
        :param Stat stat: the Stat whose value is being checked
        :param float threshold: the threshold value that this lineup must pass
        :param fun comparator: the function to compare this value to the threshold
        :return bool: True if this LineupTotal passes
        """
        return comparator(self.stats.value_for_stat(stat), threshold)