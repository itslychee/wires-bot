from __future__ import annotations
from typing import TYPE_CHECKING
import re


import discord
from discord import app_commands

from wires.errors import InvalidEmoji
from wires.helpers import find_emoji, FindEmojiResult

if TYPE_CHECKING:
    from wires import WiresBot


class AddEmojiTransformer(app_commands.Transformer):
    URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

    async def transform(self, interaction: discord.Interaction[WiresBot], argument: str) -> discord.PartialEmoji | str:
        if url_match := self.URL_REGEX.match(argument):
            return url_match.group(0)
        
        partial = discord.PartialEmoji.from_str(argument)
        if not partial.url:
            raise InvalidEmoji(argument)
        
        return partial

class EmojiTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction[WiresBot], argument: str) -> FindEmojiResult:
        emoji = find_emoji(interaction.client, argument)
        if not emoji:
            raise InvalidEmoji(argument)
        
        return emoji
    
class MultipleEmojiTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction[WiresBot], argument: str) -> list[FindEmojiResult | None]:
        return [find_emoji(interaction.client, e) for e in argument.split(" | ")]
