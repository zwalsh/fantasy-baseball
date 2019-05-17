import logging.config
import sys
from pathlib import Path

import config.notifier_config
import config.password_reader
import config.team_reader
import optimize.lineup_optimizer
from espn.espn_api import EspnApi
from fangraphs_api import FangraphsApi
from scoring_setting import ScoringSetting
from stats import Stat

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
        'optimize.optimizer': {},
    }

}

logging.config.dictConfig(DEV_LOGGING)

logger = logging.getLogger()

username = sys.argv[1]
logger.info("starting up with user %(user)s", {"user": username})
password = config.password_reader.password(username, Path.cwd() / "config/passwords")
configs = config.team_reader.all_teams(Path.cwd() / "config/team_configs")

fangraphs = FangraphsApi()

for team_config in configs:
    espn = EspnApi(username, password, team_config.league_id, team_config.team_id)
    optimize.lineup_optimizer.optimize_lineup(espn, fangraphs, config.notifier_config.current_notifier(username))

