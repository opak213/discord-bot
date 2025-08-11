from flask import Flask, jsonify, request, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from flask_session import Session
import discord
from discord.ext import commands
import asyncio
import threading
import json
import os
import random
import aiohttp
from datetime import datetime
import requests
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './flask_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

Session(app)

# Discord OAuth Configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('https://discord.com/oauth2/authorize?client_id=1399824318644621402&permissions=8&response_type=code&redirect_uri=https%3A%2F%2Fdiscord.com%2Foauth2%2Fauthorize%3Fclient_i', 'http://localhost:5000/auth/callback')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')

# Global bot instance
bot = None
bot_ready = False

# Economy system variables
user_balances = {}
user_inventory = {}

class WebBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Discord bot with web interface'
        )
        
    async def on_ready(self):
        global bot_ready
        bot_ready = True
        print(f'Bot {self.user} is ready for web interface')

    # Basic Commands
    @commands.command(name='ping', help='Check bot latency')
    async def ping(self, ctx):
        """Check bot latency - optimized for faster response"""
        latency = round(self.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name='hello', help='Say hello')
    async def hello(self, ctx):
        """Say hello"""
        await ctx.send(f'👋 Hello {ctx.author.mention}!')

    # Moderation Commands
    @commands.command(name='kick', help='Kick a member')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        await member.kick(reason=reason)
        await ctx.send(f'👢 {member.mention} has been kicked. Reason: {reason or "No reason"}')

    @commands.command(name='ban', help='Ban a member')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server"""
        await member.ban(reason=reason)
        await ctx.send(f'🔨 {member.mention} has been banned. Reason: {reason or "No reason"}')

    @commands.command(name='clear', help='Clear messages')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Clear messages from channel"""
        if amount > 100:
            amount = 100
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'🗑️ Cleared {len(deleted)-1} messages!', delete_after=5)

    # Fun Games
    @commands.command(name='roll', help='Roll dice')
    async def roll(self, ctx, dice: str = '1d6'):
        """Roll dice (format: 2d6 for 2 six-sided dice)"""
        try:
            rolls, limit = map(int, dice.split('d'))
            result = [random.randint(1, limit) for _ in range(rolls)]
            total = sum(result)
            await ctx.send(f'🎲 Rolled: {result} = **{total}**')
        except:
            await ctx.send('❌ Use format like `!roll 2d6`')

    @commands.command(name='coinflip', help='Flip a coin')
    async def coinflip(self, ctx):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        await ctx.send(f'🪙 **{result}**!')

    @commands.command(name='8ball', help='Magic 8-ball')
    async def eightball(self, ctx, *, question):
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
    @commands.command(name='weather', help='Get weather information')
    async def weather(self, ctx, *, city):
        """Get weather information"""
        WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'your_api_key_here')
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
    @commands.command(name='balance', help='Check your balance')
    async def balance(self, ctx):
        """Check your coin balance"""
        user_id = str(ctx.author.id)
        balance = user_balances.get(user_id, 100)
        await ctx.send(f"💰 {ctx.author.mention}, your balance: **{balance}** coins")

    @commands.command(name='work', help='Earn coins')
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def work(self, ctx):
        """Earn coins by working"""
        user_id = str(ctx.author.id)
        earnings = random.randint(10, 50)
        user_balances[user_id] = user_balances.get(user_id, 100) + earnings
        await ctx.send(f"💼 {ctx.author.mention}, you worked and earned **{earnings}** coins!")

    @commands.command(name='gamble', help='Gamble your coins')
    async def gamble(self, ctx, amount: int):
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
            user_balances[user_id] = current_balance + amount
            await ctx.send(f"🎉 {ctx.author.mention}, you won! New balance: **{user_balances[user_id]}** coins")
        else:
            user_balances[user_id] = current_balance - amount
            await ctx.send(f"😢 {ctx.author.mention}, you lost! New balance: **{user_balances[user_id]}** coins")

    @commands.command(name='daily', help='Claim daily reward')
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Claim daily reward"""
        user_id = str(ctx.author.id)
        reward = 100
        user_balances[user_id] = user_balances.get(user_id, 100) + reward
        await ctx.send(f"🎁 {ctx.author.mention}, you claimed your daily reward of **{reward}** coins!")

    # Fun Commands
    @commands.command(name='meme', help='Get a random meme')
    async def meme(self, ctx):
        """Get a random meme"""
        memes = [
            "https://i.imgur.com/8XVsVbN.jpg",
            "https://i.imgur.com/7VPU5b7.jpg",
            "https://i.imgur.com/5VPU5b7.jpg",
            "https://i.imgur.com/9XVsVbN.jpg"
        ]
        await ctx.send(random.choice(memes))

    @commands.command(name='joke', help='Get a random joke')
    async def joke(self, ctx):
        """Get a random joke"""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!"
        ]
        await ctx.send(f"😄 {random.choice(jokes)}")

    @commands.command(name='avatar', help='Get user avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        """Get user avatar"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(title=f"{member.name}'s Avatar", color=0x00ff00)
        embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await ctx.send(embed=embed)

    # Reminder System
    @commands.command(name='remind', help='Set a reminder')
    async def remind(self, ctx, time: str, *, message):
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
    @commands.command(name='server', help='Get server info')
    async def server(self, ctx):
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
    @commands.command(name='userinfo', help='Get user information')
    async def userinfo(self, ctx, member: discord.Member = None):
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

    # Error handling
    async def on_command_error(self, ctx, error):
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

# Initialize bot
def init_bot():
    global bot
    bot = WebBot()
    
    # Load cogs
    async def load_extensions():
        try:
            await bot.load_extension('cog.music_cog')
            await bot.load_extension('cog.invite_manager')
            await bot.load_extension('cog.tempvoice_cog')
            await bot.load_extension('cog.custom_commands_cog')
            print("All cogs loaded successfully")
        except Exception as e:
            print(f"Error loading cogs: {e}")

