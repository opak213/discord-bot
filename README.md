# Discord Bot

A feature-rich Discord bot built with discord.py that includes music playback, moderation tools, games, utilities, and both prefix commands and slash commands.

## Features

- ✅ **Music System** - Play music from YouTube with queue management
- ✅ **Moderation Tools** - Kick, ban, clear messages
- ✅ **Fun Games** - Dice rolling, coin flip, 8-ball, memes
- ✅ **Weather System** - Real-time weather information
- ✅ **Reminder System** - Set custom reminders
- ✅ **Server & User Info** - Detailed server and user information
- ✅ **Slash Commands** - Modern Discord interactions
- ✅ **Error Handling** - Comprehensive error management

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

Create a `.env` file with:
```
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_client_id_here
WEATHER_API_KEY=your_openweathermap_api_key
```

### 3. Invite the Bot to Your Server

Use this URL to invite your bot:
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=8&scope=bot%20applications.commands
```

### 4. Run the Bot

```bash
python enhanced_bot.py
```

## Command Reference

### 🎵 Music Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!join` | `!join` | Join your voice channel |
| `!leave` | `!leave` | Leave the voice channel |
| `!play` | `!play <song_name_or_url>` | Play a song from YouTube |
| `!skip` | `!skip` | Skip the current song |
| `!queue` | `!queue` | Show the current music queue |
| `!clearqueue` | `!clearqueue` | Clear the music queue |
| `!pause` | `!pause` | Pause the current song |
| `!resume` | `!resume` | Resume paused music |
| `!stop` | `!stop` | Stop music and clear queue |
| `!nowplaying` | `!nowplaying` | Show currently playing song |

### 🔨 Moderation Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!kick` | `!kick @user [reason]` | Kick a member from the server |
| `!ban` | `!ban @user [reason]` | Ban a member from the server |
| `!clear` | `!clear [amount]` | Clear messages (default: 5, max: 100) |

### 🎲 Fun & Games (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!roll` | `!roll [dice]` | Roll dice (default: 1d6, format: 2d6) |
| `!coinflip` | `!coinflip` | Flip a coin |
| `!8ball` | `!8ball <question>` | Magic 8-ball |
| `!meme` | `!meme` | Get a random meme |
| `!joke` | `!joke` | Get a random joke |
| `!avatar` | `!avatar [@user]` | Get user avatar |

### 🌤️ Utility Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!weather` | `!weather <city>` | Get weather for a city |
| `!remind` | `!remind <time> <message>` | Set a reminder (format: 10s, 5m, 1h, 1d) |
| `!server` | `!server` | Get server information |
| `!userinfo` | `!userinfo [@user]` | Get user information |

### 🎯 Basic Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!ping` | `!ping` | Check bot latency |
| `!hello` | `!hello` | Say hello |

### ⚡ Slash Commands (Prefix: /)
| Command | Usage | Description |
|---------|--------|-------------|
| `/hello` | `/hello` | Say hello with slash command |
| `/userinfo` | `/userinfo [user]` | Get user information |
| `/meme` | `/meme` | Get a random meme |
| `/joke` | `/joke` | Get a random joke |
| `/roll` | `/roll [dice]` | Roll dice (default: 1d6) |
| `/coinflip` | `/coinflip` | Flip a coin |

## Usage Examples

### Music Usage
```
!join                    # Bot joins your voice channel
!play never gonna give you up   # Play Rick Astley
!queue                   # Show current queue
!skip                    # Skip current song
!leave                   # Bot leaves voice channel
```

### Moderation Usage
```
!kick @username spamming  # Kick user for spam
!ban @username 7d        # Ban user for 7 days
!clear 50                # Clear 50 messages
```

### Fun & Games Usage
```
!roll 2d6                # Roll two six-sided dice
!coinflip                # Flip a coin
!8ball Will it rain?     # Magic 8-ball
!meme                    # Get a random meme
```

### Utility Usage
```
!weather London          # Get weather for London
!remind 5m Take a break  # Set reminder in 5 minutes
!server                  # Get server info
```

## Bot Permissions Required

### Essential Permissions
- Send Messages
- Embed Links
- Read Message History
- Add Reactions
- Use Slash Commands
- View Channels
- Connect to Voice Channels
- Speak in Voice Channels

### Moderation Permissions (Optional)
- Kick Members
- Ban Members
- Manage Messages
- Manage Channels

## Configuration Files

### requirements.txt
```
discord.py>=2.3.0
python-dotenv>=1.0.0
yt-dlp>=2023.7.6
aiohttp>=3.8.0
```

### .env Template
```
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_client_id_here
WEATHER_API_KEY=your_openweathermap_api_key
```

## Troubleshooting

### Common Issues

**Bot Not Responding**
1. Check if the bot is online in your server
2. Verify the token in `.env` is correct
3. Check console for error messages
4. Ensure bot has necessary permissions

**Music Commands Not Working**
1. Ensure bot has voice permissions
2. Check if you're in a voice channel
3. Verify YouTube links are valid
4. Ensure FFmpeg is installed on your system

**Slash Commands Not Appearing**
1. Wait 1-2 minutes for Discord to register them
2. Try restarting the bot
3. Ensure the bot has "Use Slash Commands" permission
4. Check if commands are synced with `!sync` (admin only)

**Weather Commands**
1. Get free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Add your API key to `.env` file
3. Restart the bot

## Development

### Adding New Commands

**Prefix Commands:**
```python
@bot.command(name='newcommand')
async def newcommand(ctx, arg1, arg2=None):
    """Description of the command"""
    await ctx.send(f"Response with {arg1} and {arg2}")
```

**Slash Commands:**
```python
@bot.tree.command(name="newcommand")
async def newcommand_slash(interaction: discord.Interaction, parameter: str):
    """Description of the slash command"""
    await interaction.response.send_message(f"Response with {parameter}")
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify your bot token and permissions
4. Check the console for error messages
