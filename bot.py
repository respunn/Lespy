from random import *
import random
import time
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from discord.utils import get

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

bot = commands.Bot(command_prefix='!', intents= discord.Intents.all())
bot.remove_command('help')

#On Ready
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="the developers"))
    print('Connected to bot: {}'.format(bot.user.name))
    print('Bot ID: {}'.format(bot.user.id))
    try:
        sycned = await bot.tree.sync()
        print(f'Sycned {len(sycned)} global commands.')
    except Exception as e:
        print(e)

#Latency
@bot.tree.command(name='latency', description="Shows bot's latency.")
@app_commands.checks.has_permissions(administrator=True)
async def latency(interaction: discord.Interaction):
    await interaction.response.send_message(f"Latency is {round(bot.latency * 1000)}ms", ephemeral=True)

#Description
@bot.tree.command(name='illusa', description="What is Illusa?")
async def malderecesi(interaction: discord.Interaction):
    await interaction.response.send_message(content=f'To be Announced.')


bot.run(TOKEN)