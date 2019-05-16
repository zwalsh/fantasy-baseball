import logging.config
import sys
from pathlib import Path

import config.notifier_config
from fangraphs_api import FangraphsApi

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
        "config.password_reader": {},
        "notifications": {},
        "notifications.client.dev": {},
        "notifications.client.pushed": {},
    }

}

logging.config.dictConfig(DEV_LOGGING)

logger = logging.getLogger()


username = sys.argv[1]
logger.info("starting up with user %(user)s", {"user": username})
password = config.password_reader.password(username, Path.cwd() / "config/passwords")
configs = config.team_reader.all_teams(Path.cwd() / "config/team_configs")
fangraphs = FangraphsApi()
notifier = config.notifier_config.current_notifier(username)

notifier.notify_set_lineup("Do Damage", 54.0678, [])

#
# for c in filter(lambda team_config: team_config.username == username, configs):
#     espn = EspnApi(username, password, c.league_id, c.team_id)
#     lineup_optimizer.print_lineup_optimization(espn, fangraphs)



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



