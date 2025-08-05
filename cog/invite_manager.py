import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import asyncio

class InviteManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites_file = 'invites.json'
        self.custom_invites = self.load_invites()
        self.bot.loop.create_task(self.setup_invite_tracking())

    def load_invites(self) -> Dict[str, Dict[str, Any]]:
        """Load custom invites from JSON file"""
        if os.path.exists(self.invites_file):
            try:
                with open(self.invites_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_invites(self):
        """Save custom invites to JSON file"""
        with open(self.invites_file, 'w') as f:
            json.dump(self.custom_invites, f, indent=2, default=str)

    async def setup_invite_tracking(self):
        """Setup invite tracking for all guilds"""
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            try:
                await guild.invites()
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join and assign role based on invite used"""
        try:
            guild = member.guild
            invites_before = self.custom_invites.get(str(guild.id), {})
            
            # Get current invites
            current_invites = await guild.invites()
            
            # Find which invite was used
            for invite in current_invites:
                invite_code = invite.code
                if invite_code in invites_before:
                    invite_data = invites_before[invite_code]
                    
                    # Check if invite has uses left
                    if invite_data.get('uses', 0) > 0:
                        role_id = invite_data['role_id']
                        role = guild.get_role(role_id)
                        
                        if role and role < guild.me.top_role:
                            try:
                                await member.add_roles(role)
                                
                                # Decrease uses count
                                invite_data['uses'] -= 1
                                if invite_data['uses'] <= 0:
                                    # Delete invite if no uses left
                                    try:
                                        invite_obj = discord.utils.get(current_invites, code=invite_code)
                                        if invite_obj:
                                            await invite_obj.delete()
                                        del invites_before[invite_code]
                                    except:
                                        pass
                                
                                self.custom_invites[str(guild.id)] = invites_before
                                self.save_invites()
                                
                                # Log the assignment
                                log_channel = guild.system_channel
                                if log_channel and log_channel.permissions_for(guild.me).send_messages:
                                    embed = discord.Embed(
                                        title="Role Assigned via Invite",
                                        description=f"{member.mention} was assigned the {role.mention} role",
                                        color=discord.Color.green()
                                    )
                                    embed.add_field(name="Invite Code", value=invite_code, inline=True)
                                    embed.add_field(name="Inviter", value=f"<@{invite_data['creator_id']}>", inline=True)
                                    await log_channel.send(embed=embed)
                                
                                break
                                
                            except discord.Forbidden:
                                print(f"Failed to assign role {role.name} to {member.name}")
                            except Exception as e:
                                print(f"Error assigning role: {e}")
                                
        except Exception as e:
            print(f"Error in on_member_join: {e}")

    @commands.command(name='create-invite', help='Create a custom invite link for a specific role')
    @commands.has_permissions(manage_roles=True)
    async def create_invite(self, ctx, role: discord.Role, uses: int = 10, age: int = 86400):
        """Create a custom invite link that assigns a role to new members
        
        Args:
            role: The role to assign to new members
            uses: Number of uses (default: 10)
            age: Age in seconds (default: 86400 = 24 hours)
        """
        try:
            # Check if bot has permission to create invites
            if not ctx.channel.permissions_for(ctx.guild.me).create_instant_invite:
                await ctx.send("❌ I don't have permission to create invites!")
                return

            # Check if role is manageable
            if role >= ctx.guild.me.top_role:
                await ctx.send("❌ I can't assign that role - it's higher than my highest role!")
                return

            if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                await ctx.send("❌ You can't create invites for roles higher than yours!")
                return

            # Create invite
            invite = await ctx.channel.create_invite(
                max_uses=uses,
                max_age=age,
                unique=True,
                reason=f"Custom invite for role {role.name} created by {ctx.author}"
            )

            # Store invite data
            guild_id = str(ctx.guild.id)
            if guild_id not in self.custom_invites:
                self.custom_invites[guild_id] = {}

            self.custom_invites[guild_id][invite.code] = {
                'role_id': role.id,
                'role_name': role.name,
                'creator_id': ctx.author.id,
                'creator_name': str(ctx.author),
                'uses': uses,
                'max_uses': uses,
                'age': age,
                'created_at': datetime.now().isoformat(),
                'channel_id': ctx.channel.id
            }

            self.save_invites()

            embed = discord.Embed(
                title="✅ Custom Invite Created",
                description=f"Invite link created for role: {role.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Invite Link", value=f"https://discord.gg/{invite.code}", inline=False)
            embed.add_field(name="Uses", value=f"{uses}", inline=True)
            embed.add_field(name="Expires", value=f"{age//3600}h {(age%3600)//60}m", inline=True)
            embed.add_field(name="Code", value=f"`{invite.code}`", inline=False)
            
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create invites or manage roles!")
        except Exception as e:
            await ctx.send(f"❌ Error creating invite: {str(e)}")

    @commands.command(name='list-invites', help='List all active custom invites')
    @commands.has_permissions(manage_roles=True)
    async def list_invites(self, ctx):
        """List all active custom invites for this server"""
        try:
            guild_id = str(ctx.guild.id)
            if guild_id not in self.custom_invites or not self.custom_invites[guild_id]:
                await ctx.send("❌ No custom invites found for this server!")
                return

            invites = self.custom_invites[guild_id]
            embed = discord.Embed(
                title=f"📋 Custom Invites for {ctx.guild.name}",
                description=f"Found {len(invites)} active custom invite(s)",
                color=discord.Color.blue()
            )

            for code, data in invites.items():
                role = ctx.guild.get_role(data['role_id'])
                role_mention = role.mention if role else f"Role ID: {data['role_id']}"
                
                embed.add_field(
                    name=f"Code: `{code}`",
                    value=f"Role: {role_mention}\n"
                          f"Uses: {data['uses']}/{data['max_uses']}\n"
                          f"Creator: <@{data['creator_id']}>\n"
                          f"Expires: {data['age']//3600}h {(data['age']%3600)//60}m",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Error listing invites: {str(e)}")

    @commands.command(name='delete-invite', help='Delete a custom invite')
    @commands.has_permissions(manage_roles=True)
    async def delete_invite(self, ctx, code: str):
        """Delete a custom invite
        
        Args:
            code: The invite code to delete
        """
        try:
            guild_id = str(ctx.guild.id)
            if guild_id not in self.custom_invites or code not in self.custom_invites[guild_id]:
                await ctx.send("❌ Invite code not found!")
                return

            # Delete the actual invite
            try:
                invites = await ctx.guild.invites()
                invite_obj = discord.utils.get(invites, code=code)
                if invite_obj:
                    await invite_obj.delete()
            except:
                pass  # Invite might already be deleted

            # Remove from custom invites
            del self.custom_invites[guild_id][code]
            self.save_invites()

            await ctx.send(f"✅ Invite `{code}` has been deleted!")

        except Exception as e:
            await ctx.send(f"❌ Error deleting invite: {str(e)}")

    # Slash Commands
    @discord.app_commands.command(name="create-invite", description="Create a custom invite for a specific role")
    @discord.app_commands.describe(
        role="The role to assign to new members",
        uses="Number of uses (default: 10)",
        age="Age in hours (default: 24)"
    )
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def create_invite_slash(self, interaction: discord.Interaction, role: discord.Role, uses: int = 10, age: int = 24):
        """Create a custom invite link via slash command"""
        try:
            age_seconds = age * 3600
            
            if not interaction.channel.permissions_for(interaction.guild.me).create_instant_invite:
                await interaction.response.send_message("❌ I don't have permission to create invites!", ephemeral=True)
                return

            if role >= interaction.guild.me.top_role:
                await interaction.response.send_message("❌ I can't assign that role!", ephemeral=True)
                return

            invite = await interaction.channel.create_invite(
                max_uses=uses,
                max_age=age_seconds,
                unique=True,
                reason=f"Custom invite for role {role.name}"
            )

            guild_id = str(interaction.guild.id)
            if guild_id not in self.custom_invites:
                self.custom_invites[guild_id] = {}

            self.custom_invites[guild_id][invite.code] = {
                'role_id': role.id,
                'role_name': role.name,
                'creator_id': interaction.user.id,
                'creator_name': str(interaction.user),
                'uses': uses,
                'max_uses': uses,
                'age': age_seconds,
                'created_at': datetime.now().isoformat(),
                'channel_id': interaction.channel.id
            }

            self.save_invites()

            embed = discord.Embed(
                title="✅ Custom Invite Created",
                description=f"Invite link created for role: {role.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Invite Link", value=f"https://discord.gg/{invite.code}", inline=False)
            embed.add_field(name="Uses", value=f"{uses}", inline=True)
            embed.add_field(name="Expires", value=f"{age}h", inline=True)
            
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @discord.app_commands.command(name="list-invites", description="List all active custom invites")
    @discord.app_commands.checks.has_permissions(manage_roles=True)
    async def list_invites_slash(self, interaction: discord.Interaction):
        """List custom invites via slash command"""
        try:
            guild_id = str(interaction.guild.id)
            if guild_id not in self.custom_invites or not self.custom_invites[guild_id]:
                await interaction.response.send_message("❌ No custom invites found!", ephemeral=True)
                return

            invites = self.custom_invites[guild_id]
            embed = discord.Embed(
                title=f"📋 Custom Invites",
                description=f"Found {len(invites)} active invite(s)",
                color=discord.Color.blue()
            )

            for code, data in list(invites.items())[:10]:  # Limit to 10 per embed
                role = interaction.guild.get_role(data['role_id'])
                role_mention = role.mention if role else f"Role ID: {data['role_id']}"
                
                embed.add_field(
                    name=f"Code: `{code}`",
                    value=f"Role: {role_mention}\nUses: {data['uses']}/{data['max_uses']}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        """Clean up when invites are deleted"""
        guild_id = str(invite.guild.id)
        if guild_id in self.custom_invites and invite.code in self.custom_invites[guild_id]:
            del self.custom_invites[guild_id][invite.code]
            self.save_invites()

async def setup(bot):
    await bot.add_cog(InviteManager(bot))
