from __future__ import annotations
from typing import TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from typing_extensions import Self


class Confirm(discord.ui.View):
    message: discord.Message

    def __init__(self, author_id: int, *, timeout: float | None = 60.0) -> None:
        super().__init__(timeout=timeout)
        self.value: bool | None = None

        self.author_id: int = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message('This is not for you!', ephemeral=True)
            return False
        
        return True
    
    async def on_timeout(self) -> None:
        try:
            await self.message.edit(view=None, content="Timed out", embed=None, attachments=[])
        except discord.NotFound:
            pass

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _: discord.ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, _: discord.ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.value = False
        self.stop()
