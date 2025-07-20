import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random, string

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Moderation module started!")

    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(member="Member that will be kicked", reason="Reason for kicking the member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(":x: You can not use this command.", ephemeral=True)
            return

        embed = discord.Embed(colour=0xFF2222, title=f":x: You have been kicked from {interaction.guild.name}", description=f"You have been kicked from {interaction.guild.name}. If you believe that this was a false kick, you can appeal it at [BL Appeals](https://discord.gg/idkyet)")
        embed.add_field(name="Moderator", value=f"```{interaction.user.name}```", inline=True)
        embed.add_field(name="Date and Time", value=f"```{datetime.datetime.now().replace(microsecond=0)}```", inline=True)
        embed.add_field(name="Reason", value=f"```{reason}```", inline=True)
        embed.add_field(name="Unique Kick ID", value=f"```{''.join(random.choices(string.ascii_lowercase + string.digits, k=16))}```", inline=True)

        try:
            await member.send(embed=embed)
            await member.kick()
            await interaction.response.send_message(f":white_check_mark: {member.name} just got kicked, say bye!", ephemeral=True)
        except Exception as e:
            print(f"Silently failing - {e}")