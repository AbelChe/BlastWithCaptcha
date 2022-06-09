import logging

Logging = logging

Logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y.%m.%d. %H:%M:%S'
)

