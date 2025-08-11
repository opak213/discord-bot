# Discord Bot

A feature-rich Discord bot built with discord.py that includes music playback, temporary voice channels, custom commands, invite management, and both prefix commands and slash commands.

## 🚀 Features

### 🎵 **Music System** 
- Play music from YouTube with queue management
- Support for YouTube URLs and search queries
- Queue management (add, skip, clear, view)
- Playback controls (play, pause, resume, stop)
- Auto-deafen bot for better audio quality

### 🎤 **Temporary Voice Channels**
- Auto-create temporary voice channels when users join a creation channel
- Channel ownership system with management commands
- Auto-cleanup when channels are empty
- Customizable channel templates and limits
- Channel management commands (rename, lock, unlock, limit, delete)

### 🛠️ **Custom Commands System**
- Create unlimited custom commands with variable support
- Built-in variables: {user}, {user_name}, {server}, {channel}, {time}
- Command usage tracking and statistics
- Easy management (add, edit, delete, list)
- Server-specific custom commands

### 🔗 **Invite Management**
- Create custom invite links that automatically assign roles
- Role-based invite system for organized member onboarding
- Invite usage tracking and management
- Automatic cleanup of expired invites
- Both prefix and slash command support

### 🔨 **Basic Moderation**
- Kick members from the server
- Ban members from the server
- Clear messages in bulk (up to 100 at once)
- Permission-based command access

### 💰 **Economy System**
- Virtual currency system with coin balances
- Work command to earn coins
- Gambling system with coin betting
- Daily rewards for active users
- Persistent user balances

### 🎲 **Fun Commands**
- Dice rolling with custom formats (e.g., 2d6)
- Coin flipping
- Magic 8-ball responses
- Random memes and jokes
- User avatar display
- Server and user information

### ⚡ **Slash Commands**
- Modern Discord interactions with slash commands
- Consistent command structure across features
- Better user experience with command suggestions

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

Create a `.env` file with:
```
DISCORD_TOKEN=your_bot_token_here
CLIENT_ID=your_client_id_here
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

## 🎯 Command Reference

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

### 🎤 Temporary Voice Commands (Prefix: !vc)
| Command | Usage | Description |
|---------|--------|-------------|
| `!vc` | `!vc` | Show TempVoice help |
| `!vc rename <name>` | `!vc rename My Channel` | Rename your temporary channel |
| `!vc lock` | `!vc lock` | Lock your temporary channel |
| `!vc unlock` | `!vc unlock` | Unlock your temporary channel |
| `!vc limit <number>` | `!vc limit 5` | Set user limit for your channel |
| `!vc delete` | `!vc delete` | Delete your temporary channel |

### 🛠️ Custom Commands (Prefix: !custom)
| Command | Usage | Description |
|---------|--------|-------------|
| `!custom` | `!custom` | Show custom commands help |
| `!custom add <name> <response>` | `!custom add hello Hello {user}!` | Create a new custom command |
| `!custom edit <name> <response>` | `!custom edit hello New response` | Edit an existing command |
| `!custom delete <name>` | `!custom delete hello` | Delete a custom command |
| `!custom list` | `!custom list` | List all custom commands |
| `!custom info <name>` | `!custom info hello` | Get info about a command |

### 🔗 Invite Management (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!create-invite <role> [uses] [age]` | `!create-invite @Member 10 86400` | Create role-based invite |
| `!list-invites` | `!list-invites` | List all custom invites |
| `!delete-invite <code>` | `!delete-invite abc123` | Delete a custom invite |

### 🔨 Moderation Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!kick` | `!kick @user [reason]` | Kick a member from the server |
| `!ban` | `!ban @user [reason]` | Ban a member from the server |
| `!clear` | `!clear [amount]` | Clear messages (default: 5, max: 100) |

### 💰 Economy Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!balance` | `!balance` | Check your coin balance |
| `!work` | `!work` | Earn coins by working |
| `!gamble <amount>` | `!gamble 100` | Gamble your coins |
| `!daily` | `!daily` | Claim daily reward |

