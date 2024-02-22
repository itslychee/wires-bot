import discord

from utils.bot import WiresBot

bot = WiresBot(command_prefix=(), intents=discord.Intents(guilds=True, emojis=True), strip_after_prefix=True)
bot.run()