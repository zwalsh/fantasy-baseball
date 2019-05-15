import sys
import logging
import logging.config

import lineup_optimizer
from espn.espn_api import EspnApi
from fangraphs_api import FangraphsApi
from stats import Stats

DEV_LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s [%(name)s:%(lineno)d] %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        },
        'espn.api': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True
        },
        'lineup': {},
        'fangraphs.api': {},
        'config.team_reader': {},
    }

}

logging.config.dictConfig(DEV_LOGGING)

logger = logging.getLogger()


def password(user):
    """
    Fetches the user's password from disk.
    :param str user: the username for which to get the password
    :return str: the password stored on disk for that user
    """
    with open(user + "_pass.txt", "w+") as pass_file:
        return pass_file.read()

username = sys.argv[1]
logger.info("starting up with user %(user)s", {"user": username})
password = password(username)

api = EspnApi(username, password)

current_lineup = api.lineup(api.team_id())
lineup_settings = api.lineup_settings()

scoring_settings = api.scoring_settings()

proj = FangraphsApi().hitter_projections()

max_lineup_for_stats = lineup_optimizer.optimize_lineup(current_lineup, lineup_settings, proj, scoring_settings)


lineup_maxes = dict()
print("CURRENT LINEUP")
print(current_lineup)
print(lineup_optimizer.stats_with_projections(current_lineup, proj))

for stat, best_lineup in max_lineup_for_stats.items():
    cur_bests = lineup_maxes.get(best_lineup.starters(), [best_lineup])
    cur_bests.append(stat)
    lineup_maxes[best_lineup.starters()] = cur_bests

for bests in lineup_maxes.values():
    lineup = bests[0]
    stats = lineup_optimizer.stats_with_projections(lineup, proj)
    transitions = current_lineup.transitions(lineup)
    print(lineup)
    for t in transitions:
        print(t)
    print(stats)
    print("Best for:")
    for best in bests[1:]:
        print("{}".format(best))
    print("\n\n\n")

"""
TO DO:
    * Calculate optimal lineup correctly
    * Add actual logging with a logger
    * Set up push notifications


calculate optimal lineup:
    
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



