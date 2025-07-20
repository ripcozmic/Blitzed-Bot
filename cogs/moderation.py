import discord
from discord import app_commands
from discord.ext import commands
import datetime
import random, string, json, os
import sqlite3

conf = 'config.json'
config = None

with open(conf, 'r') as c:
    config = json.load(c)

path = config["database"]["file"]

class Moderation(commands.Cog):
    def __init__(self, bot, path):
        self.bot = bot
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()
        self._setup_base()
        print("Moderation module started!")

    def _setup_base(self):
        self.cursor.executescript("""   
            CREATE TABLE IF NOT EXISTS kicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                unique_id TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS bans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                unique_id TEXT NOT NULL
            );
        """)
        self.conn.commit()

    @app_commands.command(name="kick", description="Kicks a member from the server")
    @app_commands.describe(member="Member that will be kicked", reason="Reason for kicking the member")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(":x: You can not use this command.", ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(":x: This user has a higher role than me!", ephemeral=True)
            return
        
        kick_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        self.cursor.execute(
            "INSERT INTO kicks (user_id, moderator_id, reason, unique_id) VALUES (?, ?, ?, ?)",
            (member.id, interaction.user.id, reason, kick_id)
        )
        self.conn.commit()

        embed = discord.Embed(colour=0xFF2222, title=f":x: You have been kicked from {interaction.guild.name}", description=f"You have been kicked from {interaction.guild.name}. If you believe that this was a false kick, you can appeal it at [BL Appeals](https://discord.gg/idkyet)")
        embed.add_field(name="Moderator", value=f"```{interaction.user.name}```", inline=True)
        embed.add_field(name="Date and Time", value=f"```{datetime.datetime.now().replace(microsecond=0)}```", inline=True)
        embed.add_field(name="Reason", value=f"```{reason}```", inline=True)
        embed.add_field(name="Unique Kick ID", value=f"```{kick_id}```", inline=True)

        try:
            await member.send(embed=embed)
        except Exception as e:
            print(f"DM failed - {e}")

        try:
            await member.kick()
            await interaction.response.send_message(f":white_check_mark: {member.name} just got kicked, say bye!", ephemeral=True)
        except Exception as e:
            print(f"Silently failing - {e}")

    @app_commands.command(name="ban", description="Bans a member from the server")
    @app_commands.describe(member="Member that will be banned", reason="Reason for banning the member")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "None"):
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(":x: You can not use this command.", ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message(":x: This user has a higher role than me!", ephemeral=True)
            return

        ban_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        self.cursor.execute(
            "INSERT INTO bans (user_id, moderator_id, reason, unique_id) VALUES (?, ?, ?, ?)",
            (member.id, interaction.user.id, reason, ban_id)
        )
        self.conn.commit()

        embed = discord.Embed(colour=0xFF2222, title=f":x: You have been banned from {interaction.guild.name}", description=f"You have been banned from {interaction.guild.name}. If you believe that this was a false ban, you can appeal it at [BL Appeals](https://discord.gg/idkyet)")
        embed.add_field(name="Moderator", value=f"```{interaction.user.name}```", inline=True)
        embed.add_field(name="Date and Time", value=f"```{datetime.datetime.now().replace(microsecond=0)}```", inline=True)
        embed.add_field(name="Reason", value=f"```{reason}```", inline=True)
        embed.add_field(name="Unique Ban ID", value=f"```{ban_id}```", inline=True)

        try:
            await member.send(embed=embed)
        except Exception as e:
            print(f"DM failed - {e}")

        try:
            await member.ban()
            await interaction.response.send_message(f":white_check_mark: {member.name} just got banned, say bye!", ephemeral=True)
        except Exception as e:
            print(f"Silently failing - {e}")

    @app_commands.command(name="checkkick", description="Checks a kick")
    @app_commands.describe(unique_id="Unique Kick ID, only works with this bot.")
    async def checkkick(self, interaction: discord.Interaction, unique_id: str):
        member = interaction.guild.get_member(interaction.user.id)
        if 1396507757728759892 not in [role.id for role in member.roles]:
            await interaction.response.send_message(":x: You are not a guard.", ephemeral=True)
            return
        
        self.cursor.execute(
            "SELECT user_id, moderator_id, reason, timestamp FROM kicks WHERE unique_id = ?",
            (unique_id,))
        record = self.cursor.fetchone()

        uid, mod_id, reason, timestamp = record

        user = await self.bot.fetch_user(uid)
        name = user.name

        mod = await self.bot.fetch_user(mod_id)
        mod_name = mod.name

        embed = discord.Embed(colour=0xFF2222, title=f":white_check_mark: Check kick @ {interaction.guild.name}", description=f"You are checking a kick in {interaction.guild.name}. If you believe that this was a false kick, you can re-invite the user.")
        embed.add_field(name="User", value=f"```{name} (UID: {uid})```", inline=True)
        embed.add_field(name="Moderator", value=f"```{mod_name} (UID: {mod_id})```", inline=True)
        embed.add_field(name="Date and Time", value=f"```{timestamp}```", inline=True)
        embed.add_field(name="Reason", value=f"```{reason}```", inline=True)
        embed.add_field(name="Unique Ban ID", value=f"```{unique_id}```", inline=True)

        try:
            interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Failed! {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot, path=path))