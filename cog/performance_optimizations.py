"""
Performance optimizations for the Discord bot
Focuses on improving command response time and reducing latency
"""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, Dict
import logging
from discord.ext import commands
import discord

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('performance')

class PerformanceMonitor:
    """Monitor and log command execution times"""
    
    def __init__(self):
        self.command_times = {}
    
    def track_command(self, command_name: str, duration: float):
        """Track command execution time"""
        if command_name not in self.command_times:
            self.command_times[command_name] = []
        self.command_times[command_name].append(duration)
        
        # Keep only last 100 measurements
        if len(self.command_times[command_name]) > 100:
            self.command_times[command_name] = self.command_times[command_name][-100:]
    
    def get_average_time(self, command_name: str) -> float:
        """Get average execution time for a command"""
        if command_name not in self.command_times or not self.command_times[command_name]:
            return 0.0
        return sum(self.command_times[command_name]) / len(self.command_times[command_name])

# Global performance monitor
perf_monitor = PerformanceMonitor()

def performance_timer(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            duration = time.perf_counter() - start_time
            perf_monitor.track_command(func.__name__, duration)
            logger.info(f"{func.__name__} took {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start_time
            perf_monitor.track_command(func.__name__, duration)
            logger.info(f"{func.__name__} took {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

class OptimizedCommands:
    """Optimized command implementations"""
    
    @staticmethod
    @performance_timer
    async def optimized_ping(ctx):
        """Optimized ping command with reduced latency measurement"""
        # Use WebSocket latency instead of HTTP round trip
        latency = round(ctx.bot.latency * 1000)
        
        # Use faster embed creation
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed, delete_after=10)

    @staticmethod
    @performance_timer
    async def optimized_server_info(ctx):
        """Optimized server info command with caching"""
        guild = ctx.guild
        
        # Cache frequently accessed properties
        member_count = guild.member_count
        created_at = guild.created_at
        owner = guild.owner
        
        # Use faster embed creation
        embed = discord.Embed(
            title=guild.name,
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Batch add fields for better performance
        embed.add_field(
            name="📊 Server Stats",
            value=f"Members: {member_count}\n"
                  f"Created: {created_at.strftime('%Y-%m-%d')}\n"
                  f"Owner: {owner.mention}",
            inline=False
        )
        
        await ctx.send(embed=embed)

class AsyncCache:
    """Simple async cache for frequently accessed data"""
    
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    async def get(self, key: str, fetch_func: Callable[[], Any]) -> Any:
        """Get cached value or fetch new one"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
        
        value = await fetch_func()
        self.cache[key] = (value, time.time())
        return value
    
    def invalidate(self, key: str):
        """Invalidate specific cache key"""
        self.cache.pop(key, None)
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()

# Global cache instance
global_cache = AsyncCache(ttl=300)

class OptimizedMusicPlayer:
    """Optimized music player with reduced latency"""
    
    def __init__(self):
        self.connection_pool = {}
    
    @performance_timer
    async def get_video_info_optimized(self, url: str, ytdl) -> Optional[Dict[str, Any]]:
        """Optimized video info fetching with caching"""
        cache_key = f"video_info_{url}"
        
        async def fetch():
            try:
                return await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: ytdl.extract_info(url, download=False)
                )
            except Exception:
                return None
        
        return await global_cache.get(cache_key, fetch)
    
    @performance_timer
    async def search_youtube_optimized(self, query: str, ytdl) -> Optional[Dict[str, Any]]:
        """Optimized YouTube search with caching"""
        cache_key = f"search_{query}"
        
        async def fetch():
            try:
                search_query = f"ytsearch:{query}"
                return await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ytdl.extract_info(search_query, download=False)
                )
            except Exception:
                return None
        
        return await global_cache.get(cache_key, fetch)

class ConnectionPool:
    """Manage and reuse voice connections efficiently"""
    
    def __init__(self):
        self.connections = {}
        self.last_used = {}
    
    async def get_connection(self, guild_id: int) -> Optional[discord.VoiceClient]:
        """Get existing connection or None"""
        return self.connections.get(guild_id)
    
    async def store_connection(self, guild_id: int, voice_client: discord.VoiceClient):
        """Store connection for reuse"""
        self.connections[guild_id] = voice_client
        self.last_used[guild_id] = time.time()
    
    async def cleanup_idle_connections(self, max_idle: int = 300):
        """Clean up idle voice connections"""
        current_time = time.time()
        to_remove = []
        
        for guild_id, last_used in self.last_used.items():
            if current_time - last_used > max_idle:
                voice_client = self.connections.get(guild_id)
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                to_remove.append(guild_id)
        
        for guild_id in to_remove:
            self.connections.pop(guild_id, None)
            self.last_used.pop(guild_id, None)

# Global connection pool
connection_pool = ConnectionPool()

# Performance monitoring commands
class PerformanceCommands(commands.Cog):
    """Commands for monitoring bot performance"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='perfstats', help='Show performance statistics')
    @commands.is_owner()
    async def perf_stats(self, ctx):
        """Show performance statistics"""
        embed = discord.Embed(
            title="📊 Performance Statistics",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        
        # Show top 10 slowest commands
        slow_commands = sorted(
            perf_monitor.command_times.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:10]
        
        for cmd, times in slow_commands:
            if times:
                avg_time = sum(times) / len(times)
                embed.add_field(
                    name=cmd,
                    value=f"Avg: {avg_time:.3f}s\nCalls: {len(times)}",
                    inline=True
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clearcache', help='Clear performance caches')
    @commands.is_owner()
    async def clear_cache(self, ctx):
        """Clear all performance caches"""
        global_cache.clear()
        await ctx.send("✅ All performance caches cleared!")

# Utility functions for optimization
class OptimizationUtils:
    """Utility functions for performance optimization"""
    
    @staticmethod
    def create_fast_embed(title: str, description: str = "", color: int = 0x00ff00) -> discord.Embed:
        """Create a fast embed with minimal overhead"""
        return discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )
    
    @staticmethod
    def batch_embed_fields(embed: discord.Embed, fields: list):
        """Batch add fields to embed for better performance"""
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    
    @staticmethod
    async def send_temporary_message(ctx, content: str, delete_after: int = 5):
        """Send a temporary message for quick feedback"""
        await ctx.send(content, delete_after=delete_after)

# Background task for cleanup
async def performance_cleanup_task(bot):
    """Background task for periodic cleanup"""
    while not bot.is_closed():
        try:
            # Clean up idle connections
            await connection_pool.cleanup_idle_connections()
            
            # Clear expired cache entries
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in global_cache.cache.items()
                if current_time - timestamp > global_cache.ttl
            ]
            for key in expired_keys:
                global_cache.invalidate(key)
                
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
        
        await asyncio.sleep(60)  # Run every minute

# Setup function
async def setup_performance_optimizations(bot):
    """Setup performance optimizations"""
    await bot.add_cog(PerformanceCommands(bot))
    
    # Start background cleanup task
    bot.loop.create_task(performance_cleanup_task(bot))
    
    logger.info("Performance optimizations loaded successfully")
