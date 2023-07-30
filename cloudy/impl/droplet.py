from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord_typings import InteractionData

__all__ = ("Droplet",)

# Idk if this is how I want to do it.

class Droplet():
    def __init__(self, data: InteractionData) -> None:
        self.data = data