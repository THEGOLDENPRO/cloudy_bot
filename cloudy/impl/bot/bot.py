from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from typing import Literal
    from discord_typings import UpdatePresenceData, ApplicationCommandPayload, ApplicationCommandOptionData

import logging
from datetime import datetime

from .base_bot import BaseBot
from ..command import Command

__all__ = ("Bot",)

class Bot(BaseBot):
    """Where it all begins... ❇️"""
    def __init__(
        self, 
        token: str = None, 
        intents: int = 0, 
        presence: UpdatePresenceData = {"status": "online"}, 
        log_level: Literal[50, 40, 30, 20, 10, 0] = logging.WARNING,
        no_description_msg: str = None
    ) -> None:
        super().__init__(
            token, intents, presence, log_level
        )

        self.no_description_msg = no_description_msg

        self.commands: List[Command] = []
        """A list of registered commands."""

        self.__unregistered_commands = List[Command]

    @property
    def latency(self) -> float | None:
        """
        Returns the latency in milliseconds between discord and cloudy.

        Cloudy -> Discord -> Cloudy
        """
        try:
            return self.shard_manager.active_shards[0].latency
        except RuntimeError:
            return None

    @property
    def up_time(self) -> datetime | None:
        """
        Returns a datetime object of cloudy's uptime.
        Returns None if cloudy was not started or ready, else it will always return a datetime object.
        """
        if self._start_up_time is not None:
            return datetime.fromtimestamp(datetime.now().timestamp() - self._start_up_time.timestamp())

        return None

    def command(
        self,
        name: str = None, 
        description: str = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None,
        **extra: ApplicationCommandPayload
    ):
        """
        Add a command to cloudy with this decorator.
        
        ---------------
        
        ⭐ Example:
        -------------
        This is how you create a command in Cloudy::

            @bot.command()
            async def hello(self, droplet: Droplet):
                await droplet.send("👋hello")
        
        """
        def decorate(func):
            def inner(func):
                command = Command(
                    self,
                    func,
                    name,
                    description,
                    slash_options,
                    **extra
                )

                self.__unregistered_commands.append(
                    command
                )

                return command

            return inner(func)

        return decorate