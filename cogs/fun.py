import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

quote_api = "https://api.quotable.io"
joke_api = "https://icanhazdadjoke.com/"

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Fun module has started!")

    @app_commands.command(name="dadjoke", description="Returns a random dad joke")
    async def dadjoke(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session: 
            async with session.get(joke_api, headers={'Accept': 'application/json'}) as response:
                data = await response.json()
                await interaction.response.send_message(f":white_check_mark: Your dad joke: {data['joke']}")

    
async def setup(bot):
    await bot.add_cog(Fun(bot))