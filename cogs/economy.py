import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import random

def draw_card():
    return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])

class BlackjackGame:
    def __init__(self):
        self.cards = [draw_card(), draw_card()]
        self.total = sum(self.cards)

    def hit(self):
        new_card = draw_card()
        self.cards.append(new_card)
        self.total = sum(self.cards)
        return new_card
    
    def is_bust(self):
        return self.total > 21    
    
    def get_embed(self):
        embed = discord.Embed(
            title="Blackjack",
            color=discord.Color.dark_green()
        )
        embed.add_field(name="Your cards", value=f"```{self.cards}```", inline=True)
        embed.add_field(name="Card sum", value=f"```{self.total}```", inline=True)
        if self.is_bust():
            embed.set_footer(text="Bust!")
            embed.color = discord.Color.red()
        
        return embed

class BlackjackView(View):
    def __init__(self, game: BlackjackGame):
        super().__init__(timeout=60)
        self.game = game

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, interaction: discord.Interaction, button: Button):
        card = self.game.hit()
        if self.game.is_bust():
            await interaction.response.edit_message(embed=self.game.get_embed(), view=None)
        elif self.game.total == 21:
            await interaction.response.edit_message(embed=self.game.get_embed(), view=None)
        else:
            await interaction.response.send_message(embed=self.game.get_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.danger)
    async def stand(self, interaction: discord.Interaction, button: Button):
        embed = self.game.get_embed()
        embed.set_footer(text=f"You stood at {self.game.total}. (Dealer not implemented)")
        await interaction.response.edit_message(embed=embed, view=None)

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Economy module has started!")

    @app_commands.command(name="blackjack", description="Starts a blackjack game (Dealer still not implemented.)")
    async def blackjack(self, interaction: discord.Interaction):
        game = BlackjackGame()
        view = BlackjackView(game)
        embed = game.get_embed()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Economy(bot))