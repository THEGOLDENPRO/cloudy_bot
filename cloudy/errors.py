from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .impl.command import Command

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


class InvalidParameter(CloudyError):
    """
    Raises whenever there is an invalid parameter in a command.
    Normally occurs when you have uppercase characters in a command argument.
    """
    def __init__(self, command: Command, invalid_param: str):
        super().__init__(
            f"The parameter used in the command '{command.name}' is NOT allowed >> {invalid_param}"
        )