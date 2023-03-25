# download_commands.py
import discord
from discord.ext import commands
from pytube import YouTube
import io
import asyncio
import re

import instaloader
import requests

class downloadcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Download commands cog is ready.')

    async def get_user_reaction(self, ctx):
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(title="User response timed out.", color=discord.Color.red())
            await ctx.send(embed=timeout_embed)
            return None
        else:
            return str(reaction)

    @commands.command()
    async def download(self, ctx, url: str = None, resolution: str = None):
        await ctx.message.delete()

        if not url:
            embed = discord.Embed(title="No URL provided.", description="Please provide a YouTube or Instagram Post link.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        # Validate the input URL as a YouTube link
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+'
        instagram_regex = r'(https?://)?(www\.)?instagram\.com/p/[^/]+/?'
        if re.match(instagram_regex, url):
            # Download the video in memory
            downloading_embed = discord.Embed(title="Downloading video...", description="Please wait while the video is being downloaded.", color=discord.Color.blue())
            downloading_message = await ctx.send(embed=downloading_embed)

            # Download the Instagram post
            L = instaloader.Instaloader()
            post = instaloader.Post.from_shortcode(L.context, url.split('/')[-2])

            # Determine the media type (video or photo)
            if post.typename == 'GraphVideo':
                # Get the highest resolution video source
                max_res = 0
                max_res_url = None
                for video in post.get_sidecar_nodes():
                    if 'video_url' in video:
                        width, height = video['dimensions']
                        res = width * height
                        if res > max_res:
                            max_res = res
                            max_res_url = video['video_url']

                media_url = max_res_url if max_res_url is not None else post.video_url
            else:
                media_url = post.url

            # Download the media
            response = requests.get(media_url)
            media_bytes = response.content

            # Send the media as a Discord file
            filename = f"{post.owner_username}_{post.shortcode}.{'mp4' if post.typename == 'GraphVideo' else 'jpg'}"
            media_file = discord.File(io.BytesIO(media_bytes), filename=filename)
            await ctx.send(file=media_file)
            await downloading_message.delete()
            
            # Create and send an embed message with the video name and the name of the user who requested the video
            video_embed = discord.Embed(title=f"{post.owner_username} - {post.shortcode}", color=discord.Color.green())
            video_embed.add_field(name="", value=f"Requested by {ctx.author.mention}")
            await ctx.send(embed=video_embed)
        elif re.match(youtube_regex, url):
            try:
                # Create a YouTube object
                yt = YouTube(url)

                # Download the video in memory
                downloading_embed = discord.Embed(title="Downloading video...", description="Please wait while the video is being downloaded.", color=discord.Color.blue())
                downloading_message = await ctx.send(embed=downloading_embed)

                if resolution:
                    # Filter the streams based on resolution and file extension
                    video = yt.streams.filter(file_extension='mp4', adaptive=True, resolution=resolution).first()

                    if not video:
                        # Send a message with available resolutions if the requested resolution is not available
                        available_resolutions = ", ".join(list(set([stream.resolution for stream in yt.streams.filter(file_extension='mp4', adaptive=True)])))
                        embed = discord.Embed(title="Requested resolution not available.", description=f"Available resolutions: {available_resolutions}", color=discord.Color.red())
                        await ctx.send(embed=embed)
                        return

                    if video.includes_audio_track:
                        video_to_download = video
                    else:
                        confirm_embed = discord.Embed(title=f"Requested resolution '{resolution}' has no audio.", description="Do you still want to download it? React with ✅ to download or ❌ to download the highest resolution with audio.", color=discord.Color.orange())
                        message = await ctx.send(embed=confirm_embed)
                        await message.add_reaction('✅')
                        await message.add_reaction('❌')

                        user_reaction = await self.get_user_reaction(ctx)

                        if user_reaction == '✅':
                            await message.delete()
                            video_to_download = video
                        elif user_reaction == '❌':
                            await message.delete()
                            video_to_download = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()
                        else:
                            return
                else:
                    # Get the highest resolution stream
                    video_to_download = yt.streams.filter(file_extension='mp4', progressive=True).get_highest_resolution()


                video_buffer = io.BytesIO()
                video_to_download.stream_to_buffer(video_buffer)
                video_buffer.seek(0)

                max_file_size = 50 * 1024 * 1024  # 50 MB

                # Check if the file is too large for Discord upload
                if video_buffer.getbuffer().nbytes > max_file_size:
                    large_file_embed = discord.Embed(title="Video file size too large.", description="Please try another video or a lower resolution.", color=discord.Color.red())
                    await downloading_message.delete()
                    await ctx.send(embed=large_file_embed)
                    video_buffer.close()
                    return

                # Send the video as a discord.File
                video_file = discord.File(video_buffer, filename=f"{yt.title}.mp4")
                await ctx.send(file=video_file)
                
                # Create and send an embed message with the video name and the name of the user who requested the video
                video_embed = discord.Embed(title=f"{yt.title}", color=discord.Color.green())
                video_embed.add_field(name="", value=f"Requested by {ctx.author.mention}")
                await ctx.send(embed=video_embed)
                
                await downloading_message.delete()
                video_buffer.close()

            except Exception as e:
                error_embed = discord.Embed(title="Error while downloading video.", description=f"{e}.", color=discord.Color.red())
                await downloading_message.delete()
                await ctx.send(embed=error_embed)
        else: 
            embed = discord.Embed(title="Invalid YouTube or Instagram Post link.", description="Please input a valid YouTube or Instagram Post link.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

def setup(bot):
    bot.add_cog(downloadcommands(bot))