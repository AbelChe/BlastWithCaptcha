import logging
import logging.config

import yaml

Logging = logging

with open('log.yml', 'r') as f:
    dict_conf = yaml.load(f)

Logging.config.dictConfig(dict_conf)
