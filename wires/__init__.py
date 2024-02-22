from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Iterable, Union

import logging
import pathlib

import aiohttp

import discord
from discord.ext import commands

try:
    import tomllib  # type: ignore # >=3.11  # noqa: F401
except ImportError: # <3.11
    import tomli as tomllib

if TYPE_CHECKING:
    from typing_extensions import Self


class WiresBot(commands.Bot):
    user: discord.ClientUser  # type: ignore # annoying, it shouldn't be None
    session: aiohttp.ClientSession

    def __init__(
        self,
        command_prefix: Union[Iterable[Any], Callable[[Self, discord.Message], Iterable[Any]]],
        intents: discord.Intents,
        strip_after_prefix: bool = True,
        **options: Any,
    ) -> None:
        options["owner_ids"] = options.get("owner_ids", self.config["bot"]["owners"])
        super().__init__(
            command_prefix,
            intents=intents,
            strip_after_prefix=strip_after_prefix,
            **options
        )

    @property
    def config(self) -> dict[str, Any]:
        with open("config.toml", "r", encoding="utf-8") as file:
            return tomllib.loads(file.read())  # type: ignore

    async def setup_hook(self) -> None:
        logging.info(
            f"Logged in as {self.user} ({self.user.id}) with discord.py {discord.__version__}\n"
            f"Owner(s): {', '.join(str(owner) for owner in self.owner_ids or [])}\n"

        )
        self.session = aiohttp.ClientSession()

        await self.load_extension("jishaku")
        logging.info("Loaded extension jishaku")

        for ext in pathlib.Path("wires/exts").glob("**/*.py"):
            ext = str(ext.with_suffix("")).replace("/", ".")
            print(ext)
            await self.load_extension(ext)
            logging.info(f"Loaded extension {ext}")

    async def close(self) -> None:
        await self.session.close()
        await super().close()

    def run(
        self,
        token: str | None = None,
        **kwargs: Any,
    ) -> None:
        kwargs["root_logger"] = kwargs.get("root_logger", True)
        super().run(token or self.config["bot"]["token"], **kwargs)
