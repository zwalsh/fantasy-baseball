import logging.config
import sys
from pathlib import Path

import config.notifier_config
import config.logging_config
import optimize.lineup_optimizer
from espn.espn_api import EspnApi
from fangraphs.api import FangraphsApi


logging.config.dictConfig(config.logging_config.config_dict())

logger = logging.getLogger()

username = sys.argv[1]
logger.info("starting up with user %(user)s", {"user": username})
notifier = config.notifier_config.current_notifier(username)
try:
    password = config.password_reader.password(username, Path.cwd() / "config/passwords")
    configs = config.team_reader.all_teams(Path.cwd() / "config/team_configs")

    fangraphs = FangraphsApi()

    for team_config in configs:
        espn = EspnApi(username, password, team_config.league_id, team_config.team_id)
        optimize.lineup_optimizer.optimize_lineup(espn, fangraphs, notifier)
except Exception as e:
    logger.exception(e)
    notifier.error_occurred()
    raise e
