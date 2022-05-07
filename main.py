import random
import re
from urllib import request

import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

TOKEN = "OTI2MDcyODUwMzA4Mjc2MjM0.Yc2WjQ.kgZ0Rfu9h5Pvlkr7loQnzjrfldM"
client = commands.Bot(command_prefix="!")
youtube_video_list = [None]
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@client.event
async def on_ready():
    print("Discord bot was started")


# Makes the bot join the voice channel the user is in
@client.command(pass_context=True, brief="Makes the bot join the channel.")
async def join(ctx):
    try:
        if not ctx.message.author.voice:
            await ctx.send('Enter a voice channel you dummy')
            return
        else:
            vname = str(ctx.author.voice.channel)
            print("Joined channel " + vname)
            voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=vname)
            await voiceChannel.connect()
    except discord.errors.ClientException:
        print("Already in a voice channel")


@client.command(pass_context=True, brief="Plays a song if you type in a search term after the command.")
async def play(ctx, *, search):
    if not ctx.message.author.voice:
        await ctx.send('Enter a voice channel you dummy')
        return
    else:
        await join(ctx)

    # Searches for the video with the given variable search
    print("SEARCH: " + search)
    search = search.replace(" ", "+")
    html_content = request.urlopen('https://www.youtube.com/results?search_query=' + search)
    html = html_content.read().decode()

    # can only decode once
    search_results = re.findall('videoId":"(.{11})', html)
    print("SEARCH RESULTS: " + str(search_results[0]))

    # I will just put in the first result, you can loop the response to show more results
    youtube_video = 'https://www.youtube.com/watch?v=' + str(search_results[0])
    if youtube_video_list is not None:
        await ctx.send("Added the song to the playlist")
    youtube_video_list.append(youtube_video)

    # Looping over the youtube_video_list and playing the requests
    await playMusic(ctx)


async def playMusic(ctx):
    while youtube_video_list is not None:

        # Gets Video out of playlist
        try:
            youtube_video = youtube_video_list.pop()
        except IndexError:
            return

        # setting url for ffmpeg
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(youtube_video, download=False)
        URL = info['formats'][0]['url']

        # playing the song and putting out the name of the song in chat
        while True:
            try:
                ctx.voice_client.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                await ctx.send("Now playing: " + youtube_video)
                break
            except discord.errors.ClientException:
                await asyncio.sleep(1)


@client.command(pass_context=True, brief="Pauses the song.")
async def pause(self):
    try:
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await self.send("Pausing the damn song.")
            self.voice_client.is_playing()
        else:
            await self.send("Song is Paused.")
    except:
        await self.send("Nothing is playing at all!")
        return


@client.command(pass_context=True, brief="Resumes the song.")
async def resume(self):
    try:
        if not self.voice_client.is_playing():
            self.voice_client.resume()
            await self.send("Resuming the damn song.")
            self.voice_client.is_playing()
        else:
            await self.send("The song is still playing.")
    except:
        await self.send("Nothing is playing at all!")


@client.command(pass_context=True, brief="Skips the current song.")
async def skip(self):
    try:
        if not self.message.author.voice:
            await self.send('Enter a voice channel you dummy!')
        elif youtube_video_list is None:
            await self.send('Nothing to skip!')
        elif self.voice_client.is_playing():
            self.voice_client.stop()
            await self.send("Skipped the song")
            await play(self)
        else:
            await self.send("Bot is not playing anything!")
    except Exception:
        print("An exception occured")


@client.command(pass_context=True, brief="Stops the song.")
async def stop(self):
    try:
        if self.voice_client.is_playing():
            self.voice_client.stop()
            await self.send("Stopping the damn song.")
        else:
            await self.send("Bot is not playing anything!")
    except:
        await self.send("Bot is not playing anything!")


@client.command(pass_context=True, brief="Leaves the channel.")
async def leave(self):
    voice = discord.utils.get(client.voice_clients, guild=self.guild)
    try:
        if voice.is_connected():
            await self.send("Bye, bitches.")
    except:
        print("Exception occured")
    try:
        await self.voice_client.disconnect()
    except:
        await self.send("I'm not in any channel ... yet.")


@client.command(pass_context=True, brief="Makes the bot angry at you.")
async def fuckoff(ctx):
    try:
        await ctx.send("No, you fuck off.")
    except:
        print("An exception occured")


@client.command(pass_context=True, brief="Puts out a random quote from the quotes channel")
async def quote(self):
    quotes_channel = discord.utils.get(self.guild.channels, name="quotes-channel", type=discord.ChannelType.text)
    messages = await quotes_channel.history(limit=500).flatten()
    await self.send(random.choice(messages).content)


client.run(TOKEN)