from __future__ import annotations
from typing import TYPE_CHECKING

import aiohttp

import discord
from discord import app_commands
from discord.ext import commands

from wires.helpers import FindEmojiResult, resize_for_emoji
from wires.transformers import AddEmojiTransformer, EmojiTransformer, MultipleEmojiTransformer
from wires.views import Confirm
from wires.paginators import EmojiPaginator


if TYPE_CHECKING:
    from wires import WiresBot


@app_commands.guild_only()
class Emojis(commands.GroupCog,):
    def __init__(self, bot: WiresBot) -> None:
        self.bot: WiresBot = bot

    # subcommands can't have individual perms atm
    # so we need to check for it in the command.
    def _has_permissions(self, interaction: discord.Interaction[WiresBot]) -> bool:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            raise ValueError("This command can only be used in a server.")
        
        if not interaction.guild.me.guild_permissions.manage_emojis:
            raise ValueError("I'm missing the `manage_emojis` permission.")
        
        if not interaction.user.guild_permissions.manage_emojis:
            raise ValueError("You're missing the `manage_emojis` permission.")  

        return True      

    async def _add_emoji(
        self,
        interaction: discord.Interaction[WiresBot],
        /,
        name: str,
        image: bytes,
        reason: str,
    ) -> discord.Emoji | None:
        if not interaction.guild:
            raise ValueError("This command can only be used in a server.")
        
        added_emoji: discord.Emoji | None = None

        try:
            added_emoji = await interaction.guild.create_custom_emoji(name=name, image=image, reason=reason)
        except discord.Forbidden:
            await interaction.followup.send("**Error!**\nMissing permissions `manage_emojis`")
            return
        except TypeError:
            await interaction.followup.send("Invalid image type. Only PNG, JPEG and GIF are supported.", ephemeral=True)
            return
        except discord.HTTPException as e:
            if e.code in (50045, 40005, 50035):
                main = "❌ **Error!**\nThe file is larger than 256kb.\n"
                ask = "**Would you like me to try and resize the image to the correct size?**"
                view = Confirm(interaction.user.id)
                view.message = await interaction.followup.send(main + ask, wait=True, ephemeral=True, view=view)

                await view.wait()
                if view.value is None:
                    await interaction.edit_original_response(content=f"{main}~~{ask}~~ Timed out.")
                    return
                if view.value is False:
                    await interaction.edit_original_response(content=f"{main}~~{ask}~~ Cancelled.")
                    return
                
                right_size = await resize_for_emoji(image)
                return await self._add_emoji(interaction, name=name, image=right_size.read(), reason=reason)

            elif e.code == 30008:
                return await interaction.followup.send("❌ **Error!**\nMaximum amount of static emojis reached.", ephemeral=True)
            elif e.code == 30018:
                return await interaction.followup.send("❌ **Error!**\nMaximum amount of animated emojis reached.", ephemeral=True)

            else:
                raise e

        return added_emoji


    @app_commands.command(name="add")
    @app_commands.rename(emoji_url="emoji-or-url")
    async def emoji_add(
        self,
        interaction: discord.Interaction[WiresBot],
        name: str,
        emoji_url: app_commands.Transform[discord.PartialEmoji | str, AddEmojiTransformer],
        reason: str | None = None,
    ):
        """Add a emoji to the server. Provide a valid emoji or URL."""
        try:
            self._has_permissions(interaction)
        except ValueError as e:
            return await interaction.response.send_message(str(e), ephemeral=True)

        if not interaction.guild:
            return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

        await interaction.response.defer()

        reason = f"[{interaction.user}] {reason or 'No reason given.'}"
        added_emoji: discord.Emoji | None = None

        if isinstance(emoji_url, discord.PartialEmoji):
            url = emoji_url.url
        else:
            url = emoji_url.strip("<>")

        try:
            async with self.bot.session.get(url) as response:
                if response.status != 200:
                    return await interaction.response.send_message("The URL you have provided is invalid.", ephemeral=True)

                response = await response.read()

        except aiohttp.InvalidURL:
            return await interaction.followup.send("The URL you have provided is invalid.", ephemeral=True)
        
        try:
            added_emoji = await self._add_emoji(interaction, name=name, image=response, reason=reason)
        except Exception as e:
            return await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
        
        if not added_emoji:
            return await interaction.followup.send("Something went wrong while adding the emoji. Try again later.", ephemeral=True)

        emb = discord.Embed(
            title=f"✅ **Added Emoji** | **ID**: {added_emoji.id}",
            description=f"**Name**: {added_emoji.name} - [Copy URL]({added_emoji.url})\n"
            f"**Animated?**: {added_emoji.animated}\n**Added by**: {interaction.user}\n"
            f"**Created at**: {discord.utils.format_dt(added_emoji.created_at)}\n",
            color=interaction.user.color,
        )
        emb.set_image(url=added_emoji.url)
        
        await interaction.followup.send(embed=emb)

    @app_commands.command(name="view")
    async def emoji_view(
        self,
        interaction: discord.Interaction[WiresBot],
        emojis: app_commands.Transform[list[FindEmojiResult | None], MultipleEmojiTransformer]
    ):
        """Search for emojis. Split multiple emojis with ` | `."""
        _emojis = [e for e in emojis if e]
        if not _emojis:
            return await interaction.response.send_message("No valid emojis found.", ephemeral=True)

        pag = EmojiPaginator(_emojis, per_page=1)
        await pag.send(interaction)

    @app_commands.command(name="copy")
    @commands.has_permissions(manage_emojis=True)
    async def emoji_copy(self, interaction: discord.Interaction[WiresBot], emoji: app_commands.Transform[FindEmojiResult, EmojiTransformer]):
        """Copy a emoji from any server i'm in."""
        try:
            self._has_permissions(interaction)
        except ValueError as e:
            return await interaction.response.send_message(str(e), ephemeral=True)
        
        added_emoji: discord.Emoji | None = None
        await interaction.response.defer()
        try:
            if emoji.obj:
                added_emoji = await self._add_emoji(interaction, name=emoji.name, image=await emoji.obj.read(), reason=f"Copy of {emoji.name}")
            else:
                async with self.bot.session.get(emoji.url) as response:
                    response = await response.read()

                added_emoji = await self._add_emoji(interaction, name=emoji.name, image=response, reason=f"Copy of {emoji.name}")
        except Exception as e:
            return await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

        if not added_emoji:
            return await interaction.followup.send("Something went wrong while adding the emoji. Try again later.", ephemeral=True)

        emb = discord.Embed(
            title=f"✅ **Emoji Copied** | **ID**: {added_emoji.id}",
            description=f"**Name**: {added_emoji.name} - [Copy URL]({added_emoji.url})\n"
            f"**Animated?**: {added_emoji.animated}\n**Copied by**: {interaction.user}\n"
            f"**Created at**: {discord.utils.format_dt(added_emoji.created_at)}\n",
        )
        emb.set_image(url=added_emoji.url)

        return await interaction.followup.send(embed=emb)
    

async def setup(bot: WiresBot):
    await bot.add_cog(Emojis(bot))
