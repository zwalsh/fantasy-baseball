import os
from pathlib import Path

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
        "espn.football.api": {},
        "espn.stats_translator": {},
        "espn.trade_finder": {},
        "espn.trade_store": {},
        "espn.stat_store": {},
        'draft.draft_state_evaluator': {},
        'lineup': {},
        'fangraphs.api': {},
        "fangraphs.metrics": {},
        'fantasypros.api': {},
        'config.team_reader': {},
        "config.password_reader": {},
        "notifications": {},
        "notifications.client.dev": {},
        "notifications.client.pushed": {},
        "numberfire.api": {},
        'optimize.optimizer': {},
        "optimize.optimize_fp": {},
        "fantasysp.api": {},
        "tasks.set_lineup": {},
        "tasks.notify_new_trades": {},
        "tasks.check_fangraphs": {},
        "tasks.archive_daily_stats": {},
        "tasks.archive_year_stats": {},
        "tasks.set_fba_lineup": {},
    }
}


def prod_logging():
    prod_config = DEV_LOGGING.copy()

    log_dir = Path.cwd() / 'logs'
    if not log_dir.exists() or not log_dir.is_dir():
        log_dir.mkdir()
    log_path = log_dir / 'fantasy-baseball.log'
    if not log_path.exists() or not log_path.is_file():
        f = log_path.open('w+')
        f.close()

    prod_handler = prod_config['handlers']['default']
    prod_handler['level'] = 'INFO'
    prod_handler['class'] = 'logging.handlers.TimedRotatingFileHandler'
    prod_handler.pop('stream', None)
    prod_handler['filename'] = log_path.absolute()
    prod_handler['when'] = 'd'
    prod_handler['interval'] = 1
    prod_handler['backupCount'] = 10
    return prod_config


def config_dict():
    env = os.getenv('ENV', 'DEV')
    if env == 'PROD':
        return prod_logging()
    else:
        return DEV_LOGGING
