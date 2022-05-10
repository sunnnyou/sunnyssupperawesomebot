import random
import re
from urllib import request

import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL

intents = discord.Intents.default()
intents.members = True
intents.presences = True

TOKEN = "OTI2MDcyODUwMzA4Mjc2MjM0.Yc2WjQ.kgZ0Rfu9h5Pvlkr7loQnzjrfldM"
client = commands.Bot(command_prefix="!", intents=intents)
youtube_video_list = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'outtmpl': 'ytdl/'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


@client.event
async def on_ready():
    print("Discord bot was started")
    print(client.is_ws_ratelimited())
    incelVille = discord.utils.get(client.guilds, id=794272408529797152)
    print(incelVille.name)
    general = discord.utils.get(incelVille.channels, id=794272408529797154)
    print(general.name)
    pip = incelVille.get_member(385826918844596224)
    print(pip.name)
    print(pip.activity)
    while True:
        for activity in pip.activities:
            if activity.name == "League of Legends":
                print("sent message about pip playing league")
                await general.send("ATTENTION EVERYONE!\nPIP IS PLAYING LEAGUE!\nTHANK YOU FOR YOUR ATTENTION!")
                print("sent message about pip playing league")
                await asyncio.sleep(5)
        await asyncio.sleep(5)


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
    await play_music(ctx)


async def play_music(ctx):
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
            except RuntimeError:
                return


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
async def quote(ctx):
    quotes_channel = discord.utils.get(ctx.guild.channels, name="quotes-channel", type=discord.ChannelType.text)
    messages = await quotes_channel.history(limit=500).flatten()
    randomMessage = random.choice(messages).content
    print("nice")
    await ctx.send(randomMessage)


@client.event
async def on_message(message):
    if message.author == client.user or message.channel.name == 'quotes-channel':
        return
    wordList = {"chad", "cheese", "vote", "twitter", "surgeon", "deutschland", "germany", ""}

    switcher = {
        "chad": "https://i.kym-cdn.com/entries/icons/original/000/026/152/gigachad.jpg",
        "cheese": "https://www.youtube.com/watch?v=y3qrHn0WALs",
        "vote": "⚠️WARNING⚠️ \ncock inspection is NOT required at the voting booths!!!! don't be tricked like "
                "me!!\nSo I was waiting in line to vote when all of a sudden this voting \"official\" came up to me "
                "and said that there was something wrong with my voter registration and asked me to follow him to the "
                "back. When we went around back he said that I had to take off my pants and show my cock because "
                "penis size is the most accurate way to confirm voter identity. Because I thought he was a voting "
                "official I swiftly removed my pants and underwear to show him my member. After he fondled it for a "
                "bit he said it was good and I could go back into the line. It was only after I voted I realized that "
                "he forgot to check my balls too!!! He was obviously not certified to check such an area and I "
                "immediately contacted the security guards about his presence. Please do not fall for any tricks like "
                "I did! stay safe and happy voting!",
        "twitter": "OFFICIAL ACCOUNT!\nBLM, ACAB\nshe/her•13 💁♥️ • 2-9-07 💋💞 • Atheist 😈💫 • God's Princess 😇🙏• "
                   "Twerker 😵🍑 • aquarius ♒• DON'T MESSED WITH ME BITCH 😏✨ • Jake 😍💕",
        "surgeon": "In Korea, heart surgeon. Number one. Steady hand. One day, Kim Jong Un need new heart. I do "
                   "operation. But mistake! Kim Jong Un die! SSD very mad! I hide fishing boat, come to America. No "
                   "English, no food, no money. Darryl give me job. Now I have house, American car and new woman. "
                   "Darryl save life.\nMy big secret. I kill Kim Jong Un on purpose. I good surgeon. The best!",
        "deutschland": "Ein Land, ein Reich, ein Kommentarbereich!",
        "germany": "Ein Land, ein Reich, ein Kommentarbereich!",
        "fortnite": "https://tenor.com/view/fortnite-default-dance-gif-13330926",
        "69": "nice"
    }
    await message.channel.send(switcher.get(message.content.lower()))


client.run(TOKEN)
