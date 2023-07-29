"""
Contains the Cloudy logger object. You may use this to change logging levels.
"""

import logging
from devgoldyutils import add_custom_handler, Colours

cloudy_logger = add_custom_handler(
    logging.getLogger(Colours.BLUE.apply("☁️  Cloudy")), level = logging.INFO
)