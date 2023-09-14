# Importing config values from separate file
import asyncio

import discord
from discord.ext import commands

from important_files.config import *
from important_files.connection_to_database import *


class super_admin_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Super admin commands cog is ready.")

    # Command to add a new admin to the database
    @commands.command()
    async def addadmin(self, ctx, mentioned_user: discord.User = None):
        # Checking if the user invoking the command is a super admin
        if str(ctx.author.id) in super_admin_ids:
            if mentioned_user == None:
                # If user didn't mention someone or put user's id, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(
                    name=f"❌ You need to mention user or put user's id.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                cursor = conn.cursor()
                # Checking if the user is already an admin
                cursor.execute(
                    "SELECT * FROM admins WHERE id = ?", (mentioned_user.id,)
                )
                result = cursor.fetchone()
                # If user is already an admin, send error message
                if result is not None:
                    embed = discord.Embed(color=discord.Color.red())
                    embed.add_field(
                        name=f"❌ {mentioned_user} is already an admin.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                # If user is not an admin, add user as an admin to the database
                else:
                    cursor.execute(
                        "INSERT INTO admins (id, name) VALUES (?, ?)",
                        (mentioned_user.id, str(mentioned_user)),
                    )
                    conn.commit()
                    # Sending confirmation message
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(
                        name=f"✅ {mentioned_user} has been added as an admin.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
        # If user invoking the command is not a super admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name=f"⛔ You don't have enough permission for this command.",
                value="",
                inline=False,
            )
            await ctx.send(embed=embed)

    # Command to remove an admin from the database
    @commands.command()
    async def removeadmin(self, ctx, mentioned_user: discord.User = None):
        # Checking if the user invoking the command is an admin
        if str(ctx.author.id) in super_admin_ids:
            if mentioned_user == None:
                # If user didn't mention someone or put user's id, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(
                    name=f"❌ You need to mention user or put user's id.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                # Removing the mentioned_user ID from the list of admin IDs
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM admins WHERE id = ?", (mentioned_user.id,)
                )
                result = cursor.fetchone()
                if result is not None:
                    cursor.execute(
                        "DELETE FROM admins WHERE id = ?", (mentioned_user.id,)
                    )
                    conn.commit()
                    # Sending confirmation message
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(
                        name=f"✅ {mentioned_user} is no longer an admin.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                else:
                    # Sending error message if mentioned_user is not found in the database
                    embed = discord.Embed(color=discord.Color.red())
                    embed.add_field(
                        name=f"⛔ {mentioned_user} is not an admin.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
        else:
            # If user invoking the command is not a super admin, send error message
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name=f"⛔ You don't have enough permission for this command.",
                value="",
                inline=False,
            )
            await ctx.send(embed=embed)

    # Command that resets the level and XP of all users in the database
    @commands.command()
    async def resetall(self, ctx):
        # Checking if the user invoking the command is a super admin
        if str(ctx.author.id) in super_admin_ids:
            cursor = conn.cursor()
            # Warning message to confirm action
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name="⚠️ WARNING: This action will reset all users' levels and XP. Are you sure?",
                value="",
                inline=False,
            )
            warning = await ctx.send(embed=embed)
            # Waiting for confirmation from user
            await warning.add_reaction("✅")
            await warning.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda reaction, user: user == ctx.author
                    and str(reaction.emoji) in ["✅", "❌"],
                )
                # Checking if the user reacting is a super admin
                if str(user.id) not in super_admin_ids:
                    return
            except asyncio.TimeoutError:
                await warning.delete()
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(
                    name="❌ Command timed out. Please try again.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                # If user confirms action, reset all user levels and XP in the database
                if str(reaction.emoji) == "✅":
                    cursor.execute("UPDATE users SET level = 0, xp = 0")
                    conn.commit()
                    # Sending confirmation message with the name of the super admin who did it
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(
                        name=f"✅ All users' levels and XP have been reset by {user}.",
                        value=f"ID: {user.id}",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                # If user cancels action, send error message
                elif str(reaction.emoji) == "❌":
                    await warning.delete()
                    embed = discord.Embed(color=discord.Color.red())
                    embed.add_field(
                        name="❌ Command cancelled. No changes have been made.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
        # If user invoking the command is not a super admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name=f"⛔ You don't have enough permission for this command.",
                value="",
                inline=False,
            )
            await ctx.send(embed=embed)

    # Command to delete a user from the database
    @commands.command()
    async def deleteuser(self, ctx, mentioned_user: discord.User):
        if str(ctx.author.id) in super_admin_ids:
            if mentioned_user == None:
                # If user didn't mention someone or put user's id, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(
                    name=f"❌ You need to mention user or put user's id.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (mentioned_user.id,))
                conn.commit()
                # Sending confirmation message
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(
                    name=f"✅ {mentioned_user} has been deleted from the database.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
        # If user invoking the command is not a super admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name=f"⛔ You don't have enough permission for this command.",
                value="",
                inline=False,
            )
            await ctx.send(embed=embed)

    # Command to delete all users from the database
    @commands.command()
    async def deleteusers(self, ctx):
        if str(ctx.author.id) in super_admin_ids:
            cursor = conn.cursor()
            # Warning message to confirm action
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name="⚠️ WARNING: This action will delete all users with their levels and XP. Are you sure?",
                value="",
                inline=False,
            )
            warning = await ctx.send(embed=embed)
            # Waiting for confirmation from user
            await warning.add_reaction("✅")
            await warning.add_reaction("❌")
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=60.0,
                    check=lambda reaction, user: user == ctx.author
                    and str(reaction.emoji) in ["✅", "❌"],
                )
                # Checking if the user reacting is a super admin
                if str(user.id) not in super_admin_ids:
                    return
            except asyncio.TimeoutError:
                await warning.delete()
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(
                    name="❌ Command timed out. Please try again.",
                    value="",
                    inline=False,
                )
                await ctx.send(embed=embed)
            else:
                # If user confirms action, delete all user from the database
                if str(reaction.emoji) == "✅":
                    cursor.execute("DELETE FROM users")
                    conn.commit()
                    # Sending confirmation message with the name of the super admin who did it
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(
                        name=f"✅ All users have been deleted from the database by {user}.",
                        value=f"ID: {user.id}",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                # If user cancels action, send error message
                elif str(reaction.emoji) == "❌":
                    await warning.delete()
                    embed = discord.Embed(color=discord.Color.red())
                    embed.add_field(
                        name="❌ Command cancelled. No changes have been made.",
                        value="",
                        inline=False,
                    )
                    await ctx.send(embed=embed)
        # If user invoking the command is not a super admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(
                name="⛔ You don't have enough permission for this command.",
                value="",
                inline=False,
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(super_admin_commands(bot))
