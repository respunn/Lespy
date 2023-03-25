# Importing necessary modules
import discord
import asyncio
from discord.ext import commands
import time

# Connecting to database
from important_files.connection_to_database import *

# Getting bot token from environment variables
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Creating bot instance
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.remove_command('help')

# Import the cogs
from cogs.user_commands import user_commands
from cogs.admin_commands import admin_commands
from cogs.super_admin_commands import super_admin_commands

# Add the cogs to the bot (await the add_cog() method calls)
async def setup():
    # Add the cogs to the bot
    await bot.add_cog(user_commands(bot))
    await bot.add_cog(admin_commands(bot))
    await bot.add_cog(super_admin_commands(bot))

# Bot ready event listener
@bot.event
async def on_ready():
    # Setting bot status and activity
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
    # Printing bot's name and ID to console
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))

# Importing config values from separate file
from important_files.config import *

# User's cooldown datas
cooldowns = {}

# Message event listener for XP system
@bot.event
async def on_message(message):
    global cooldowns
    # Return if the message is sent by the bot itself
    if message.author.bot:
        return
    # Check for cooldown
    user_id = message.author.id
    current_time = time.time()
    if user_id in cooldowns:
        cooldown_end = cooldowns[user_id]
        if current_time < cooldown_end:
            # Ignore the message if the user is still on cooldown
            return
        else:
            # Remove user from cooldowns if the cooldown has ended
            del cooldowns[user_id]
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
            # Add user to cooldowns
            cooldowns[user_id] = current_time + cooldown_duration_on_message
            cursor = conn.cursor()
            cursor.execute('SELECT xp, level FROM users WHERE id = ?', (user.id,))
            result = cursor.fetchone()
            if result is None:
                # Insert new user with default level and xp if not found in the database
                cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (user.id, str(user), 0, min_level))
                conn.commit()
                # make embed message here
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
                # Creating check for level up or not.
                level_check = False
                # Level up and send an embed message if required xp is reached
                if xp >= required_xp:
                    level += 1
                    xp = xp - required_xp
                    channel = message.channel
                    # We recalculate the amount of xp needed. (Because level is changed.)
                    required_xp = level * 2 * level_xp_multiplier
                    required_xp = round(required_xp)
                    # Check if required xp is within the defined range
                    if required_xp > max_level_experience:
                        required_xp = max_level_experience
                    elif required_xp < min_level_experience:
                        required_xp = min_level_experience
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(name=f"🎉 You've leveled up {user}, congratulations!", value="", inline=False)
                    embed.set_footer(text=f"Your current level is {level}.\nFor the next level you must earn {required_xp} xp!")
                    await channel.send(embed=embed)
                    level_check = True
                # Clamp level to max level if it exceeds the max level
                if level >= max_level:
                    level = max_level
                    xp = 0
                # Update user's xp and level in the database
                cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, user.id))
                conn.commit()
                if level_check == False:
                    xp_percentage = int((xp / required_xp) * 100)
                    channel = message.channel
                    embed = discord.Embed(color=discord.Color.green())
                    embed.add_field(name=f"🎊 You've earned an xp {user}!", value="", inline=False)
                    embed.set_footer(text=f"XP: {xp}/{required_xp} ({xp_percentage}%)")
                    await channel.send(embed=embed)
    else:
        # Process commands if the message does not contain any of the WORDS
        await bot.process_commands(message)

if __name__ == '__main__':
    # Call the setup function and run the bot using asyncio.run()
    asyncio.run(setup())
    bot.run(TOKEN)