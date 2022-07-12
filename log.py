import logging
import logging.config

import yaml

Logging = logging

with open('log.yml', 'r', encoding='utf-8') as f:
    dict_conf = yaml.safe_load(f)

Logging.config.dictConfig(dict_conf)
