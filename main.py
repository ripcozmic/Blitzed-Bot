import discord
from discord.ext import commands
import os
import asyncio
import json

conf = 'config.json'
config = None

with open(conf, 'r') as c:
    config = json.load(c)

token = config["bot"]["TOKEN"]
logging = config["bot"]["logging"]

bot = commands.Bot(command_prefix="!", help_command=None, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (UID: {bot.user.id})")

    try:
        synced = await bot.tree.sync()
        print(f"Successfully synced {len(synced)} 'slash' commands")
    except Exception as e:
        print(f"Unexpected error occured - {e}")

async def load_cogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f'cogs.{file[:-3]}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

asyncio.run(main())