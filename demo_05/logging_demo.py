#!/usr/bin/env python

import logging

# https://docs.python.org/3.7/howto/logging.html
# create default StreamHandler handler with NOTSET level and add it into root
logging.basicConfig(format="%(levelname)s\t%(asctime)s\t%(message)s")

# create logger with no handlers
logger = logging.getLogger(__name__)

# logger will propagate all level enabled message to root
logger.setLevel(logging.DEBUG)

# logging message
logger.debug("debug message")
logger.info("info message")
logger.warning("warn message")
logger.error("error message")
logger.critical("critical message")
