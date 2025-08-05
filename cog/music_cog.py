import discord
from discord.ext import commands
import yt_dlp
import asyncio
import urllib.parse
import re

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.voice_clients = {}
        
        # yt-dlp options for better audio quality
        self.ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        
        self.ffmpeg_options = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }
        
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_format_options)

    async def get_video_info(self, url):
        """Extract video information from URL"""
        try:
            data = await self.bot.loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
            return data
        except Exception as e:
            return None

    def search_youtube(self, query):
        """Search YouTube for videos"""
        try:
            search_query = f"ytsearch:{query}"
            data = self.ytdl.extract_info(search_query, download=False)
            if 'entries' in data and data['entries']:
                return data['entries'][0]
            return None
        except Exception:
            return None

    @commands.command(name='join', help='Join your voice channel')
    async def join(self, ctx):
        """Join the voice channel"""
        if ctx.author.voice is None:
            return await ctx.send("❌ You're not in a voice channel!")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
            # Automatically deafen the bot
            await voice_client.guild.change_voice_state(channel=channel, self_deaf=True)
        
        await ctx.send(f"✅ Joined **{channel.name}** (deafened)")

    @commands.command(name='leave', help='Leave the voice channel')
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client is None:
            return await ctx.send("❌ I'm not in a voice channel!")
        
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel!")

    @commands.command(name='play', help='Play a song from YouTube')
    async def play(self, ctx, *, query):
        """Play a song from YouTube"""
        if ctx.author.voice is None:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        # Join voice channel if not already connected
        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            voice_client = await channel.connect()
            # Automatically deafen the bot
            await voice_client.guild.change_voice_state(channel=channel, self_deaf=True)
            
        
        # Check if URL or search query
        if query.startswith('http'):
            video_info = await self.get_video_info(query)
        else:
            video_info = self.search_youtube(query)
        
        if not video_info:
            return await ctx.send("❌ Could not find the song!")
        
        # Get guild ID for queue management
        guild_id = ctx.guild.id
        
        if guild_id not in self.queue:
            self.queue[guild_id] = []
        
        # Add song to queue
        song = {
            'title': video_info.get('title', 'Unknown'),
            'url': video_info.get('webpage_url', ''),
            'duration': video_info.get('duration', 0),
            'requester': ctx.author.display_name
        }
        
        self.queue[guild_id].append(song)
        
        if ctx.voice_client.is_playing():
            await ctx.send(f"🎵 Added to queue: **{song['title']}**")
        else:
            await self.play_next(ctx)

    async def play_next(self, ctx):
        """Play the next song in queue"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.queue or not self.queue[guild_id]:
            return
        
        song = self.queue[guild_id].pop(0)
        
        def after_playing(error):
            if error:
                print(f"Error playing audio: {error}")
            coro = self.play_next(ctx)
            fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error in after_playing: {e}")
        
        try:
            # Get audio source
            data = await self.bot.loop.run_in_executor(None, lambda: self.ytdl.extract_info(song['url'], download=False))
            url2 = data['url']
            
            source = discord.FFmpegPCMAudio(url2, **self.ffmpeg_options)
            ctx.voice_client.play(source, after=after_playing)
            
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{song['title']}**\nRequested by: {song['requester']}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error playing song: {str(e)}")
            await self.play_next(ctx)

    @commands.command(name='skip', help='Skip the current song')
    async def skip(self, ctx):
        """Skip the current song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("❌ No song is currently playing!")
        
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song!")

    @commands.command(name='queue', help='Show the current queue')
    async def queue_list(self, ctx):
        """Show the current queue"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.queue or not self.queue[guild_id]:
            return await ctx.send("📭 The queue is empty!")
        
        embed = discord.Embed(title="🎵 Current Queue", color=0x00ff00)
        
        for i, song in enumerate(self.queue[guild_id], 1):
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"Requested by: {song['requester']}",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name='clearqueue', help='Clear the music queue')
    async def clear_queue(self, ctx):
        """Clear the music queue"""
        guild_id = ctx.guild.id
        
        if guild_id in self.queue:
            self.queue[guild_id] = []
        
        await ctx.send("🗑️ Music queue cleared!")

    @commands.command(name='pause', help='Pause the current song')
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("❌ No song is currently playing!")
        
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused the music!")

    @commands.command(name='resume', help='Resume the paused song')
    async def resume(self, ctx):
        """Resume the paused song"""
        if ctx.voice_client is None or not ctx.voice_client.is_paused():
            return await ctx.send("❌ No song is paused!")
        
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed the music!")

    @commands.command(name='stop', help='Stop the music and clear queue')
    async def stop(self, ctx):
        """Stop the music and clear queue"""
        guild_id = ctx.guild.id
        
        if guild_id in self.queue:
            self.queue[guild_id] = []
        
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
        
        await ctx.send("⏹️ Stopped the music and cleared the queue!")

    @commands.command(name='nowplaying', help='Show currently playing song')
    async def now_playing(self, ctx):
        """Show currently playing song"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("❌ No song is currently playing!")
        
        await ctx.send("🎵 A song is currently playing...")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
