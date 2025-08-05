import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token from environment
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Create bot instance
bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    description='Advanced Discord bot with music, games, and utilities',
    activity=discord.Activity(type=discord.ActivityType.listening, name="!help")
)

# Music player variables
music_queue = {}
voice_clients = {}

# Weather API key (you can get free from openweathermap.org)
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'your_api_key_here')

# Economy system
user_balances = {}
user_inventory = {}

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Basic Commands
@bot.command(name='ping', help='Check bot latency')
async def ping(ctx):
    """Check bot latency - optimized for faster response"""
    # Use WebSocket latency for more accurate measurement
    latency = round(bot.latency * 1000)
    
    # Use faster embed creation
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"**Latency:** {latency}ms",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    
    # Send immediately without additional processing
    await ctx.send(embed=embed, delete_after=10)

@bot.command(name='hello', help='Say hello')
async def hello(ctx):
    """Say hello"""
    await ctx.send(f'👋 Hello {ctx.author.mention}!')

# Note: The join command is already defined in music_cog.py
# The enhanced_bot.py file doesn't need its own join command

# Load cogs
async def load_cogs():
    await bot.load_extension('cog.music_cog')
    await bot.load_extension('cog.invite_manager')
    await bot.load_extension('cog.tempvoice_cog')
    await bot.load_extension('cog.custom_commands_cog')

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Load cogs
    try:
        await load_cogs()
        print("✅ Music cog loaded successfully")
        print("✅ Invite Manager cog loaded successfully")
        print("✅ TempVoice cog loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load cogs: {e}")
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_member_join(member):
    """Send welcome message to new members"""
    guild = member.guild
    welcome_channel = guild.system_channel or next((channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages), None)
    
    if welcome_channel:
        embed = discord.Embed(
            title=f"Welcome {member.display_name}!",
            description=f"Welcome to {guild.name}! We're glad you're here.",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Getting Started", value="Check out our rules and enjoy your stay!", inline=False)
        embed.add_field(name="Support", value="Feel free to ask questions in chat!", inline=False)
        
        await welcome_channel.send(embed=embed)

# Moderation Commands
@bot.command(name='kick', help='Kick a member')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kick a member from the server"""
    await member.kick(reason=reason)
    await ctx.send(f'👢 {member.mention} has been kicked. Reason: {reason or "No reason"}')

@bot.command(name='ban', help='Ban a member')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Ban a member from the server"""
    await member.ban(reason=reason)
    await ctx.send(f'🔨 {member.mention} has been banned. Reason: {reason or "No reason"}')

@bot.command(name='clear', help='Clear messages')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    """Clear messages from channel"""
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'🗑️ Cleared {len(deleted)-1} messages!', delete_after=5)

# Fun Games
@bot.command(name='roll', help='Roll dice')
async def roll(ctx, dice: str = '1d6'):
    """Roll dice (format: 2d6 for 2 six-sided dice)"""
    try:
        rolls, limit = map(int, dice.split('d'))
        result = [random.randint(1, limit) for _ in range(rolls)]
        total = sum(result)
        await ctx.send(f'🎲 Rolled: {result} = **{total}**')
    except:
        await ctx.send('❌ Use format like `!roll 2d6`')

@bot.command(name='coinflip', help='Flip a coin')
async def coinflip(ctx):
    """Flip a coin"""
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'🪙 **{result}**!')

@bot.command(name='8ball', help='Magic 8-ball')
async def eightball(ctx, *, question):
    """Magic 8-ball"""
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes – definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.",
        "Don't count on it.", "My reply is no.", "My sources say no.",
        "Outlook not so good.", "Very doubtful."
    ]
    await ctx.send(f'🎱 **{random.choice(responses)}**')

# Weather Commands
@bot.command(name='weather', help='Get weather information')
async def weather(ctx, *, city):
    """Get weather information"""
    if not WEATHER_API_KEY or WEATHER_API_KEY == 'your_api_key_here':
        await ctx.send("⚠️ Weather API key not configured. Get free key from openweathermap.org")
        return
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                weather_desc = data['weather'][0]['description']
                temp = data['main']['temp']
                humidity = data['main']['humidity']
                
                embed = discord.Embed(title=f"Weather in {city}", color=0x00ff00)
                embed.add_field(name="Description", value=weather_desc.title(), inline=True)
                embed.add_field(name="Temperature", value=f"{temp}°C", inline=True)
                embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ City not found!")

# Economy System
@bot.command(name='balance', help='Check your balance')
async def balance(ctx):
    """Check your coin balance"""
    user_id = str(ctx.author.id)
    balance = user_balances.get(user_id, 100)
    await ctx.send(f"💰 {ctx.author.mention}, your balance: **{balance}** coins")

@bot.command(name='work', help='Earn coins')
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    """Earn coins by working"""
    user_id = str(ctx.author.id)
    earnings = random.randint(10, 50)
    
    user_balances[user_id] = user_balances.get(user_id, 100) + earnings
    await ctx.send(f"💼 {ctx.author.mention}, you worked and earned **{earnings}** coins!")

