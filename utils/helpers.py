from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Awaitable, Any, NamedTuple

import re
import asyncio
import functools

from PIL import Image
from io import BytesIO

import discord

if TYPE_CHECKING:
    from .bot import WiresBot

AsyncExecutorReturnType = Callable[[Callable[..., Any]], Callable[..., Awaitable[Any]]]

def async_executor() -> AsyncExecutorReturnType:
    def decorator(func: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Awaitable[asyncio.Future[Any]]:
            return asyncio.to_thread(func, *args, **kwargs)

        return wrapper

    return decorator


@async_executor()
def resize_for_emoji(img):
    with Image.open(BytesIO(img)) as my_image:
        my_image = my_image.resize((256, 256), resample=Image.LANCZOS)
        output_buffer = BytesIO()
        my_image.save(output_buffer, "png")
        output_buffer.seek(0)
    return output_buffer

class FindEmojiResult(NamedTuple):
    name: str
    url: str
    id: int | None = None
    guild_name: str | None = None
    animated: bool = False
    obj: discord.Emoji | None = None


def find_emoji(bot: WiresBot, content: str) -> FindEmojiResult | None:
    msg = re.sub("<a?:(.+):([0-9]+)>", "\\2", content)
    color_modifiers = [
        "1f3fb",
        "1f3fc",
        "1f3fd",
        "1f44c",
        "1f3fe",
        "1f3ff",
    ]  # These color modifiers aren't in Twemoji

    name = None

    for emoji in bot.emojis:
        if msg.strip().lower() in (str(emoji.id), emoji.name.lower()):
            name = emoji.name + (".gif" if emoji.animated else ".png")
            url = emoji.url
            eid = emoji.id
            guild_name = emoji.guild and emoji.guild.name
            animated = emoji.animated

            return FindEmojiResult(name, url, eid, guild_name, animated, obj=emoji)

    # Here we check for a stock emoji before returning a failure
    codepoint_regex = re.compile(r"([\d#])?\\\\[xuU]0*([a-f\d]*)")
    unicode_raw = msg.encode("unicode-escape").decode("ascii")
    codepoints = codepoint_regex.findall(unicode_raw)
    if codepoints == []:
        return None

    if len(codepoints) > 1 and codepoints[1][1] in color_modifiers:
        codepoints.pop(1)

    if codepoints[0][0] == "#":
        emoji_code = "23-20e3"
    elif codepoints[0][0] == "":
        codepoints = [x[1] for x in codepoints]
        emoji_code = "-".join(codepoints)
    else:
        emoji_code = "3{}-{}".format(codepoints[0][0], codepoints[0][1])

    url = f"https://raw.githubusercontent.com/astronautlevel2/twemoji/gh-pages/128x128/{emoji_code}.png"
    name = "emoji.png"

    return FindEmojiResult(name, url)