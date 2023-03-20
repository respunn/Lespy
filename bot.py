import discord
from discord.ext import commands

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

#Getting ready for bot.
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="you"))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
    try:
        sycned = await bot.tree.sync()
        print(f'Sycned {len(sycned)} global commands.')
    except Exception as e:
        print(e)

#Checking every message for is there any words that we want to detect.
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.content.lower() in ['thanks', 'ty']:
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level FROM users WHERE id = ?', (message.author.id,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (message.author.id, str(message.author), 1, 1))
            conn.commit()
        else:
            xp, level = result
            xp += 1
            if xp >= level * 10:
                level += 1
            cursor.execute('UPDATE users SET xp = ?, level = ? WHERE id = ?', (xp, level, message.author.id))
            conn.commit()
    else:
        await bot.process_commands(message)

#User's XP and Level info.
@bot.command()
async def xp(ctx):
    c.execute('SELECT * FROM users WHERE id = ?', (ctx.author.id,))
    result = c.fetchone()
    if result is None:
        await ctx.send('You have no level yet!')
    else:
        xp = result[3]
        level = result[2]
        await ctx.send(f'Your level is {level} with {xp} XP.')

bot.run(TOKEN)