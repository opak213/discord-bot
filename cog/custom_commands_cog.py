import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.commands_file = 'custom_commands.json'
        self.custom_commands = self.load_commands()
        
    def load_commands(self):
        """Load custom commands from JSON file"""
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_commands(self):
        """Save custom commands to JSON file"""
        with open(self.commands_file, 'w', encoding='utf-8') as f:
            json.dump(self.custom_commands, f, indent=4, ensure_ascii=False)
    
    def replace_variables(self, text, ctx):
        """Replace variables in custom command responses"""
        variables = {
            '{user}': ctx.author.mention,
            '{user_name}': ctx.author.name,
            '{user_id}': str(ctx.author.id),
            '{server}': ctx.guild.name,
            '{server_id}': str(ctx.guild.id),
            '{channel}': ctx.channel.mention,
            '{channel_name}': ctx.channel.name,
            '{prefix}': ctx.prefix,
            '{time}': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for var, value in variables.items():
            text = text.replace(var, value)
        
        return text
    
    @commands.group(name='custom', invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def custom(self, ctx):
        """Custom commands management system"""
        embed = discord.Embed(
            title="🛠️ Custom Commands System",
            description="Manage your server's custom commands",
            color=0x00ff00
        )
        embed.add_field(
            name="Available Subcommands:",
            value=(
                "`!custom add <name> <response>` - Create a new custom command\n"
                "`!custom edit <name> <new_response>` - Edit an existing command\n"
                "`!custom delete <name>` - Delete a custom command\n"
                "`!custom list` - List all custom commands\n"
                "`!custom info <name>` - Get info about a specific command"
            ),
            inline=False
        )
        embed.add_field(
            name="Variables:",
            value=(
                "`{user}` - User mention\n"
                "`{user_name}` - Username\n"
                "`{server}` - Server name\n"
                "`{channel}` - Channel mention\n"
                "`{time}` - Current time"
            ),
            inline=False
        )
        await ctx.send(embed=embed)
    
    @custom.command(name='add')
    @commands.has_permissions(manage_guild=True)
    async def custom_add(self, ctx, name: str, *, response: str):
        """Add a new custom command"""
        name = name.lower()
        
        if name in self.custom_commands:
            await ctx.send(f"❌ Command `{name}` already exists! Use `!custom edit {name}` to modify it.")
            return
        
        if name.startswith('!'):
            name = name[1:]  # Remove ! if provided
        
        # Check if it's trying to override built-in commands
        if self.bot.get_command(name):
            await ctx.send(f"❌ Cannot override built-in command `{name}`!")
            return
        
        self.custom_commands[name] = {
            'response': response,
            'author': str(ctx.author.id),
            'author_name': ctx.author.name,
            'created_at': datetime.now().isoformat(),
            'uses': 0
        }
        
        self.save_commands()
        await ctx.send(f"✅ Custom command `!{name}` has been created successfully!")
    
    @custom.command(name='edit')
    @commands.has_permissions(manage_guild=True)
    async def custom_edit(self, ctx, name: str, *, new_response: str):
        """Edit an existing custom command"""
        name = name.lower()
        
        if name not in self.custom_commands:
            await ctx.send(f"❌ Command `{name}` does not exist!")
            return
        
        self.custom_commands[name]['response'] = new_response
        self.custom_commands[name]['edited_at'] = datetime.now().isoformat()
        self.custom_commands[name]['edited_by'] = str(ctx.author.id)
        
        self.save_commands()
        await ctx.send(f"✅ Custom command `!{name}` has been updated successfully!")
    
    @custom.command(name='delete')
    @commands.has_permissions(manage_guild=True)
    async def custom_delete(self, ctx, name: str):
        """Delete a custom command"""
        name = name.lower()
        
        if name not in self.custom_commands:
            await ctx.send(f"❌ Command `{name}` does not exist!")
            return
        
        del self.custom_commands[name]
        self.save_commands()
        await ctx.send(f"🗑️ Custom command `!{name}` has been deleted successfully!")
    
    @custom.command(name='list')
    @commands.has_permissions(manage_guild=True)
    async def custom_list(self, ctx):
        """List all custom commands"""
        if not self.custom_commands:
            await ctx.send("📭 No custom commands found! Use `!custom add <name> <response>` to create one.")
            return
        
        embed = discord.Embed(
            title="📋 Custom Commands List",
            description=f"Found {len(self.custom_commands)} custom command(s)",
            color=0x00ff00
        )
        
        for name, data in self.custom_commands.items():
            response_preview = data['response'][:50] + "..." if len(data['response']) > 50 else data['response']
            embed.add_field(
                name=f"!{name}",
                value=f"Response: {response_preview}\nUses: {data.get('uses', 0)}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @custom.command(name='info')
    @commands.has_permissions(manage_guild=True)
    async def custom_info(self, ctx, name: str):
        """Get detailed info about a custom command"""
        name = name.lower()
        
        if name not in self.custom_commands:
            await ctx.send(f"❌ Command `{name}` does not exist!")
            return
        
        data = self.custom_commands[name]
        embed = discord.Embed(
            title=f"ℹ️ Command Info: !{name}",
            color=0x00ff00
        )
        
        embed.add_field(name="Response", value=data['response'][:1000], inline=False)
        embed.add_field(name="Created by", value=data['author_name'], inline=True)
        embed.add_field(name="Uses", value=str(data.get('uses', 0)), inline=True)
        embed.add_field(name="Created", value=datetime.fromisoformat(data['created_at']).strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        
        if 'edited_at' in data:
            embed.add_field(name="Last edited", value=datetime.fromisoformat(data['edited_at']).strftime('%Y-%m-%d %H:%M:%S'), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for custom commands in messages"""
        if message.author.bot:
            return
        
        if not message.content.startswith('!'):
            return
        
        # Extract command name
        command_name = message.content[1:].split()[0].lower()
        
        if command_name in self.custom_commands:
            # Process custom command
            data = self.custom_commands[command_name]
            response = data['response']
            
            # Replace variables
            response = self.replace_variables(response, message)
            
            # Increment usage counter
            data['uses'] = data.get('uses', 0) + 1
            self.save_commands()
            
            # Send response
            try:
                # Check if response should be an embed
                if response.startswith('embed:'):
                    embed_content = response[6:].strip()
                    embed = discord.Embed(description=embed_content, color=0x00ff00)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(response)
            except discord.HTTPException:
                await message.channel.send("❌ Failed to send custom command response!")

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
