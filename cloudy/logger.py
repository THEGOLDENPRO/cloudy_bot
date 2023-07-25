import logging
from devgoldyutils import add_custom_handler, Colours

cloudy_logger = add_custom_handler(
    logging.getLogger(Colours.BLUE.apply("☁️  Cloudy")), level = logging.WARN
)

__all__ = ("logger",)