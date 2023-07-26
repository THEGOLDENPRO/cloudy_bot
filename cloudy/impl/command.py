from __future__ import annotations
from typing import Callable, Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from discord_typings import ApplicationCommandOptionData, ApplicationCommandPayload

    from .bot import Bot
    from .droplet import Droplet

import regex
from .. import errors

__all__ = ("Command",)

# Idk if this is how I want to do it.

class Command(dict): 
    """Represents an interaction command."""
    def __init__(
        self, 
        bot: Bot, 
        func: Callable[[], Any], # TODO: Add droplet here.
        name: str = None, 
        description: str = None, 
        slash_options: Dict[str, ApplicationCommandOptionData] = None,
        **extra: ApplicationCommandPayload
    ):
        self.bot = bot
        """An instance of ☁️ cloudy."""
        self.func = func
        """The command's callback function."""

        if name is None:
            name = func.__name__

        if description is None:
            description = "☁️ No description! Sorry." if bot.no_description_msg is None else bot.no_description_msg

        if slash_options is None:
            self.__slash_options = {}
        else:
            self.__slash_options = slash_options

        self.__params = self.__get_function_parameters()


        data = {
            "name": name,
            "description": description,
            "options": self.__params_to_options(),
            "type": 1
        }

        data.update(extra)

        super().__init__(
            data
        )

    @property
    def name(self) -> str:
        """The command's code name."""
        return self.get("name")

    @property
    def description(self) -> str:
        """The command's description. None if you didn't set a description for this command."""
        return self.get("description") if self.bot.no_description_msg is not None else None

    @property
    def slash_options(self):
        """Returns the slash command options set for this command."""
        return self.__slash_options
    
    @property
    def params(self) -> List[str]:
        """Returns list of the command's function parameters."""
        return self.__params


    async def invoke(self, droplet: Droplet) -> None:
        self.bot.logger.debug(f"Attempting to invoke command '{self.name}'...")
        ...


    def __get_function_parameters(self) -> List[str]:
        """Returns the function parameters of a command respectively."""
        
        # Get list of function params.
        func_params = list(self.func.__code__.co_varnames)
        
        # Removes 'self' argument.
        func_params.pop(0)

        # Removes 'platter' argument.
        func_params.pop(0)

        # Filters out other variables resulting in just function parameters. It's weird I know.
        params = func_params[:self.func.__code__.co_argcount - 2]

        return params

    def __params_to_options(self) -> List[ApplicationCommandOptionData]:
        """A function that converts slash command parameters to slash command options."""
        options: List[ApplicationCommandOptionData] = []

        # Discord chat input regex as of https://discord.com/developers/docs/interactions/application-commands#application-command-object-application-command-naming
        chat_input_pattern = regex.compile(r"^[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}$", regex.UNICODE)

        for param in self.params:
            if param.isupper() or bool(chat_input_pattern.match(param)) is False: # Uppercase parameters are not allowed in the discord API.
                raise errors.InvalidParameter(self, param)

            if param in self.slash_options:
                option_data = self.slash_options[param]
                
                if option_data.get("name") is None:
                    option_data["name"] = param

                options.append(
                    option_data
                )
            
            else:
                options.append({
                    "name": param,
                    "description": "☁️ Option has no description! Sorry." if self.bot.no_description_msg is None else self.bot.no_description_msg,
                    "type": 3,
                    "required": True,
                })

        return options