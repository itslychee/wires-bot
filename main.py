import discord
from discord.ext import commands

from utils.bot import WiresBot

bot = WiresBot(command_prefix=commands.when_mentioned_or("wires"), intents=discord.Intents(guilds=True, emojis=True), strip_after_prefix=True)
bot.run()