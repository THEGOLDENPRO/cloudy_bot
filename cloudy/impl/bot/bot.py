from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from typing import Literal
    from discord_typings import UpdatePresenceData, ApplicationCommandPayload

import logging
from .base_bot import BaseBot

__all__ = ("Bot",)

class Bot(BaseBot):
    """Where it all begins... ❇️"""
    def __init__(
        self, 
        token: str = None, 
        intents: int = 0, 
        presence: UpdatePresenceData = {"status": "online"}, 
        log_level: Literal[50, 40, 30, 20, 10, 0] = logging.WARNING
    ) -> None:
        super().__init__(
            token, intents, presence, log_level
        )

        self.interactions: List[ApplicationCommandPayload] = []