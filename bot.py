# Importing necessary modules
import discord
from discord.ext import commands
import asyncio
import sqlite3

# Connecting to database
try:
    conn = sqlite3.connect('level_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, name TEXT, level INTEGER, xp INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins
                (id INTEGER PRIMARY KEY, name TEXT)''')
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")

# Getting bot token from environment variables
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Creating bot instance
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')

# Bot ready event listener
@bot.event
async def on_ready():
    # Setting bot status and activity
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
    # Printing bot's name and ID to console
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))

# Importing config values from separate file
from config import *

# Message event listener for XP system
@bot.event
async def on_message(message):
    # Return if the message is sent by the bot itself
    if message.author == bot.user:
        return
    # Check if the message contains any of the WORDS
    elif any(word in message.content.lower() for word in WORDS):
        # Check if the message is a reply or mentions the message author
        is_reply_or_mention = False
        if message.reference:
            # Fetch the referenced message and check if its author is the message author
            try:
                referenced_msg = await message.channel.fetch_message(message.reference.message_id)
                is_reply_or_mention = referenced_msg.author == message.author
            except discord.errors.NotFound:
                pass
        else:
            # Check if the message mentions the message author
            is_reply_or_mention = any(user.id == message.author.id for user in message.mentions)
        # Do not give xp if message author replies or mentions themselves
        if is_reply_or_mention:
            return
        user = None
        # Extracting the user who is tagged or replied to in the message
        if message.reference and not is_reply_or_mention:
            referenced_msg = await message.channel.fetch_message(message.reference.message_id)
            if referenced_msg.author.id != message.author.id:
                user = referenced_msg.author
        elif message.mentions:
            user = message.mentions[0]
        # If a valid user is found, add xp and level up accordingly
        if user:
            cursor = conn.cursor()
            cursor.execute('SELECT xp, level FROM users WHERE id = ?', (user.id,))
            result = cursor.fetchone()
            if result is None:
                # Insert new user with default level and xp if not found in the database
                cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (user.id, str(user), 0, min_level))
                conn.commit()
            else:
                # Add 1 xp to the user's current xp
                xp, level = result
                xp += 1
                required_xp = level * 2 * level_xp_multiplier
                required_xp = round(required_xp)
                # Check if required xp is within the defined range
                if required_xp > max_level_experience:
                    required_xp = max_level_experience
                elif required_xp < min_level_experience:
                    required_xp = min_level_experience
                # Level up and send an embed message if required xp is reached
                if xp >= required_xp:
                    level += 1
                    xp = xp - required_xp
                    channel = message.channel
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(name=f"🎉 You've leveled up {user.name}, congratulations!", value="", inline=False)
                    embed.set_footer(text=f"Your current level is {level}.")
                    await channel.send(embed=embed)
                # Clamp level to max level if it exceeds the max level
                if level >= max_level:
                    level = max_level
                    xp = 0
                # Update user's xp and level in the database
                cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, user.id))
                conn.commit()
    else:
        # Process commands if the message does not contain any of the WORDS
        await bot.process_commands(message)

# Command to set a user's level
@bot.command()
async def setlevel(ctx, mentioned_user: discord.User, level_from_user: int):
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
@bot.command()
async def addxp(ctx, mentioned_user: discord.User, xp_amount_from_user: int):
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

# Command to show the leaderboard of the top 5 users by level
@bot.command()
async def leaderboard(ctx):
    check = False
    embed = discord.Embed(title="Leaderboard", description="Top 5 Users by Level", color=0x00c3ff)
    c.execute('SELECT name, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT 5')
    result = c.fetchall()
    i = 1
    # Looping through the top 5 users and adding their names, levels, and XP to the embed
    for row in result:
        name = row[0]
        level = row[1]
        xp = row[2]
        if str(name) == str(ctx.author):
            if level == max_level:
                embed.add_field(name=f"{i}. {name} (You)", value=f"Level: {level}\nReached max level.", inline=False)
            else:
                embed.add_field(name=f"{i}. {name} (You)", value=f"Level: {level}\nXP: {xp}", inline=False)
            check = True
        else:
            if level == max_level:
                embed.add_field(name=f"{i}. {name}", value=f"Level: {level}\nReached max level.", inline=False)
            else:
                embed.add_field(name=f"{i}. {name}", value=f"Level: {level}\nXP: {xp}", inline=False)
        i += 1
    # Checking the rank of the user invoking the command and adding their rank to the embed if they're in the top 5
    c.execute('SELECT name, level, xp FROM users WHERE id = ?', (ctx.author.id,))
    result = c.fetchone()
    if result is not None:
        name = result[0]
        level = result[1]
        xp = result[2]
        c.execute('SELECT COUNT(*) FROM users WHERE level > ? OR (level = ? AND xp > ?)', (level, level, xp))
        rank = c.fetchone()[0] + 1
        if check == False:
            if level == max_level:
                embed.add_field(name=f"{name} (You)", value=f"Level: {level}\nReached max level.\nRank: {rank}", inline=False)
            else:
                embed.add_field(name=f"{name} (You)", value=f"Level: {level}\nXP: {xp}\nRank: {rank}", inline=False)
    else:
        embed.add_field(name=f"{ctx.author} (You)", value=f"You don't have any XP and Level.", inline=False)
    await ctx.send(embed=embed)

# Command to delete a user from the database
@bot.command()
async def deleteuser(ctx, mentioned_user: discord.User):
    if str(ctx.author.id) in super_admin_ids:
        if mentioned_user == None:
            # If user didn't mention someone or put user's id, send error message
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"❌ You need to mention user or put user's id.", value="", inline=False)
            await ctx.send(embed=embed)
        else:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (mentioned_user.id,))
            conn.commit()
            # Sending confirmation message
            embed = discord.Embed(color=discord.Color.green())
            embed.add_field(name=f"✅ {mentioned_user} has been deleted from the database.", value="", inline=False)
            await ctx.send(embed=embed)
    # If user invoking the command is not a super admin, send error message
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
        await ctx.send(embed=embed)

# Command to delete all users from the database
@bot.command()
async def deleteusers(ctx):
    if str(ctx.author.id) in super_admin_ids:
        cursor = conn.cursor()
        # Warning message to confirm action
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="⚠️ WARNING: This action will delete all users with their levels and XP. Are you sure?", value="", inline=False)
        warning = await ctx.send(embed=embed)
        # Waiting for confirmation from user
        await warning.add_reaction('✅')
        await warning.add_reaction('❌')
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ['✅', '❌'])
            # Checking if the user reacting is a super admin
            if str(user.id) not in super_admin_ids:
                return
        except asyncio.TimeoutError:
            await warning.delete()
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name="❌ Command timed out. Please try again.", value="", inline=False)
            await ctx.send(embed=embed)
        else:
            # If user confirms action, delete all user from the database
            if str(reaction.emoji) == '✅':
                cursor.execute('DELETE FROM users')
                conn.commit()
                # Sending confirmation message with the name of the super admin who did it
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(name=f"✅ All users have been deleted from the database by {user}.", value=f"ID: {user.id}", inline=False)
                await ctx.send(embed=embed)
            # If user cancels action, send error message
            elif str(reaction.emoji) == '❌':
                await warning.delete()
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="❌ Command cancelled. No changes have been made.", value="", inline=False)
                await ctx.send(embed=embed)
    # If user invoking the command is not a super admin, send error message
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="⛔ You don't have enough permission for this command.", value="", inline=False)
        await ctx.send(embed=embed)

# Command to show user's own or tagged user's XP and level progress
@bot.command()
async def progress(ctx, user: discord.User = None):
    # If no user is tagged, show progress of the message author
    if user is None:
        user = ctx.author
    cursor = conn.cursor()
    cursor.execute('SELECT xp, level FROM users WHERE id = ?', (user.id,))
    result = cursor.fetchone()
    # If user not found in database, send error message
    if result is None:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"❗ User not found in database.", value="", inline=False)
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
                embed.add_field(name=f"📊 Your progress:", value=f"Level: {level}\nYou are at the highest level you can reach!")
            else:
                embed.add_field(name=f"📊 Your progress:", value=f"Level: {level}\nXP: {xp}/{required_xp} ({xp_percentage}%)\nRemaining XP to next level: {remaining_xp}")
        else:
            if level == max_level:
                embed.add_field(name=f"📊 {user}'s progress:", value=f"Level: {level}\nYou are at the highest level you can reach!")
            else:
                embed.add_field(name=f"📊 {user}'s progress:", value=f"Level: {level}\nXP: {xp}/{required_xp} ({xp_percentage}%)\nRemaining XP to next level: {remaining_xp}")
        await ctx.send(embed=embed)

# Command to add a new admin to the database
@bot.command()
async def addadmin(ctx, mentioned_user: discord.User = None):
    # Checking if the user invoking the command is a super admin
    if str(ctx.author.id) in super_admin_ids:
        if mentioned_user == None:
            # If user didn't mention someone or put user's id, send error message
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"❌ You need to mention user or put user's id.", value="", inline=False)
            await ctx.send(embed=embed)
        else:
            cursor = conn.cursor()
            # Checking if the user is already an admin
            cursor.execute('SELECT * FROM admins WHERE id = ?', (mentioned_user.id,))
            result = cursor.fetchone()
            # If user is already an admin, send error message
            if result is not None:
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"❌ {mentioned_user} is already an admin.", value="", inline=False)
                await ctx.send(embed=embed)
            # If user is not an admin, add user as an admin to the database
            else:
                cursor.execute('INSERT INTO admins (id, name) VALUES (?, ?)', (mentioned_user.id, str(mentioned_user)))
                conn.commit()
                # Sending confirmation message
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(name=f"✅ {mentioned_user} has been added as an admin.", value="", inline=False)
                await ctx.send(embed=embed)
    # If user invoking the command is not a super admin, send error message
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
        await ctx.send(embed=embed)

# Command to remove an admin from the database
@bot.command()
async def removeadmin(ctx, mentioned_user: discord.User = None):
    # Checking if the user invoking the command is an admin
    if str(ctx.author.id) in super_admin_ids:
        if mentioned_user == None:
            # If user didn't mention someone or put user's id, send error message
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name=f"❌ You need to mention user or put user's id.", value="", inline=False)
            await ctx.send(embed=embed)
        else:
            # Removing the mentioned_user ID from the list of admin IDs
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM admins WHERE id = ?', (mentioned_user.id,))
            result = cursor.fetchone()
            if result is not None:
                cursor.execute('DELETE FROM admins WHERE id = ?', (mentioned_user.id,))
                conn.commit()
                # Sending confirmation message
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(name=f"✅ {mentioned_user} is no longer an admin.", value="", inline=False)
                await ctx.send(embed=embed)
            else:
                # Sending error message if mentioned_user is not found in the database
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name=f"⛔ {mentioned_user} is not an admin.", value="", inline=False)
                await ctx.send(embed=embed)
    else:
        # If user invoking the command is not a super admin, send error message
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
        await ctx.send(embed=embed)

# Command to show all admins from the database
@bot.command()
async def showadmins(ctx):
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

# Command that gives information about all commands
@bot.command()
async def help(ctx):
    # Dictionary of all the commands and their descriptions
    commands = {
        '!leaderboard': 'Displays the leaderboard of the top users in the server based on their level.',
        '!progress @user or user_id [Optional]': 'Displays the progress of a specific user in the server towards the next level.\nIf no user is specified, the command will display the progress of the user who invoked the command.',
        '!help': 'Shows a list of all the available commands and their descriptions.',
        '!setlevel @user or user_id': '**[Admin Command]** Sets the level of a specific user in the server.',
        '!addxp @user or user_id': '**[Admin Command]** Adds experience points to a specific user in the server.',
        '!showadmins': '**[Admin Command]** Shows a list of all the admins in the database.',
        '!deleteuser @user or user_id': "**[Super Admin Command]** Deletes a specific user's data from the server, including their level and experience points.",
        '!deleteusers': '**[Super Admin Command]** Deletes all user data from the server, including their levels and experience points.',
        '!addadmin @user or user_id': '**[Super Admin Command]** Adds a new admin to the database.',
        '!removeadmin @user or user_id': '**[Super Admin Command]** Removes an admin from the database.',
        '!resetall': '**[Super Admin Command]** Resets the level and XP of all users in the database.'
    }
    # Creating an embed message with the commands and their descriptions
    embed = discord.Embed(title="Help", description="List of all available commands and their descriptions.", color=0x00c3ff)
    for command, description in commands.items():
        embed.add_field(name=command, value=description, inline=False)
    await ctx.send(embed=embed)

# Command that resets the level and XP of all users in the database
@bot.command()
async def resetall(ctx):
    # Checking if the user invoking the command is a super admin
    if str(ctx.author.id) in super_admin_ids:
        cursor = conn.cursor()
        # Warning message to confirm action
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="⚠️ WARNING: This action will reset all users' levels and XP. Are you sure?", value="", inline=False)
        warning = await ctx.send(embed=embed)
        # Waiting for confirmation from user
        await warning.add_reaction('✅')
        await warning.add_reaction('❌')
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.author and str(reaction.emoji) in ['✅', '❌'])
            # Checking if the user reacting is a super admin
            if str(user.id) not in super_admin_ids:
                return
        except asyncio.TimeoutError:
            await warning.delete()
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name="❌ Command timed out. Please try again.", value="", inline=False)
            await ctx.send(embed=embed)
        else:
            # If user confirms action, reset all user levels and XP in the database
            if str(reaction.emoji) == '✅':
                cursor.execute('UPDATE users SET level = 0, xp = 0')
                conn.commit()
                # Sending confirmation message with the name of the super admin who did it
                embed = discord.Embed(color=discord.Color.green())
                embed.add_field(name=f"✅ All users' levels and XP have been reset by {user}.", value=f"ID: {user.id}", inline=False)
                await ctx.send(embed=embed)
            # If user cancels action, send error message
            elif str(reaction.emoji) == '❌':
                await warning.delete()
                embed = discord.Embed(color=discord.Color.red())
                embed.add_field(name="❌ Command cancelled. No changes have been made.", value="", inline=False)
                await ctx.send(embed=embed)
    # If user invoking the command is not a super admin, send error message
    else:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name=f"⛔ You don't have enough permission for this command.", value="", inline=False)
        await ctx.send(embed=embed)

# Running the bot with the TOKEN
bot.run(TOKEN)