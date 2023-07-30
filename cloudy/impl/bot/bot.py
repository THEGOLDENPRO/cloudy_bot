from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from typing import Literal
    from discord_typings import (
        UpdatePresenceData, ApplicationCommandPayload, ApplicationCommandOptionData,
        UserData, ApplicationData, ApplicationCommandData, InteractionData
    )

import logging
from datetime import datetime
from devgoldyutils import Colours
from nextcore.http import Route

from ..droplet import Droplet
from .basic_bot import BasicBot
from ..command import Command

__all__ = ("Bot",)

class Bot(BasicBot):
    """Where it all begins... ❇️"""
    def __init__(
        self, 
        token: str = None, 
        intents: int = 0, 
        presence: UpdatePresenceData = {"status": "online"}, 
        log_level: Literal[50, 40, 30, 20, 10, 0] = logging.INFO,
        no_description_msg: str = None
    ) -> None:
        super().__init__(
            token, intents, presence, log_level
        )

        self.no_description_msg = no_description_msg

        self.commands: List[Command] = []
        """A list of registered commands."""

        self.user: UserData = None
        """The bot's user data."""
        self.application: ApplicationData = None
        """The bot's application data."""

        self.__unregistered_commands: Dict[str, Command] = {}
        """Dictionary of commands to be registered on setup. Command name as key."""

        self.registered_commands: Dict[str, Command] = {}
        """Dictionary of registered commands. Interaction id are their keys."""

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

                self.__unregistered_commands[command.name] = command

                self.logger.debug(f"Added command '{Colours.PINK_GREY.apply(command.name)}'.")

                return command

            return inner(func)

        return decorate


    async def _setup(self) -> None:
        await self.__batch_create_interactions(
            testing_guild = self.config("TESTING_GUILD", default = None)
        )
        self.logger.debug("Done registering interactions!")

        self.shard_manager.event_dispatcher.add_listener(
            self.__on_interaction,
            event_name="INTERACTION_CREATE"
        )
        self.logger.info("Interaction listener set!")

    async def _pre_setup(self) -> None:
        """
        Used to fetch some data from discord needed by cloudy before running actual setup.
        """

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

        self.user = await r.json()
        self.logger.debug("Bot's user data requested!")


    async def __batch_create_interactions(
        self, 
        testing_guild: str | None
    ) -> None:
        created_interactions: List[ApplicationCommandData] = []
        slash_command_payloads: List[ApplicationCommandPayload] = [
            dict(x) for _, x in self.__unregistered_commands.items()
        ]

        if testing_guild is not None:
            # Creating guild commands for testing server.
            # --------------------------------------------
            testing_guild_route = Route(
                "PUT",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id = self.application["id"],
                guild_id = testing_guild,
            )

            # Creating guild commands for testing server.
            r = await self.http_client.request(
                testing_guild_route,
                rate_limit_key = self.authentication.rate_limit_key,
                headers = self.authentication.headers,
                json = slash_command_payloads
            )

            created_interactions = await r.json()

            self.logger.debug("Created guild commands for testing guild. ✅")

        else:

            # Creating global commands.
            # --------------------------
            global_route = Route(
                "PUT",
                "/applications/{application_id}/commands",
                application_id = self.application["id"]
            )

            r = await self.http_client.request(
                global_route,
                rate_limit_key = self.authentication.rate_limit_key,
                headers = self.authentication.headers,
                json = slash_command_payloads
            )

            created_interactions = await r.json()
            self.logger.debug("Created global commands. ✅")


        # Registering slash commands with the interaction id.
        # idk, I might support more interactions in the future so this may become necessary.
        for interaction in created_interactions:

            for command_name in self.__unregistered_commands:

                if command_name == interaction["name"]:
                    self.registered_commands[interaction["id"]] = self.__unregistered_commands[command_name]
                    del self.__unregistered_commands[command_name]
                    self.logger.debug(
                        f"Registered '{Colours.PINK_GREY.apply(command_name)}' command with interaction id '{Colours.GREY.apply(interaction['id'])}'."
                    )
                    break

        return None


    async def __on_interaction(self, interaction: InteractionData) -> None:

        # Slash commands.
        # ----------------
        if interaction["type"] == 2:
            command: Command | None = self.registered_commands.get(f"{interaction['data']['id']}")

            if command is not None:
                droplet = Droplet(
                    data = interaction
                )

                await command.invoke(
                    droplet
                )

        return None