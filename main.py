import random
import re
from urllib import request

import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL, DownloadError

intents = discord.Intents.default()
intents.members = True
intents.presences = True

TOKEN = "OTI2MDcyODUwMzA4Mjc2MjM0.Yc2WjQ.kgZ0Rfu9h5Pvlkr7loQnzjrfldM"
client = commands.Bot(command_prefix="!", intents=intents)
youtube_video_list = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', 'outtmpl': 'ytdl/', 'verbose': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


# executes starting methods if needed
@client.event
async def on_ready():
    print("Discord bot was started")
    print(client.is_ws_ratelimited())
    # await pip_league()


# every 60 seconds it checks if pip is playing league and if he does it will send a message in general every hour
async def pip_league():
    incelVille = discord.utils.get(client.guilds, id=794272408529797152)
    print(incelVille.name)
    general = discord.utils.get(incelVille.channels, id=794272408529797154)
    print(general.name)
    pip = incelVille.get_member(385826918844596224)
    print(pip.name)
    print(pip.activity)
    try:
        while True:
            for activity in pip.activities:
                if activity.name == "League of Legends":
                    print("sent message about pip playing league")
                    await general.send("ATTENTION EVERYONE!\nPIP IS PLAYING LEAGUE!\nTHANK YOU FOR YOUR ATTENTION!")
                    await asyncio.sleep(3600)
            await asyncio.sleep(60)
    except RuntimeError as e:
        print(str(e))
        return


# Makes the bot join the voice channel the user is in
async def join(ctx):
    try:
        if not ctx.message.author.voice:
            await ctx.send('Enter a voice channel you dummy')
            return
        else:
            vname = str(ctx.author.voice.channel)
            voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=vname)
            await voiceChannel.connect()
            print("Joined channel " + vname)
    except discord.errors.ClientException:
        print("Already in a voice channel")
    return


@client.command(pass_context=True, brief="Plays a song if you type in a search term after the command.")
async def play(ctx, *, search=None):
    if not ctx.message.author.voice:
        await ctx.send('Enter a voice channel you dummy')
        return
    elif search is None:
        await ctx.send("You have to type in a search term after the command you dummy")
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
    await ctx.send("Added the song to the playlist")
    youtube_video_list.append(youtube_video)

    # Looping over the youtube_video_list and playing the requests
    await play_music(ctx)
    return


async def play_music(ctx):
    try:
        while True:
            # Gets Video out of playlist and leaves the voice channel after max 5 min if no music is playing anymore
            try:
                youtube_video = youtube_video_list.pop()
            except IndexError:
                await asyncio.sleep(300)
                try:
                    if ctx.voice_client.is_playing():
                        continue
                    await ctx.send("Leaving voice channel due to inactivity")
                    await ctx.voice_client.disconnect()
                except AttributeError:
                    pass
                return

            # setting url for ffmpeg
            with YoutubeDL(YDL_OPTIONS) as ydl:
                try:
                    info = ydl.extract_info(youtube_video, download=False)
                except DownloadError:
                    print("Error occurred while trying to fetch video")
                    await ctx.send("Error occurred while trying to fetch video :(")
                    return
            URL = info['formats'][0]['url']

            # playing the song and putting out the name of the song in chat
            while True:
                try:
                    ctx.voice_client.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                    await ctx.send("Now playing: " + youtube_video)
                    break
                except discord.errors.ClientException:
                    await asyncio.sleep(1)
    except RuntimeError as e:
        print(e)
        return
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
    except AttributeError:
        await self.send("Bot is not playing anything!")
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
    except AttributeError:
        await self.send("Bot is not playing anything!")
    return


@client.command(pass_context=True, brief="Skips the current song.")
async def skip(self):
    if len(youtube_video_list) == 0:
        await self.send("Nothing to skip!")
        return
    try:
        if self.voice_client.is_playing():
            self.voice_client.stop()
            await self.send("Skipped the song")
            await play_music(self)
    except AttributeError:
        await self.send("Nothing to skip!")
    return


@client.command(pass_context=True, brief="Stops the song.")
async def stop(self):
    try:
        self.voice_client.stop()
        await self.send("Stopping the damn song.")
    except AttributeError:
        await self.send("Bot is not playing anything!")
    return


@client.command(pass_context=True, brief="Leaves the channel.")
async def leave(self):
    try:
        if self.voice_client.is_connected():
            await self.send("Bye, have a great time.")
            await self.voice_client.disconnect()
    except AttributeError:
        await self.send("I'm not in any channel ... yet.")
    return


@client.command(pass_context=True, brief="Makes the bot angry at you.")
async def fuckoff(ctx):
    await ctx.send("No, you fuck off.")
    return


@client.command(pass_context=True, brief="Sends a random quote from the quotes channel")
async def quote(ctx):
    try:
        quotes_channel = discord.utils.get(ctx.guild.channels, name="quotes-channel", type=discord.ChannelType.text)
        messages = await quotes_channel.history(limit=500).flatten()
        randomMessage = random.choice(messages).content
        print("Quote was sent")
        await ctx.send(randomMessage)
    except AttributeError:
        ctx.send("This command cant be used in this server!")
    return


@client.command(pass_context=True, brief="Sends a random meme")
async def meme(ctx):
    try:
        sunnys_chat = discord.utils.get(ctx.guild.channels, name="sunnys-chat", type=discord.ChannelType.text)
        messages = await sunnys_chat.history(limit=500).flatten()
        randomMessage = random.choice(messages).content
        print("Meme was sent")
        await ctx.send(randomMessage)
    except AttributeError:
        await ctx.send("This command cant be used in this server!")
    return


@client.event
async def on_message(message):
    # Prevents the bot from looping if the response-value has a trigger-key from responseList
    # Stops the bot from sending a message in the quotes-channel
    if message.author == client.user or message.channel.name == 'quotes-channel':
        return

    # Dictionary with trigger word = key and response = value
    responseList = {
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
        " 69 ": "nice",
        "based": "Based? Based on what? In your dick? Please shut the fuck up and use words properly you fuckin "
                 "troglodyte, do you think God gave us a freedom of speech just to spew random words that have no "
                 "meaning that doesn't even correllate to the topic of the conversation? Like please you always "
                 "complain about why no one talks to you or no one expresses their opinions on you because you're "
                 "always spewing random shit like poggers based cringe and when you try to explain what it is and you "
                 "just say that it's funny like what? What the fuck is funny about that do you think you'll just "
                 "become a stand-up comedian that will get a standing ovation just because you said \"cum\" in the "
                 "stage? HELL NO YOU FUCKIN IDIOT, so please shut the fuck up and use words properly you dumb bitch "
    }

    # Checks if key is message and if true, sends a message containing the value
    for key, value in responseList.items():
        if key in message.content.lower():
            await message.channel.send(value)

    # Makes the client.command methods work
    await client.process_commands(message)


client.run(TOKEN)