# Discord OAuth Routes
@app.route('/auth/login')
def discord_login():
    """Redirect to Discord OAuth"""
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email guilds',
        'state': 'random_state_string'  # In production, use proper CSRF token
    }
    
    discord_url = f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"
    return redirect(discord_url)

@app.route('/auth/callback')
def discord_callback():
    """Handle Discord OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return jsonify({"error": "Authorization failed"}), 400
    
    # Exchange code for access token
    token_response = requests.post('https://discord.com/api/oauth2/token', data={
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': DISCORD_REDIRECT_URI
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    
    if not access_token:
        return jsonify({"error": "Failed to get access token"}), 400
    
    # Get user info from Discord
    user_response = requests.get('https://discord.com/api/users/@me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    user_data = user_response.json()
    
    # Get user's guilds
    guilds_response = requests.get('https://discord.com/api/users/@me/guilds', headers={
        'Authorization': f'Bearer {access_token}'
    })
    
    guilds_data = guilds_response.json()
    
    # Store user session
    session['user'] = {
        'id': user_data['id'],
        'username': user_data['username'],
        'discriminator': user_data['discriminator'],
        'avatar': user_data.get('avatar'),
        'email': user_data.get('email'),
        'guilds': guilds_data
    }
    
    session['access_token'] = access_token
    
    return redirect('/dashboard')

@app.route('/auth/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect('/')

@app.route('/auth/user')
def get_user():
    """Get current user info"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    return jsonify(session['user'])

@app.route('/auth/check')
def check_auth():
    """Check if user is authenticated"""
    return jsonify({"authenticated": 'user' in session})

# API Routes
@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Get all bot commands with live data"""
    if not bot_ready or not bot:
        return jsonify({"error": "Bot not ready"}), 503
    
    commands_data = []
    
    # Get prefix commands
    for command in bot.commands:
        if not command.hidden:
            commands_data.append({
                "name": command.name,
                "usage": f"!{command.name} {command.signature}",
                "description": command.help or "No description",
                "aliases": command.aliases,
                "permissions": [str(p) for p in command.checks] if command.checks else ["Send Messages"],
                "examples": [f"!{command.name}"],
                "category": "basic",
                "type": "prefix"
            })
    
    # Get slash commands
    for command in bot.tree.get_commands():
        commands_data.append({
            "name": f"/{command.name}",
            "usage": f"/{command.name}",
            "description": command.description or "No description",
            "aliases": [],
            "permissions": ["Send Messages"],
            "examples": [f"/{command.name}"],
            "category": "slash",
            "type": "slash"
        })
    
    return jsonify({"commands": commands_data})

@app.route('/api/bot/status', methods=['GET'])
def get_bot_status():
    """Get bot connection status"""
    if not bot:
        return jsonify({"status": "offline", "guilds": 0, "users": 0})
    
    return jsonify({
        "status": "online" if bot_ready else "offline",
        "guilds": len(bot.guilds),
        "users": sum(guild.member_count for guild in bot.guilds),
        "uptime": str(datetime.now().replace(tzinfo=None) - bot.user.created_at.replace(tzinfo=None)) if bot_ready else None
    })

@app.route('/api/guilds', methods=['GET'])
def get_guilds():
    """Get list of guilds the bot is in"""
    if not bot_ready:
        return jsonify({"error": "Bot not ready"}), 503
    
    guilds = []
    for guild in bot.guilds:
        guilds.append({
            "id": str(guild.id),
            "name": guild.name,
            "member_count": guild.member_count,
            "icon_url": str(guild.icon.url) if guild.icon else None
        })
    
    return jsonify({"guilds": guilds})

# Root route - redirect to dashboard if logged in, login page if not
@app.route('/')
def index():
    """Root route - redirect based on login status"""
    if 'user' in session:
        # User is logged in, redirect to dashboard
        return redirect('/dashboard')
    else:
        # User is not logged in, redirect to login
        return redirect('/login')

# Static file serving for CSS, JS, and other assets
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JS files"""
    return send_from_directory('js', filename)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve asset files"""
    return send_from_directory('.', filename)

# Login page route
@app.route('/login')
def login_page():
    """Serve the login page"""
    try:
        return send_from_directory('.', 'login.html')
    except FileNotFoundError:
        return "Login page not found", 404

# Dashboard page route
@app.route('/dashboard')
def dashboard_page():
    """Serve the dashboard page - requires authentication"""
    if 'user' not in session:
        return redirect('/login')
    try:
        return send_from_directory('.', 'dashboard.html')
    except FileNotFoundError:
        return "Dashboard page not found", 404

# Protected routes (require authentication)
@app.route('/api/user/guilds', methods=['GET'])
def get_user_guilds():
    """Get guilds where the authenticated user is admin"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if not bot_ready:
        return jsonify({"error": "Bot not ready"}), 503
    
    user_guilds = []
    for guild in bot.guilds:
        member = guild.get_member(int(session['user']['id']))
        if member and member.guild_permissions.administrator:
            user_guilds.append({
                "id": str(guild.id),
                "name": guild.name,
                "member_count": guild.member_count,
                "icon_url": str(guild.icon.url) if guild.icon else None
            })
    
    return jsonify({"guilds": user_guilds})

# Start bot in separate thread
def run_bot():
    init_bot()
    bot.run(DISCORD_BOT_TOKEN)

# Start web server
if __name__ == '__main__':
    # Create session directory
    os.makedirs('./flask_session', exist_ok=True)
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait for bot to be ready
    import time
    time.sleep(5)
    
    # Start web server
    app.run(host='0.0.0.0', port=5000, debug=True)
