import logging
from devgoldyutils import Colours

from .logger import cloudy_logger

class CloudyError(Exception):
    """Raises whenever there's a known error in cloudy."""
    def __init__(self, message:str, logger: logging.Logger = None):
        message = Colours.RED.apply_to_string(message)

        if logger is None:
            logger = cloudy_logger

        logger.error(message)
        super().__init__(message)