from __future__ import annotations
from typing import NoReturn, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import UpdatePresenceData

import os
import asyncio
from datetime import datetime
from decouple import AutoConfig
from abc import ABC, abstractmethod
from devgoldyutils import LoggerAdapter, Colours

from nextcore.gateway import ShardManager
from nextcore.http import HTTPClient, BotAuthentication, UnauthorizedError

from ... import errors
from ...logger import cloudy_logger

__all__ = ("BasicBot",)

class BasicBot(ABC):
    """A basic bot."""
    def __init__(
        self, 
        token: str | None,
        intents: int,
        presence: UpdatePresenceData,
        log_level: Literal[50, 40, 30, 20, 10, 0]
    ) -> None:
        self.config = AutoConfig(search_path = os.getcwd())

        if token is None:
            token = self.config("BOT_TOKEN", default = None)

            if token is None:
                raise errors.CloudyError("Please enter a discord bot token!")

        self.intents = intents
        self.authentication = BotAuthentication(token)
        """Nextcore authentication class."""

        self.http_client = HTTPClient()
        """Nextcore http client, use this if you would like to perform low-level requests."""

        self.shard_manager = ShardManager(
            authentication = self.authentication,
            intents = self.intents,
            http_client = self.http_client,
            presence = presence
        )
        """Nextcore shard manager, use if you would like to take control of shards."""

        self._start_up_time: datetime = None

        # Setting log level.
        cloudy_logger.setLevel(log_level)

        self.async_loop = asyncio.get_event_loop()
        self.logger = LoggerAdapter(cloudy_logger, prefix = "Bot")

        super().__init__()

    def run(self) -> NoReturn:
        """⚡ Starts cloudy."""
        self.async_loop.run_until_complete(
            self.__run_async()
        )

    async def stop(self) -> NoReturn:
        """🛑 Stops cloudy."""
        # Raises critical error within nextcore and stops it.
        await self.shard_manager.dispatcher.dispatch( 
            "critical"
        )


    @abstractmethod
    async def _setup(self) -> None:
        """Runs right after nextcore is done with setup."""
        ...

    @abstractmethod
    async def _pre_setup(self) -> None:
        """Runs before the actual setup method is ran."""
        ...


    async def __run_async(self):
        await self.http_client.setup()

        try:
            await self.shard_manager.connect()
            self.logger.debug("Nextcore shard manager connecting...")
        except UnauthorizedError as e:
            raise errors.CloudyError(
                f"Nextcord shard manager failed to connect! We got '{e.message}' from nextcord.\n" \
                    "This might mean you haven't entered your discord token or it is incorrect!"
            )

        # Log when shards are ready.
        self.shard_manager.event_dispatcher.add_listener(
            lambda _: self.logger.info(f"Nextcore shards are {Colours.GREEN.apply_to_string('connected')} and {Colours.BLUE.apply_to_string('READY!')}"), 
            event_name = "READY"
        )

        await self._pre_setup()
        await self._setup()

        self._start_up_time = datetime.now() # Setting the start up time.

        # Raise a error and exit whenever a critical error occurs.
        error = await self.shard_manager.dispatcher.wait_for(lambda: True, "critical")

        self.logger.info(Colours.YELLOW.apply_to_string("Cloudy is quitting..."))
        self.logger.info(Colours.BLUE.apply_to_string(f"Reason: {error[0]}"))

        await self.__stop()

    async def __stop(self):
        self.logger.debug("Closing nextcore http client...")
        await self.http_client.close()

        self.logger.debug("Closing nextcore shard manager...")
        await self.shard_manager.close()
    
        self.logger.debug("Closing async_loop...")
        self.async_loop.stop()