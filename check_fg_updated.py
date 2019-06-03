import logging.config

import config.logging_config
from fangraphs.api import FangraphsApi
from fangraphs.metrics import FangraphsMetrics

logging.config.dictConfig(config.logging_config.config_dict())

cur_last_updated = FangraphsApi.last_updated()
metrics_last_updated = FangraphsMetrics.last_seen_update()
if cur_last_updated != metrics_last_updated:
    FangraphsMetrics.record_update(cur_last_updated)
