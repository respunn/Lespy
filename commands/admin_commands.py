# Importing config values from separate file
import discord
from discord.ext import commands

from important_files.config import *
from important_files.connection_to_database import *

class admin_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Command to set a user's level
    @commands.command()
    async def setlevel(self, ctx, mentioned_user: discord.User, level_from_user: int):
        # Checking if the user invoking the command is an admin
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        if result is not None or str(ctx.author.id) in super_admin_ids:
            if mentioned_user == None:
                # If user didn't mention someone or put user's id, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"❌ You need to mention user or put user's id.", value="", inline=False)
                await ctx.send(embed=embed)
            elif level_from_user == None:
                # If user didn't put xp amount, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"❌ You need to put level.", value="", inline=False)
                await ctx.send(embed=embed)
            else:
                cursor = conn.cursor()
                cursor.execute('SELECT xp, level FROM users WHERE id = ?', (mentioned_user.id,))
                result = cursor.fetchone()
                check = 0
                # Clamping level to max level if it exceeds the max level
                if level_from_user > max_level:
                    level_from_user = max_level
                    check = 1
                if level_from_user < min_level:
                    level_from_user = min_level
                    check = 2
                # If user not found in database, insert new user with specified level and default XP
                if result is None:
                    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (mentioned_user.id, str(mentioned_user), level_from_user, 0))
                    conn.commit()
                    # Sending confirmation message
                    # Check if the user's level is within the defined minimum and maximum levels
                    if check == 0:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ {mentioned_user}'s level has been set to {level_from_user}.", value="", inline=False)
                        embed.set_footer(text=f"{mentioned_user} has been added to the database.")
                        await ctx.send(embed=embed)
                    # Check if the user's level is greater than the defined maximum level
                    elif check == 1:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ {mentioned_user}'s level has been set to {level_from_user}.", value="", inline=False)
                        embed.set_footer(text=f"{mentioned_user} has been added to the database.\nMax level set to {max_level}.")
                        await ctx.send(embed=embed)
                    # Check if the user's level is less than the defined minimum level
                    else:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ {mentioned_user}'s level has been set to {level_from_user}.", value="", inline=False)
                        embed.set_footer(text=f"{mentioned_user} has been added to the database.\nMin level set to {min_level}.")
                        await ctx.send(embed=embed)
                # If user found in database, update their level and reset their XP to 0
                else:
                    cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (0, level_from_user, mentioned_user.id))
                    conn.commit()
                    # Sending confirmation message
                    # Check if the user's level is within the defined minimum and maximum levels
                    if check == 0:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ **{mentioned_user}**'s level has been set to {level_from_user}.", value="", inline=False)
                        await ctx.send(embed=embed)
                    # Check if the user's level is greater than the defined maximum level
                    elif check == 1:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ {mentioned_user}'s level has been set to {level_from_user}.", value="", inline=False)
                        embed.set_footer(text=f"Max level set to {max_level}.")
                        await ctx.send(embed=embed)
                    # Check if the user's level is less than the defined minimum level
                    else:
                        embed = discord.Embed(color=discord.Color.green())
                        embed.add_field(name=f"✅ {mentioned_user}'s level has been set to {level_from_user}.", value="", inline=False)
                        embed.set_footer(text=f"Min level set to {min_level}.")
                        await ctx.send(embed=embed)
        # If user invoking the command is not an admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
            await ctx.send(embed=embed)

    # Command to add XP to a user
    @commands.command()
    async def addxp(self, ctx, mentioned_user: discord.User, xp_amount_from_user: int):
        # Checking if the user invoking the command is an admin
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        if result is not None or str(ctx.author.id) in super_admin_ids:
            if mentioned_user == None:
                # If user didn't mention someone or put user's id, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"❌ You need to mention user or put user's id.", value="", inline=False)
                await ctx.send(embed=embed)
            elif xp_amount_from_user == None:
                # If user didn't put xp amount, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"❌ You need to put xp amount.", value="", inline=False)
                await ctx.send(embed=embed)
            else:
                cursor = conn.cursor()
                cursor.execute('SELECT xp, level FROM users WHERE id = ?', (mentioned_user.id,))
                result = cursor.fetchone()
                # If user not found in database, insert new user with default level and specified XP
                if result is None:
                    level = 1
                    xp = xp_amount_from_user
                    required_xp = level * 2 * level_xp_multiplier
                    required_xp = round(required_xp)
                    if required_xp > max_level_experience:
                        required_xp = max_level_experience
                    elif required_xp < min_level_experience:
                        required_xp = min_level_experience
                    while xp >= required_xp:
                        level += 1
                        xp = xp - required_xp
                    cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (mentioned_user.id, str(mentioned_user), level, xp))
                    conn.commit()
                    # Sending confirmation message
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(name=f"✅ Added {xp_amount_from_user} xp to {mentioned_user}.", value="", inline=False)
                    embed.set_footer(text=f"{mentioned_user} has been added to the database.")
                    await ctx.send(embed=embed)
                # If user found in database, update their XP and level accordingly
                else:
                    xp, level = result
                    xp += xp_amount_from_user
                    required_xp = level * 2 * level_xp_multiplier
                    required_xp = round(required_xp)
                    if required_xp > max_level_experience:
                        required_xp = max_level_experience
                    elif required_xp < min_level_experience:
                        required_xp = min_level_experience
                    while xp >= required_xp:
                        level += 1
                        xp = xp - required_xp
                    if level >= max_level:
                        level = max_level
                        xp = 0
                    cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, mentioned_user.id))
                    conn.commit()
                    # Sending confirmation message
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(name=f"✅ Added {xp_amount_from_user} xp to {mentioned_user}.", value="", inline=False)
                    await ctx.send(embed=embed)
        # If user invoking the command is not an admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
            await ctx.send(embed=embed)
    
    
    # Command to show all admins from the database
    @commands.command()
    async def showadmins(self, ctx):
        # Checking if the user invoking the command is an admin
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE id = ?', (ctx.author.id,))
        result = cursor.fetchone()
        if result is not None or str(ctx.author.id) in super_admin_ids:
            cursor = conn.cursor()
            # Fetching all the admins from the database
            cursor.execute('SELECT id, name FROM admins')
            result = cursor.fetchall()
            if not result:
                # If there are no admins in the database, send error message
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="❌ There are no admins in the database.", value="", inline=False)
                await ctx.send(embed=embed)
            else:
                # Creating an embed message with the list of admins
                embed = discord.Embed(title="Admin List", description="List of all admins", color=0x00c3ff)
                for row in result:
                    embed.add_field(name=f"ID: {row[0]}", value=f"Name: {row[1]}", inline=False)
                await ctx.send(embed=embed)
        # If user invoking the command is not an admin, send error message
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(admin_commands(bot))