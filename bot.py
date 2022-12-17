from random import *
import random
import time
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from discord.utils import get
import datetime


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

#Avatar
@bot.tree.command(name='avatar', description="You can get people's profile pictures.")
async def avatar(interaction: discord.Interaction, member: Optional[discord.Member]):
    if member == None:
        ProfilePicture = interaction.user.display_avatar.url
        await interaction.response.send_message(ProfilePicture)
    else:
        ProfilePicture = member.avatar.url
        await interaction.response.send_message(ProfilePicture)



#Admin Commands
#Clear
@bot.tree.command(name='clear', description="Clears the given amount of messages.")
@app_commands.checks.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"Successfully deleted {amount} of messages.", ephemeral=True)
    await interaction.channel.purge(limit=amount)
#TODO clear from specific user

#Ban
@bot.tree.command(name='ban', description="Bans members.")
@app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member: discord.Member, delete_messages: int ,reason: str = "No reason provided."):
    try:
        await member.ban(reason = reason, delete_message_days = delete_messages)
        await interaction.response.send_message(f"Successfully banned {member.mention} for {reason}")
    except:
        await interaction.response.send_message(f"The {member.mention} could not be banned from the server.", ephemeral=True)
@ban.error
async def ban_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingPermissions):
        await interaction.response.send_message(f"You don't have permission to use this command!", ephemeral=True)

#Kick
@bot.tree.command(name='kick', description="Kicks members.")
@app_commands.checks.has_permissions(administrator=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.kick(reason = reason)
        await interaction.response.send_message(f"Successfully kicked {member.mention} for: {reason}")
    except:
        await interaction.response.send_message(f"The {member.mention} could not be kicked from the server.", ephemeral=True)
@kick.error
async def ban_error(interaction: discord.Interaction, error):
    if isinstance(error, MissingPermissions):
        await interaction.response.send_message(f"You don't have permission to use this command!", ephemeral=True)



#Logging

# Get the current time
now = datetime.datetime.now()
# Format the timestamp
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

#Importing config file
from logger_config import *
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Only log messages that are sent in a guild
    if message.guild.id == GUILD_ID:
        # Log the message when it is sent
        # Get the channel object
        channel = bot.get_channel(CHANNEL_ID)
        # Send a message to the channel
        await channel.send(f"{timestamp} - {message.author.mention} (ID: {message.author.id} ) sent: {message.content}")

@bot.event
async def on_message_edit(before, after):
    if before.author == bot.user:
        return
    # Only log messages that are edited in a guild
    if after.guild.id == GUILD_ID:
        # Log the message when it is sent
        # Get the channel object
        channel = bot.get_channel(CHANNEL_ID)
        # Send a message to the channel
        await channel.send(f"{timestamp} - {after.author.mention} (ID: {after.author.id} ) edited his/her message from '{before.content}' to '{after.content}'")

@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    # Only log messages that are deleted in a guild
    if message.guild.id == GUILD_ID:
        # Log the message when it is sent
        # Get the channel object
        channel = bot.get_channel(CHANNEL_ID)
        # Send a message to the channel
        await channel.send(f"{timestamp} - {message.author.mention} (ID: {message.author.id} ) deleted: {message.content}")

#TODO reaction log 
#TODO audit log

#Join and leave
@bot.event
async def on_member_join(member):
    # Get the channel object
    channel = bot.get_channel(CHANNEL_ID)
    # Print a message when a user joins the server
    await channel.send(f"{timestamp} - {member.mention} (ID: {member.id} ) joined the server.")

@bot.event
async def on_member_remove(member):
    # Get the channel object
    channel = bot.get_channel(CHANNEL_ID)
    # Print a message when a user leaves the server
    await channel.send(f"{timestamp} - {member.mention} (ID: {member.id} ) left the server.")


"""
#Channel
@bot.event
async def on_guild_channel_delete(channel):
    # Get the channel object
    channel2 = bot.get_channel(CHANNEL_ID)
    # Print a message when a user leaves the server
    await channel2.send(f"{timestamp} - Channel {channel.mention} (ID: {channel.id} ) deleted.")
@bot.event
async def on_guild_channel_create(channel):
    # Get the channel object
    channel2 = bot.get_channel(CHANNEL_ID)
    # Print a message when a user leaves the server
    await channel2.send(f"{timestamp} - Channel {channel.mention} (ID: {channel.id} ) created.")
@bot.event
async def on_guild_channel_update(before, after):
    # Get the channel object
    channel2 = bot.get_channel(CHANNEL_ID)
    # Print a message when a user leaves the server
    await channel2.send(f"{timestamp} - Channel {before.mention} (ID: {before.id} ) changed to {after} from {before}.")
"""

@bot.event
async def on_ready(guild):
    # Get the channel object
    channel2 = bot.get_channel(CHANNEL_ID)
    async for entry in guild.audit_logs(limit=100):
        await channel2.send(f'{entry.user} did {entry.action} to {entry.target}')

bot.run(TOKEN)