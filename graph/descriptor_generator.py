from graph.graph_descriptor import GraphDescriptor, GraphLine
from stats import Stats


def generate_descriptor(stat_store, stat, espn, period_range):
    """
    Generates a GraphDescriptor with all necessary info to plot the graph.
    :param StatStore stat_store: the source of statistics
    :param Stat stat: the Stat being graphed
    :param EspnApi espn: access to ESPN's API (used to get team names)
    :param range period_range: the range of scoring periods to graph over
    :return GraphDescriptor: a descriptor for the resulting graph
    """
    team_ids = [t.team_id for t in espn.league().teams]
    lines = all_lines(team_ids, stat_store, stat, period_range)
    title = title_for_graph(stat, period_range)
    return GraphDescriptor(list(period_range), lines, title, "Scoring Period", str(stat))


def all_lines(team_ids, stat_store, stat, period_range):
    """
    Creates a list of all GraphLines for the graph over the given inputs
    :param list team_ids: a list of all team ids in the league
    :param StatStore stat_store: source of all historical information
    :param Stat stat: the statistic being graphed
    :param range period_range: the range of scoring periods being graphed
    :return list: a list of GraphLines, one per team over the given period
    """
    return [graph_line(team, stat_store, stat, period_range) for team in team_ids]


def graph_line(team, stat_store, stat, period_range):
    """
    Produces a GraphLine of the given stat for the given team over the range of scoring periods
    :param int team: the team id
    :param StatStore stat_store: the source of statistics
    :param Stat stat: the stat being graphed
    :param range period_range: the range being graphed
    :return GraphLine: the corresponding graph line
    """
    stats_dict = stat_store.retrieve_stats(team)
    cumul_total = 0.0
    data = []
    for pd in period_range:
        period_stats = stats_dict.get(pd, Stats({}))
        cumul_total += period_stats.value_for_stat(stat) or 0.0
        data.append(cumul_total)
    return GraphLine(data, team)


def title_for_graph(stat, period_range):
    """
    Determines the appropriate title for the graph based on the stat and the range
    :param Stat stat: the stat being graphed
    :param range period_range: the range of scoring periods being graphed
    :return str: the title of the graph
    """
    return f"{stat} from {period_range[0]} to {period_range[-1]}"
