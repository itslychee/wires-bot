import discord
from discord.ext import commands
from wires import WiresBot

bot = WiresBot(
    command_prefix=commands.when_mentioned_or("wires"),
    intents=discord.Intents(
        guilds=True,
        emojis=True,
        messages=True,
        message_content=True,
    ),
    strip_after_prefix=True
)


def run():
    bot.run()

if __name__ == '__main__':
    run()
