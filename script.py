import sys
import logging
import logging.config
from pathlib import Path

import config.team_reader
import config.password_reader
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
        "config.password_reader": {},
    }

}

logging.config.dictConfig(DEV_LOGGING)

logger = logging.getLogger()


username = sys.argv[1]
logger.info("starting up with user %(user)s", {"user": username})
password = config.password_reader.password(username, Path.cwd() / "config/passwords")
configs = config.team_reader.all_teams(Path.cwd() / "config/team_configs")
fangraphs = FangraphsApi()


for c in filter(lambda team_config: team_config.username == username, configs):
    espn = EspnApi(username, password, c.league_id, c.team_id)
    lineup_optimizer.print_lineup_optimization(espn, fangraphs)



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



