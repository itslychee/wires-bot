from __future__ import annotations
from typing import TYPE_CHECKING
import discord

from discord.ext.paginators.button_paginator import ButtonPaginator

if TYPE_CHECKING:
    from .helpers import FindEmojiResult

class EmojiPaginator(ButtonPaginator["FindEmojiResult"]):
    def format_page(self, emoji: FindEmojiResult) -> discord.Embed:
        emb = discord.Embed(
            title=emoji.name,
            url=emoji.url,
            description=f"[Copy URL]({emoji.url})",
            color=discord.Color.blurple(),
        )
        emb.set_image(url=emoji.url)
        if emoji.id:
            emb.description += f"\n**ID**: {emoji.id} | **Animated:** {emoji.animated}"  # type: ignore

        return emb
    