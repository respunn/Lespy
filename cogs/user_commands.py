# Importing config values from separate file
import asyncio
import math

import discord
from discord.ext import commands
from discord.ext.commands import BucketType, CommandOnCooldown, cooldown

from important_files.config import *
from important_files.connection_to_database import *


class user_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_cooldown_users = set()
        self.progress_cooldown_users = set()
        self.leaderboard_cooldown_users = set()

    @commands.Cog.listener()
    async def on_ready(self):
        print("User commands cog is ready.")

    # Command to show the leaderboard of the top 5 users by level
    @commands.command()
    @cooldown(1, cooldown_duration_commands, BucketType.user)
    async def leaderboard(self, ctx):
        check = False
        embed = discord.Embed(
            title="Leaderboard", description="Top 5 Users by Level", color=0x00C3FF
        )
        c.execute(
            "SELECT name, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT 5"
        )
        result = c.fetchall()
        i = 1
        # Looping through the top 5 users and adding their names, levels, and XP to the embed
        for row in result:
            name = row[0]
            level = row[1]
            xp = row[2]
            if str(name) == str(ctx.author):
                if level == max_level:
                    embed.add_field(
                        name=f"{i}. {name} (You)",
                        value=f"Level: {level}\nReached max level.",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{i}. {name} (You)",
                        value=f"Level: {level}\nXP: {xp}",
                        inline=False,
                    )
                check = True
            else:
                if level == max_level:
                    embed.add_field(
                        name=f"{i}. {name}",
                        value=f"Level: {level}\nReached max level.",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{i}. {name}",
                        value=f"Level: {level}\nXP: {xp}",
                        inline=False,
                    )
            i += 1
        # Checking the rank of the user invoking the command and adding their rank to the embed if they're in the top 5
        c.execute("SELECT name, level, xp FROM users WHERE id = ?", (ctx.author.id,))
        result = c.fetchone()
        if result is not None:
            name = result[0]
            level = result[1]
            xp = result[2]
            c.execute(
                "SELECT COUNT(*) FROM users WHERE level > ? OR (level = ? AND xp > ?)",
                (level, level, xp),
            )
            rank = c.fetchone()[0] + 1
            if check == False:
                if level == max_level:
                    embed.add_field(
                        name=f"{name} (You)",
                        value=f"Level: {level}\nReached max level.\nRank: {rank}",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name=f"{name} (You)",
                        value=f"Level: {level}\nXP: {xp}\nRank: {rank}",
                        inline=False,
                    )
        else:
            embed.add_field(
                name=f"{ctx.author} (You)",
                value=f"You don't have any XP and Level.",
                inline=False,
            )
        await ctx.send(embed=embed)

    # Command to show user's own or tagged user's XP and level progress
    @commands.command()
    @cooldown(1, cooldown_duration_commands, BucketType.user)
    async def progress(self, ctx, user: discord.User = None):
        # If no user is tagged, show progress of the message author
        if user is None:
            user = ctx.author
        cursor = conn.cursor()
        cursor.execute("SELECT xp, level FROM users WHERE id = ?", (user.id,))
        result = cursor.fetchone()
        # If user not found in database, send error message
        if result is None:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name=f"❗ User not found in database.", value="", inline=False
            )
            await ctx.send(embed=embed)
        else:
            xp, level = result
            required_xp = level * 2 * level_xp_multiplier
            required_xp = round(required_xp)
            # Clamping required XP to max and min level XP values
            if required_xp > max_level_experience:
                required_xp = max_level_experience
            elif required_xp < min_level_experience:
                required_xp = min_level_experience
            # Calculating percentage of XP progress
            xp_percentage = int((xp / required_xp) * 100)
            # Calculating remaining XP to next level
            remaining_xp = required_xp - xp
            # Sending progress message
            embed = discord.Embed(color=discord.Color.green())
            # Checking user is at max level or not
            if user == ctx.author:
                if level == max_level:
                    embed.add_field(
                        name=f"📊 Your progress:",
                        value=f"Level: {level}\nYou are at the highest level you can reach!",
                    )
                else:
                    embed.add_field(
                        name=f"📊 Your progress:",
                        value=f"Level: {level}\nXP: {xp}/{required_xp} ({xp_percentage}%)\nRemaining XP to next level: {remaining_xp}",
                    )
            else:
                if level == max_level:
                    embed.add_field(
                        name=f"📊 {user}'s progress:",
                        value=f"Level: {level}\nYou are at the highest level you can reach!",
                    )
                else:
                    embed.add_field(
                        name=f"📊 {user}'s progress:",
                        value=f"Level: {level}\nXP: {xp}/{required_xp} ({xp_percentage}%)\nRemaining XP to next level: {remaining_xp}",
                    )
            await ctx.send(embed=embed)

    # Command that gives information about all commands
    @commands.command()
    @cooldown(1, cooldown_duration_commands, BucketType.user)
    async def help(self, ctx):
        # Dictionary of all the commands and their descriptions
        commands = {
            "!leaderboard": "Displays the leaderboard of the top users in the server based on their level.",
            "!progress @user or user_id [Optional]": "Displays the progress of a specific user in the server towards the next level.\nIf no user is specified, the command will display the progress of the user who invoked the command.",
            "!help": "Shows a list of all the available commands and their descriptions.",
            "!setlevel @user or user_id": "**[Admin Command]** Sets the level of a specific user in the server.",
            "!addxp @user or user_id": "**[Admin Command]** Adds experience points to a specific user in the server.",
            "!showadmins": "**[Admin Command]** Shows a list of all the admins in the database.",
            "!deleteuser @user or user_id": "**[Super Admin Command]** Deletes a specific user's data from the server, including their level and experience points.",
            "!deleteusers": "**[Super Admin Command]** Deletes all user data from the server, including their levels and experience points.",
            "!addadmin @user or user_id": "**[Super Admin Command]** Adds a new admin to the database.",
            "!removeadmin @user or user_id": "**[Super Admin Command]** Removes an admin from the database.",
            "!resetall": "**[Super Admin Command]** Resets the level and XP of all users in the database.",
        }
        # Creating an embed message with the commands and their descriptions
        embed = discord.Embed(
            title="Help",
            description="List of all available commands and their descriptions.",
            color=0x00C3FF,
        )
        for command, description in commands.items():
            embed.add_field(name=command, value=description, inline=False)
        await ctx.send(embed=embed)

    @help.error
    async def command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            user_id = ctx.author.id
            remaining_time = math.ceil(error.retry_after)
            if user_id not in self.help_cooldown_users:
                self.help_cooldown_users.add(user_id)
                remaining_time = math.ceil(error.retry_after)
                embed = discord.Embed(color=discord.Color.orange())
                embed.add_field(
                    name=f"⚠️ {ctx.author} this command is on cooldown for you.",
                    value=f"Please try again in {remaining_time} seconds.",
                    inline=False,
                )
                cooldown_error = await ctx.send(embed=embed)
                await asyncio.sleep(remaining_time)
                await cooldown_error.delete()
                self.help_cooldown_users.remove(user_id)

    @progress.error
    async def command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            user_id = ctx.author.id
            remaining_time = math.ceil(error.retry_after)
            if user_id not in self.progress_cooldown_users:
                self.progress_cooldown_users.add(user_id)
                remaining_time = math.ceil(error.retry_after)
                embed = discord.Embed(color=discord.Color.orange())
                embed.add_field(
                    name=f"⚠️ {ctx.author} this command is on cooldown for you.",
                    value=f"Please try again in {remaining_time} seconds.",
                    inline=False,
                )
                cooldown_error = await ctx.send(embed=embed)
                await asyncio.sleep(remaining_time)
                await cooldown_error.delete()
                self.progress_cooldown_users.remove(user_id)

    @leaderboard.error
    async def command_error(self, ctx, error):
        if isinstance(error, CommandOnCooldown):
            user_id = ctx.author.id
            remaining_time = math.ceil(error.retry_after)
            if user_id not in self.leaderboard_cooldown_users:
                self.leaderboard_cooldown_users.add(user_id)
                remaining_time = math.ceil(error.retry_after)
                embed = discord.Embed(color=discord.Color.orange())
                embed.add_field(
                    name=f"⚠️ {ctx.author} this command is on cooldown for you.",
                    value=f"Please try again in {remaining_time} seconds.",
                    inline=False,
                )
                cooldown_error = await ctx.send(embed=embed)
                await asyncio.sleep(remaining_time)
                await cooldown_error.delete()
                self.leaderboard_cooldown_users.remove(user_id)


def setup(bot):
    bot.add_cog(user_commands(bot))