### 🎲 Fun Commands (Prefix: !)
| Command | Usage | Description |
|---------|--------|-------------|
| `!roll` | `!roll [dice]` | Roll dice (default: 1d6, format: 2d6) |
| `!coinflip` | `!coinflip` | Flip a coin |
| `!8ball <question>` | `!8ball Will I win?` | Magic 8-ball |
| `!meme` | `!meme` | Get a random meme |
| `!joke` | `!joke` | Get a random joke |
| `!avatar [@user]` | `!avatar @user` | Get user avatar |
| `!server` | `!server` | Get server information |
| `!userinfo [@user]` | `!userinfo @user` | Get user information |
| `!ping` | `!ping` | Check bot latency |
| `!hello` | `!hello` | Say hello |

### ⚡ Slash Commands (Prefix: /)
| Command | Usage | Description |
|---------|--------|-------------|
| `/create-invite` | `/create-invite role:@Member uses:10 age:24` | Create role-based invite |
| `/list-invites` | `/list-invites` | List custom invites |
| `/hello` | `/hello` | Say hello |
| `/meme` | `/meme` | Get a random meme |
| `/joke` | `/joke` | Get a random joke |
| `/roll` | `/roll dice:2d6` | Roll dice |
| `/coinflip` | `/coinflip` | Flip a coin |

## 🎮 Usage Examples

### Music Usage
```
!join                    # Bot joins your voice channel
!play never gonna give you up   # Play Rick Astley
!queue                   # Show current queue
!skip                    # Skip current song
!leave                   # Bot leaves voice channel
```

### Temporary Voice Channels
```
!vc setup                # Admin: Setup TempVoice system
!vc rename Gaming Room   # Rename your temporary channel
!vc lock                 # Lock your channel
!vc limit 5              # Set user limit to 5
!vc delete               # Delete your temporary channel
```

### Custom Commands
```
!custom add welcome Welcome {user} to {server}!   # Create welcome command
!custom edit welcome Updated welcome message      # Edit existing command
!custom list                                        # List all commands
!custom delete welcome                              # Delete command
```

### Invite Management
```
!create-invite @Member 10 86400   # Create invite for Member role with 10 uses
!list-invites                     # List all active invites
!delete-invite abc123             # Delete specific invite
```

### Economy System
```
!balance                          # Check your coins
!work                             # Earn coins
!gamble 100                       # Gamble 100 coins
!daily                            # Claim daily reward
```

## 🔧 Bot Permissions Required

### Essential Permissions
- Send Messages
- Embed Links
- Read Message History
- Add Reactions
- Use Slash Commands
- View Channels
- Connect to Voice Channels
- Speak in Voice Channels
- Manage Channels (for TempVoice)
- Manage Roles (for invite system)

### Moderation Permissions (Optional)
- Kick Members
- Ban Members
- Manage Messages

## 📁 Configuration Files

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
```

### Configuration Files
- `custom_commands.json` - Stores custom commands
- `invites.json` - Stores custom invite configurations
- `tempvoice_config.json` - Stores TempVoice settings

## 🛠️ Setup Guide

### TempVoice Setup (Admin Only)
1. Run `!vc setup` to automatically create the TempVoice system
2. Users can then join the "➕ Create Channel" to make temporary channels
3. Use `!vc config` to view current settings

### Custom Commands Setup
1. Use `!custom add <name> <response>` to create commands
2. Use variables like `{user}`, `{server}`, `{time}` for dynamic content
3. Use `!custom list` to see all commands

### Invite Management Setup
1. Create roles for different member types
2. Use `!create-invite @role uses age_hours` to create role-based invites
3. New members joining via these invites will automatically get the role

## 🐛 Troubleshooting

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

**TempVoice Not Creating Channels**
1. Run `!vc setup` to configure the system
2. Ensure bot has "Manage Channels" permission
3. Check if creation channel exists

**Custom Commands Not Working**
1. Ensure commands don't conflict with built-in ones
2. Check `custom_commands.json` file exists
3. Verify bot has "Send Messages" permission

**Slash Commands Not Appearing**
1. Wait 1-2 minutes for Discord to register them
2. Try restarting the bot
3. Ensure the bot has "Use Slash Commands" permission

## 📝 Development

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

### Cog Structure
```python
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def mycommand(self, ctx):
        await ctx.send("Hello from cog!")
    
    @discord.app_commands.command()
    async def myslash(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello from slash command!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify your bot token and permissions
4. Check the console for error messages
5. Join our support server for help

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE)
