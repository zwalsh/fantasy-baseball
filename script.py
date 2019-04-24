import sys

import lineup_optimizer
from espn.espn_api import EspnApi
from fangraphs_api import FangraphsApi
from stats import Stats


def password(user):
    with open(user + "_pass.txt", "w+") as pass_file:
        return pass_file.read()


username = sys.argv[1]
password = password(username)

api = EspnApi(username, password)

l = api.lineup(api.team_id())

# league = api.league()
# lineup = api.lineup(api.team_id())
# lineup_settings = api.lineup_settings()
#
# scoring_settings = api.scoring_settings()
#
# proj = FangraphsApi().hitter_projections()
#
# max_lineup_for_stats = lineup_optimizer.optimize_lineup(lineup, lineup_settings, proj, scoring_settings)
#
# lineup_maxes = dict()
#
# for stat_id, (_, best_lineup) in max_lineup_for_stats.items():
#     cur_bests = lineup_maxes.get(best_lineup, [])
#     cur_bests.append(stat_id)
#     lineup_maxes[best_lineup] = cur_bests
#
# for lineup, bests in lineup_maxes.items():
#     stats = lineup_optimizer.stats_with_projections(lineup, proj)
#     for player in lineup:
#         print("{}\n".format(player.__str__()))
#     print(stats)
#     print("Best for:")
#     for best in bests:
#         print("{}".format(Stats.stat_names.get(best)))

"""
TO DO:
- improve lineup generation to be less memory-intensive
    * generate all sets of starters instead of all lineups
    * depth-first search through slots instead of breadth-first
    * make list of lineups to process a stack that gets added onto?
    * associate ea/ starter set with the "closest" lineup to initial?
    * generate hitting starters and pitching starters separately?
    * examine handling of IL slot?




GOAL:
    - set lineup each day based on ideal lineup (fantasy points)
        * get current roster
        * get lineup settings
        * scan (all possible?) lineups
        * determine projections for each player
        * determine fantasy points generated by ea/ lineup (based on % to next guy?)
        * set best lineup
    
    Data types:
    Roster = [Player, ...]
        (Roster LineupSettings) -> [Lineup, ...] all possible lineups
        
    Player = {
        name: ...
        id: ...
        position?: ...
        possibleSlots: [Num, ...]
    }
    
    LineupSettings = {
        slot_id: count,
        ...
    }
    
    Lineup = {
        0: [Player, ...]
        1: [Player, ...]
        ...
    }
        (Lineup LineupSettings? Projections) -> Statistics
    
    Projections = { Player: Statistics }
    
    ScoringSettings: [(id, reverse?), ...]
    
    Statistics: {
        id: value,
        ...
    }
    
    League: [Team, ...]
    
    Team: {
        id: Int,
        lineup: Lineup,
        year_stats: Statistics,
    }
    
    Now, calculate optimal lineup:
    
    Given:
    * League
    * Team Id
    * Projections
    * Scoring Settings
    * set of starters
    
    Determine:
    * point value of those starters
    
    Approach:
    - calculate all others' stats based on curr lineup, projections
    - save my curr year stats
    - calc my stats with daily projections
    - for each stat, calc my % difference vs. all others ... ? sum to total points
    
    
    

"""