@bot.command(name='gamble', help='Gamble your coins')
async def gamble(ctx, amount: int):
    """Gamble your coins"""
    user_id = str(ctx.author.id)
    current_balance = user_balances.get(user_id, 100)
    
    if amount <= 0:
        await ctx.send("❌ Bet must be positive!")
        return
    
    if amount > current_balance:
        await ctx.send("❌ You don't have enough coins!")
        return
    
    if random.choice([True, False]):
        winnings = amount * 2
        user_balances[user_id] = current_balance + amount
        await ctx.send(f"🎉 {ctx.author.mention}, you won! New balance: **{user_balances[user_id]}** coins")
    else:
        user_balances[user_id] = current_balance - amount
        await ctx.send(f"😢 {ctx.author.mention}, you lost! New balance: **{user_balances[user_id]}** coins")

@bot.command(name='daily', help='Claim daily reward')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    """Claim daily reward"""
    user_id = str(ctx.author.id)
    reward = 100
    user_balances[user_id] = user_balances.get(user_id, 100) + reward
    await ctx.send(f"🎁 {ctx.author.mention}, you claimed your daily reward of **{reward}** coins!")

# Fun Commands
@bot.command(name='meme', help='Get a random meme')
async def meme(ctx):
    """Get a random meme"""
    memes = [
        "https://i.imgur.com/8XVsVbN.jpg",
        "https://i.imgur.com/7VPU5b7.jpg",
        "https://i.imgur.com/5VPU5b7.jpg",
        "https://i.imgur.com/9XVsVbN.jpg"
    ]
    await ctx.send(random.choice(memes))

@bot.command(name='joke', help='Get a random joke')
async def joke(ctx):
    """Get a random joke"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!"
    ]
    await ctx.send(f"😄 {random.choice(jokes)}")

@bot.command(name='avatar', help='Get user avatar')
async def avatar(ctx, member: discord.Member = None):
    """Get user avatar"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(title=f"{member.name}'s Avatar", color=0x00ff00)
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await ctx.send(embed=embed)

# Reminder System
@bot.command(name='remind', help='Set a reminder')
async def remind(ctx, time: str, *, message):
    """Set a reminder (format: 10s, 5m, 1h, 1d)"""
    try:
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = time[-1].lower()
        amount = int(time[:-1])
        
        if unit not in time_units:
            await ctx.send("❌ Use format like `10s`, `5m`, `1h`, or `1d`")
            return
            
        seconds = amount * time_units[unit]
        
        await ctx.send(f"⏰ Reminder set for {time} from now!")
        
        await asyncio.sleep(seconds)
        await ctx.send(f"🔔 Reminder: {message} - {ctx.author.mention}")
        
    except ValueError:
        await ctx.send("❌ Invalid time format! Use like `!remind 5m Take a break`")

# Server Info
@bot.command(name='server', help='Get server info')
async def server(ctx):
    """Get server information"""
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description="Server Information", color=0x00ff00)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier}", inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    await ctx.send(embed=embed)

# User Info
@bot.command(name='userinfo', help='Get user information')
async def userinfo(ctx, member: discord.Member = None):
    """Get user information"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(title=f"{member.name}'s Info", color=0x00ff00)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Roles", value=len(member.roles)-1, inline=True)
    await ctx.send(embed=embed)

# Slash Commands
@bot.tree.command(name="meme", description="Get a random meme")
async def meme_slash(interaction: discord.Interaction):
    """Get a random meme via slash command"""
    memes = [
        "https://i.imgur.com/8XVsVbN.jpg",
        "https://i.imgur.com/7VPU5b7.jpg",
        "https://i.imgur.com/5VPU5b7.jpg",
        "https://i.imgur.com/9XVsVbN.jpg"
    ]
    await interaction.response.send_message(random.choice(memes))

@bot.tree.command(name="joke", description="Get a random joke")
async def joke_slash(interaction: discord.Interaction):
    """Get a random joke via slash command"""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? He was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!"
    ]
    await interaction.response.send_message(f"😄 {random.choice(jokes)}")

@bot.tree.command(name="roll", description="Roll dice")
async def roll_slash(interaction: discord.Interaction, dice: str = '1d6'):
    """Roll dice via slash command"""
    try:
        rolls, limit = map(int, dice.split('d'))
        result = [random.randint(1, limit) for _ in range(rolls)]
        total = sum(result)
        await interaction.response.send_message(f'🎲 Rolled: {result} = **{total}**')
    except:
        await interaction.response.send_message('❌ Use format like `2d6`')

@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip_slash(interaction: discord.Interaction):
    """Flip a coin via slash command"""
    result = random.choice(['Heads', 'Tails'])
    await interaction.response.send_message(f'🪙 **{result}**!')

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to use this command!")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Command on cooldown! Try again in {error.retry_after:.1f} seconds.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Use `!help {ctx.command}` for usage.")
    else:
        await ctx.send(f"⚠️ An error occurred: {str(error)}")

# Performance optimizations setup
async def setup_optimizations():
    """Setup performance optimizations"""
    try:
        from cog.performance_optimizations import setup_performance_optimizations
        await setup_performance_optimizations(bot)
        print("✅ Performance optimizations loaded successfully")
    except ImportError:
        print("⚠️ Performance optimizations module not found")

# Run the bot
if __name__ == "__main__":
    if TOKEN:
        # Use setup_hook for async initialization
        async def setup_hook():
            await setup_optimizations()
        
        bot.setup_hook = setup_hook
        bot.run(TOKEN)
    else:
        print("❌ Error: DISCORD_TOKEN not found in environment variables")
