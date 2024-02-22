import discord

from utils.bot import WiresBot

bot = WiresBot(command_prefix="wires", intents=discord.Intents.all(), strip_after_prefix=True)
bot.run()