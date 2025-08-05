import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}
        self.config_file = "tempvoice_config.json"
        self.load_config()
        
    def load_config(self):
        """Load TempVoice configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "create_channel_id": None,
                "category_id": None,
                "channel_name_template": "🎤 {user}'s Channel",
                "max_channels_per_user": 3,
                "delete_delay": 5
            }
            self.save_config()
    
    def save_config(self):
        """Save TempVoice configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice channel join/leave events"""
        if after.channel and after.channel.id == self.config.get("create_channel_id"):
            await self.create_temp_channel(member, after.channel.guild)
        
        if before.channel and before.channel.id in self.temp_channels:
            await self.check_channel_cleanup(before.channel)
    
    async def create_temp_channel(self, member, guild):
        """Create a temporary voice channel for a user"""
        user_id = str(member.id)
        
        user_channels = [c for c in self.temp_channels.values() if c['owner'] == user_id]
        if len(user_channels) >= self.config["max_channels_per_user"]:
            try:
                await member.send(f"You have reached the maximum of {self.config['max_channels_per_user']} temporary channels!")
            except:
                pass
            return
        
        category = guild.get_channel(self.config.get("category_id"))
        if not category:
            category = guild.categories[0] if guild.categories else None
        
        channel_name = self.config["channel_name_template"].format(user=member.display_name)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
            member: discord.PermissionOverwrite(manage_channels=True, manage_roles=True, mute_members=True, deafen_members=True, move_members=True)
        }
        
        try:
            channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )
            
            self.temp_channels[channel.id] = {
                "owner": user_id,
                "created_at": datetime.now().isoformat(),
                "original_name": channel_name
            }
            
            await member.move_to(channel)
            
            embed = discord.Embed(
                title="🎤 Temporary Channel Created!",
                description=f"Your temporary voice channel **{channel_name}** has been created!\n\n"
                           f"**Commands:**\n"
                           f"• Rename: `!vc rename <new_name>`\n"
                           f"• Lock: `!vc lock`\n"
                           f"• Unlock: `!vc unlock`\n"
                           f"• Limit: `!vc limit <number>`\n"
                           f"• Delete: `!vc delete`\n\n"
                           f"Channel will auto-delete when empty for {self.config['delete_delay']} seconds.",
                color=discord.Color.green()
            )
            try:
                await member.send(embed=embed)
            except:
                pass
                
        except discord.Forbidden:
            print(f"Failed to create temp channel for {member.display_name}: Missing permissions")
        except Exception as e:
            print(f"Error creating temp channel: {e}")
    
    async def check_channel_cleanup(self, channel):
        """Check if a temporary channel should be deleted"""
        if channel.id not in self.temp_channels:
            return
        
        if len(channel.members) == 0:
            await asyncio.sleep(self.config["delete_delay"])
            
            try:
                fresh_channel = channel.guild.get_channel(channel.id)
                if fresh_channel and len(fresh_channel.members) == 0:
                    await fresh_channel.delete()
                    del self.temp_channels[channel.id]
            except discord.NotFound:
                if channel.id in self.temp_channels:
                    del self.temp_channels[channel.id]
            except Exception as e:
                print(f"Error deleting temp channel: {e}")
    
    @commands.group(name="vc", invoke_without_command=True)
    async def voice_commands(self, ctx):
        """Temporary voice channel commands"""
        embed = discord.Embed(
            title="🎤 TempVoice Commands",
            description="Available commands for managing your temporary voice channel:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Channel Management",
            value="`!vc rename <name>` - Rename your channel\n"
                  "`!vc lock` - Lock your channel\n"
                  "`!vc unlock` - Unlock your channel\n"
                  "`!vc limit <number>` - Set user limit\n"
                  "`!vc delete` - Delete your channel",
            inline=False
        )
        embed.add_field(
            name="Admin Commands",
            value="`!vc setup` - Setup TempVoice system\n"
                  "`!vc config` - View current configuration",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @voice_commands.command(name="rename")
    async def vc_rename(self, ctx, *, new_name: str):
        """Rename your temporary voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        channel = ctx.author.voice.channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id]["owner"] != str(ctx.author.id):
            await ctx.send("❌ You don't own this temporary channel!")
            return
        
        try:
            await channel.edit(name=new_name)
            await ctx.send(f"✅ Channel renamed to **{new_name}**")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to rename this channel!")
    
    @voice_commands.command(name="lock")
    async def vc_lock(self, ctx):
        """Lock your temporary voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        channel = ctx.author.voice.channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id]["owner"] != str(ctx.author.id):
            await ctx.send("❌ You don't own this temporary channel!")
            return
        
        try:
            await channel.set_permissions(ctx.guild.default_role, connect=False)
            await ctx.send("🔒 Channel locked!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to lock this channel!")
    
    @voice_commands.command(name="unlock")
    async def vc_unlock(self, ctx):
        """Unlock your temporary voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        channel = ctx.author.voice.channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id]["owner"] != str(ctx.author.id):
            await ctx.send("❌ You don't own this temporary channel!")
            return
        
        try:
            await channel.set_permissions(ctx.guild.default_role, connect=True)
            await ctx.send("🔓 Channel unlocked!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unlock this channel!")

    @voice_commands.command(name="limit")
    async def vc_limit(self, ctx, limit: int):
        """Set user limit for your temporary voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        if limit < 0 or limit > 99:
            await ctx.send("❌ Limit must be between 0 and 99!")
            return
        
        channel = ctx.author.voice.channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id]["owner"] != str(ctx.author.id):
            await ctx.send("❌ You don't own this temporary channel!")
            return
        
        try:
            await channel.edit(user_limit=limit)
            await ctx.send(f"✅ User limit set to **{limit}**")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to set the limit!")

    @voice_commands.command(name="delete")
    async def vc_delete(self, ctx):
        """Delete your temporary voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        channel = ctx.author.voice.channel
        if channel.id not in self.temp_channels or self.temp_channels[channel.id]["owner"] != str(ctx.author.id):
            await ctx.send("❌ You don't own this temporary channel!")
            return
        
        try:
            await channel.delete()
            del self.temp_channels[channel.id]
            await ctx.send("🗑️ Channel deleted!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete this channel!")
        except discord.NotFound:
            await ctx.send("❌ Channel not found!")

    @voice_commands.command(name="setup")
    @commands.has_permissions(manage_channels=True)
    async def vc_setup(self, ctx):
        """Setup TempVoice system (Admin only)"""
        embed = discord.Embed(
            title="🎤 TempVoice Setup",
            description="Let's set up the temporary voice channel system!",
            color=discord.Color.blue()
        )
        
        # Create category
        category = await ctx.guild.create_category("🎤 Temporary Channels")
        
        # Create creation channel
        create_channel = await ctx.guild.create_voice_channel(
            name="➕ Create Channel",
            category=category
        )
        
        # Update config
        self.config["create_channel_id"] = create_channel.id
        self.config["category_id"] = category.id
        self.save_config()
        
        embed.add_field(
            name="✅ Setup Complete!",
            value=f"**Creation Channel:** {create_channel.mention}\n"
                  f"**Category:** {category.name}\n\n"
                  f"Users can now join **{create_channel.name}** to create their own temporary voice channels!",
            inline=False
        )
        await ctx.send(embed=embed)

    @voice_commands.command(name="config")
    @commands.has_permissions(manage_channels=True)
    async def vc_config(self, ctx):
        """View current TempVoice configuration (Admin only)"""
        create_channel = ctx.guild.get_channel(self.config.get("create_channel_id"))
        category = ctx.guild.get_channel(self.config.get("category_id"))
        
        embed = discord.Embed(
            title="⚙️ TempVoice Configuration",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Channel Settings",
            value=f"**Creation Channel:** {create_channel.mention if create_channel else 'Not set'}\n"
                  f"**Category:** {category.name if category else 'Not set'}\n"
                  f"**Channel Template:** {self.config['channel_name_template']}\n"
                  f"**Max Channels/User:** {self.config['max_channels_per_user']}\n"
                  f"**Delete Delay:** {self.config['delete_delay']}s",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @voice_commands.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def vc_reset(self, ctx):
        """Reset all temporary channels (Admin only)"""
        deleted = 0
        for channel_id in list(self.temp_channels.keys()):
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.delete()
                    deleted += 1
                except:
                    pass
            del self.temp_channels[channel_id]
        
        self.save_config()
        await ctx.send(f"🧹 Reset complete! Deleted {deleted} temporary channels.")

    @vc_setup.error
    @vc_config.error
    @vc_reset.error
    async def vc_admin_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need **Manage Channels** permission to use this command!")

async def setup(bot):
    await bot.add_cog(TempVoice(bot))
