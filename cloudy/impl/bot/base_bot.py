from __future__ import annotations
from typing import NoReturn, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import UpdatePresenceData, ApplicationData, UserData

import os
import asyncio
from decouple import AutoConfig
from devgoldyutils import LoggerAdapter, Colours

from nextcore.gateway import ShardManager
from nextcore.http import HTTPClient, BotAuthentication, UnauthorizedError, Route

from ... import errors
from ...logger import cloudy_logger

config = AutoConfig(search_path = os.getcwd())

__all__ = ("BaseBot",)

class BaseBot():
    """Base class for Bot."""
    def __init__(
        self, 
        token: str | None,
        intents: int,
        presence: UpdatePresenceData,
        log_level: Literal[50, 40, 30, 20, 10, 0]
    ) -> None:
        if token is None:
            token = config("BOT_TOKEN", default = None)

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

        self.bot_user: UserData = None
        """The bot's user data."""
        self.application: ApplicationData = None
        """The bot's application data."""

        # Setting log level.
        cloudy_logger.setLevel(log_level)

        self.async_loop = asyncio.get_event_loop()
        self.logger = LoggerAdapter(cloudy_logger, prefix = "Bot")

    def run(self) -> NoReturn:
        """⚡ Starts cloudy bot."""
        self.async_loop.run_until_complete(
            self.__run_async()
        )


    async def __setup(self) -> None:
        # TODO: Register interaction commands.
        # TODO: Start listening for interaction commands.
        ...

    async def __pre_setup(self) -> None:
        """Method ran before actual setup. This is used to fetch some data from discord needed by cloudy before running the actual setup."""

        # Get bot's application data.
        # ----------------------------
        r = await self.http_client.request(
            Route(
                "GET", 
                "/oauth2/applications/@me"
            ),
            rate_limit_key = self.authentication.rate_limit_key,
            headers = self.authentication.headers
        )

        self.application = await r.json()
        self.logger.debug("Application data requested!")

        # Get bot's user data.
        # ---------------------
        r = await self.http_client.request(
            Route(
                "GET", 
                "/users/@me"
            ),
            rate_limit_key = self.authentication.rate_limit_key,
            headers = self.authentication.headers
        )

        self.bot_user = await r.json()
        self.logger.debug("Bot's user object requested!")


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

        await self.__pre_setup()
        await self.__setup()

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