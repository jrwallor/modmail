import asyncio
import logging
import typing

import discord

from discord.ext import commands

from utils import checks

log = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_permission = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
            read_message_history=False,
            create_instant_invite=False,
            manage_channels=False,
            manage_roles=False,
            manage_webhooks=False,
            send_tts_messages=False,
            manage_messages=False,
            embed_links=False,
            attach_files=False,
            mention_everyone=False,
            external_emojis=False,
            add_reactions=False
        )
        self.unraid_permission = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            read_message_history=True,
            create_instant_invite=False,
            manage_channels=False,
            manage_roles=False,
            manage_webhooks=False,
            send_tts_messages=False,
            manage_messages=False,
            embed_links=False,
            attach_files=False,
            mention_everyone=False,
            external_emojis=False,
            add_reactions=False
        )

    @checks.in_database()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(
        description="Set or clear the channels to shutdown in a raid.",
        usage="raidchannel [channels]",
        hidden=True
    )
    async def raidchannel(self, ctx, channels: commands.Greedy[discord.TextChannel] = [], *, check=None):
        if check:
            await ctx.send(
                embed=discord.Embed(
                    description=f"The channel(s) are not found. Please try again.", colour=self.bot.error_colour,
                )
            )
            return
        #if len(channels) > 10:
        #    await ctx.send(
        #        embed=discord.Embed(
        #            description="There can at most be 10 channels. Try using the command again but specify less channels.",
        #            colour=self.bot.error_colour,
        #        )
        #    )
        #    return
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "UPDATE data SET raidchannel=$1 WHERE guild=$2", [channel.id for channel in channels], ctx.guild.id,
            )
        await ctx.send(
            embed=discord.Embed(description="The channel(s) are updated successfully.", colour=self.bot.primary_colour)
        )

    @checks.in_database()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command(
        description="Set or clear the roles to remove permissions from.",
        usage="raidrole [roles]",
        hidden=True
    )
    async def raidrole(self, ctx, roles: commands.Greedy[discord.Role] = [], *, check=None):
        if check:
            await ctx.send(
                embed=discord.Embed(
                    description=f"The role(s) are not found. Please try again.", colour=self.bot.error_colour,
                )
            )
            return
        #if len(roles) > 10:
        #    await ctx.send(
        #        embed=discord.Embed(
        #            description="There can at most be 10 roles. Try using the command again but specify less roles.",
        #            colour=self.bot.error_colour,
        #        )
        #    )
        #    return
        async with self.bot.pool.acquire() as conn:
            await conn.execute(
                "UPDATE data SET raidrole=$1 WHERE guild=$2", [role.id for role in roles], ctx.guild.id,
            )
        await ctx.send(
            embed=discord.Embed(description="The role(s) are updated successfully.", colour=self.bot.primary_colour)
        )

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(description="Use to shutdown the server during a raid.",usage="raid", hidden=True)
    async def raid(self, ctx, *, check=None):
        data = await self.bot.get_data(ctx.guild.id)
        channels = data[12]
        roles = data[11]
        if channels:
            try:
                for channel in channels:
                    channel = ctx.guild.get_channel(channel)
                    for role in roles:
                        await channel.set_permissions(ctx.guild.get_role(role), overwrite=self.raid_permission)
            except discord.Forbidden:
                await ctx.send(
                    embed=discord.Embed(
                        description="The changes failed to take. Update my permissions and try again or set the overwrites manually.",
                        colour=self.bot.error_colour,
                    )
                )
                return
        await ctx.send(
            embed=discord.Embed(description="The channels are updated successfully.", colour=self.bot.primary_colour)
        )

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(description="Use to reeopen the server.",usage="unraid", hidden=True)
    async def unraid(self, ctx, *, check=None):
        data = await self.bot.get_data(ctx.guild.id)
        channels = data[12]
        roles = data[11]
        if channels:
            try:
                for channel in channels:
                    channel = ctx.guild.get_channel(channel)
                    for role in roles:
                        await channel.set_permissions(ctx.guild.get_role(role), overwrite=self.unraid_permission)
            except discord.Forbidden:
                await ctx.send(
                    embed=discord.Embed(
                        description="The changes failed to take. Update my permissions and try again or set the overwrites manually.",
                        colour=self.bot.error_colour,
                    )
                )
                return
        await ctx.send(
            embed=discord.Embed(description="The channels are updated successfully.", colour=self.bot.primary_colour)
        )


def setup(bot):
    bot.add_cog(Moderation(bot))
