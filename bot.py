import discord
from discord.ext import commands
import os
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
    description='A simple Discord bot',
    activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
)

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

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Don't respond to ourselves
    if message.author == bot.user:
        return
    
    # Check for mentions
    if bot.user.mentioned_in(message):
        await message.channel.send(f"Hello {message.author.mention}! I'm a bot. Use `!help` to see my commands.")
    
    await bot.process_commands(message)

# Basic commands
@bot.command(name='ping', help='Check bot latency')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

@bot.command(name='hello', help='Say hello')
async def hello(ctx):
    """Say hello"""
    await ctx.send(f'Hello {ctx.author.mention}!')

@bot.command(name='server', help='Get server info')
async def server(ctx):
    """Get server information"""
    guild = ctx.guild
    embed = discord.Embed(title=guild.name, description="Server Information", color=0x00ff00)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    await ctx.send(embed=embed)

# Slash commands
@bot.tree.command(name="hello", description="Say hello with slash command")
async def hello_slash(interaction: discord.Interaction):
    """Say hello with slash command"""
    await interaction.response.send_message(f"Hello {interaction.user.mention}! This is a slash command.")

@bot.tree.command(name="userinfo", description="Get user information")
async def userinfo_slash(interaction: discord.Interaction, user: discord.User = None):
    """Get user information"""
    if user is None:
        user = interaction.user
    
    embed = discord.Embed(title=f"{user.name}'s Info", color=0x00ff00)
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
    
    await interaction.response.send_message(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables")
