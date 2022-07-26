from operator import is_, truediv
import discord
from discord.ext import commands
import youtube_dl
from time import *
import threading

client = commands.Bot(command_prefix = "/")

music_queue = []
duration_queue = []
is_playing = []
current_duration = []
paused = False

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format' : "bestaudio"}

#///////////////////////////////////////////////////

@client.command()
async def join(ctx) :
    global paused

    if (ctx.author.voice is None) : # if user is not in vc
        await ctx.send(":butterfly: | you're not in vc.")
    else : 
        vc = ctx.author.voice.channel
        if (ctx.voice_client is None) : # if bot is not in vc
            await vc.connect()
        else :                          # if bot is in another vc
            await ctx.voice_client.move_to(vc)

@client.command()
async def disconnect(ctx) :
    await ctx.voice_client.disconnect()

@client.command()
async def play(ctx, url = None) :

    # create a queue/playlist
    global music_queue, is_playing, duration_queue, current_duration, paused
    global FFMPEG_OPTIONS, YDL_OPTIONS

    # joins vc
    if (ctx.author.voice is None) : # if user is not in vc
        await ctx.send(":butterfly: | you're not in vc.")
    else : 
        vc = ctx.author.voice.channel
        if (ctx.voice_client is None) : # if bot is not in vc
            await vc.connect()
        else :                          # if bot is in another vc
            await ctx.voice_client.move_to(vc)
        if (paused == True) :
            ctx.voice_client.resume()

    if (url is not None) :
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl :
            info = ydl.extract_info(url, download = False)
            url_a = info['formats'][0]['url']
            duration = info['duration']
            source = await discord.FFmpegOpusAudio.from_probe(url_a, **FFMPEG_OPTIONS)
            music_queue.append(source)  # add music to queue
            duration_queue.append(duration) # add duration to queue
            
            if (len(is_playing) == 0) :
                func_play(ctx)


def func_play(ctx) :
    global music_queue, is_playing, duration_queue, current_duration, paused

    if (not ctx.voice_client.is_playing() and len(music_queue) == 0) :
        ctx.voice_client.stop()
        is_playing.clear()
        current_duration.clear()
        return None

    elif (len(music_queue) > 0) :
        ctx.voice_client.stop()
        is_playing.clear()
        current_duration.clear()
        is_playing.append(music_queue[0])
        current_duration.append(duration_queue[0])

        music_queue.pop(0)
        duration_queue.pop(0)
        
        print(len(music_queue))
        ctx.voice_client.play(is_playing[0]) # after = lambda e : print('Player error: %s' % e) if e else None)
        timer = threading.Timer(current_duration[0], func_play, args = [ctx])
        timer.start()


@client.command()
async def pause(ctx) :
    global paused

    if (ctx.voice_client.is_playing() and paused == False) :
        ctx.voice_client.pause()
        paused = True
        await ctx.send(":pause_button: | paused.")
    elif (paused == True) :
        await ctx.send(":pause_button: | already paused.")
    else :
        await ctx.send(":butterfly: | nothing to pause.")


@client.command()
async def resume(ctx) :
    global music_queue, is_playing, paused

    if (not ctx.voice_client.is_playing() and ctx.voice_client is not None and paused == True) :
        ctx.voice_client.resume()
        paused = False
        await ctx.send(":arrow_forward: | resumed.")
    elif (paused == False) :
        pass
    else :
        await ctx.send(":butterfly: | nothing to resume.")


@client.command()
async def skip(ctx) :
    global music_queue, is_playing, paused

    if (ctx.voice_client is None) :
        await ctx.send(":butterfly: | nothing to skip.") 

    else :
        paused = False
        ctx.voice_client.stop()
        await ctx.send(":fast_forward: | skipped.")
        is_playing.clear()
        current_duration.clear()

        if (len(music_queue) > 0) :
            is_playing.append(music_queue[0])
            current_duration.append(duration_queue[0])
            music_queue.pop(0)
            duration_queue.pop(0)
            ctx.voice_client.play(is_playing[0])
            timer = threading.Timer(current_duration[0], func_play, args = [ctx])
            timer.start()

client.run("")


