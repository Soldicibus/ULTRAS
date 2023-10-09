import disnake
from disnake.ext import commands
from disnake.ext.commands import bot
from disnake.utils import get
import config
import asyncio
import time
from time import strftime
from time import localtime

bot = commands.Bot(command_prefix=config.PREFIX, help_command=None, intents=disnake.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(status=disnake.Status.dnd, activity=disnake.Game(name=".help", type=2))
    print("[!] Logged in as:")
    print("[!] Status: ✅")
    print("[!] The bot is ready to work")

bot.run(config.TOKEN)
