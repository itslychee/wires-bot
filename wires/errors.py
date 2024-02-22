from __future__ import annotations

import discord
from discord import app_commands


class InvalidEmoji(app_commands.AppCommandError):
    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f"{argument} is not a valid emoji or URL.")