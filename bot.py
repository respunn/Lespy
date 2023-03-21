import discord
from discord.ext import commands
import math

#Connecting to database.
import sqlite3
try:
    conn = sqlite3.connect('level_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, name TEXT, level INTEGER, xp INTEGER)''')
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")

#Getting TOKEN for bot.
import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

#Assigning bot.
bot = commands.Bot(command_prefix='!', intents= discord.Intents.all())
bot.remove_command('help')

# Getting ready for bot.
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} global commands.')
    except Exception as e:
        print(e)

from config import *

#Checking every message for is there any words that we want to detect.
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif any(word in message.content.lower() for word in WORDS):
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE id = ?', (message.author.id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (message.author.id, str(message.author), 1, 1))
            conn.commit()
        else:
            xp, level = result
            xp += 1
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
            cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, message.author.id))
            conn.commit()
    else:
        await bot.process_commands(message)

@bot.command()
async def setlevel(ctx, user: discord.User, level_from_user: int):
    if str(ctx.author.id) in admin_ids:
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE id = ?', (user.id,))
        result = cursor.fetchone()
        check = False
        if level_from_user > max_level:
            level_from_user = max_level
            check = True
        if result is None:
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (user.id, str(user), level_from_user, 0))
            conn.commit()
            if check == False:
                await ctx.send(f'**{user}** has been added to the database and level has been set to **{level_from_user}**.')
            else:
                await ctx.send(f'**{user}** has been added to the database and level has been set to **{level_from_user}**. (Max level set to {max_level})')
        else:
            cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (0, level_from_user, user.id))
            conn.commit()
            if check == False:
                await ctx.send(f"**{user}**'s level has been set to **{level_from_user}**.")
            else:
                await ctx.send(f"**{user}**'s level has been set to **{level_from_user}**. (Max level set to {max_level})")
    else:
        await ctx.send(f"You don not have enough authorization for use this command.")

@bot.command()
async def addxp(ctx, user: discord.User, xp_amount_from_user: int):
    if str(ctx.author.id) in admin_ids:
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE id = ?', (user.id,))
        result = cursor.fetchone()
        if result is None:
            level = 1
            required_xp = 1 * 2 * level_xp_multiplier
            required_xp = round(required_xp)
            if required_xp > max_level_experience:
                required_xp = max_level_experience
            elif required_xp < min_level_experience:
                required_xp = min_level_experience
            while xp >= required_xp:
                level += 1
                xp = xp - required_xp
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (user.id, str(user), level, xp_amount_from_user))
            conn.commit()
            await ctx.send(f'**{user}** has been added to the database and added **{xp_amount_from_user}**.')
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
            cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, user.id))
            conn.commit()
            await ctx.send(f"Added **{xp_amount_from_user}** xp to **{user}**.")
    else:
        await ctx.send(f"You don not have enough authorization for use this command.")

#Leaderboard command
@bot.command()
async def leaderboard(ctx):
    check = False
    embed = discord.Embed(title="Leaderboard", description="Top 5 Users by Level and XP", color=discord.Color.blue())
    c.execute('SELECT name, level, xp FROM users ORDER BY level DESC, xp DESC LIMIT 5')
    result = c.fetchall()
    i = 1
    for row in result:
        name = row[0]
        level = row[1]
        xp = row[2]
        if str(name) == str(ctx.author):
            embed.add_field(name=f"{i}. {name} (You)", value=f"Level: {level}\nXP: {xp}", inline=False)
            check = True
        else:
            embed.add_field(name=f"{i}. {name}", value=f"Level: {level}\nXP: {xp}", inline=False)
        i += 1
    c.execute('SELECT name, level, xp FROM users WHERE id = ?', (ctx.author.id,))
    result = c.fetchone()
    if result is not None:
        name = result[0]
        level = result[1]
        xp = result[2]
        c.execute('SELECT COUNT(*) FROM users WHERE level > ? OR (level = ? AND xp > ?)', (level, level, xp))
        rank = c.fetchone()[0] + 1
        if check == False:
            embed.add_field(name=f"{name} (You)", value=f"Level: {level}\nXP: {xp}\nRank: {rank}", inline=False)
    else:
        embed.add_field(name=f"{ctx.author} (You)", value=f"You don't have any XP and Level.", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)