import json
import logging

from typing import Optional

import discord

from discord.ext import commands

from utils import checks

log = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_admin()
    @commands.command(
        description="Get a list of servers with the specified name.", usage="findserver <name>", hidden=True,
    )
    async def findserver(self, ctx, *, name: str):
        data = await self.bot.cogs["Communication"].handler("find_guild", self.bot.cluster_count, {"name": name})
        guilds = []
        for chunk in data:
            guilds.extend(chunk)
        if len(guilds) == 0:
            await ctx.send(embed=discord.Embed(description="No such guild was found.", colour=self.bot.error_colour))
        else:
            try:
                await ctx.send(embed=discord.Embed(description="\n".join(guilds), colour=self.bot.primary_colour))
            except discord.HTTPException:
                await ctx.send(
                    embed=discord.Embed(
                        description="The message is too long to be sent.", colour=self.bot.error_colour,
                    )
                )

    @checks.is_admin()
    @commands.command(
        description="Get a list of servers the bot shares with the user.", usage="sharedservers <user>", hidden=True
    )
    async def sharedservers(self, ctx, *, user: discord.User):
        data = await self.bot.cogs["Communication"].handler(
            "get_user_guilds", self.bot.cluster_count, {"user_id": user.id}
        )
        guilds = []
        for chunk in data:
            guilds.extend(chunk)
        guild_list = [f"{guild['name']} `{guild['id']}`" for guild in guilds]
        try:
            await ctx.send(embed=discord.Embed(description="\n".join(guild_list), colour=self.bot.primary_colour))
        except discord.HTTPException:
            await ctx.send(
                embed=discord.Embed(description="The message is too long to be sent.", colour=self.bot.error_colour)
            )

    @checks.is_admin()
    @commands.command(
        description="Create an invite to the specified server.", usage="createinvite <server ID>", hidden=True,
    )
    async def createinvite(self, ctx, *, guild_id: int):
        guild = await self.bot.cogs["Communication"].handler("get_guild", 1, {"guild_id": guild_id})
        if not guild:
            await ctx.send(embed=discord.Embed(description="No such guild was found.", colour=self.bot.error_colour))
            return
        invite = await self.bot.cogs["Communication"].handler("invite_guild", 1, {"guild_id": guild_id})
        if not invite:
            await ctx.send(
                embed=discord.Embed(
                    description="No permissions to create an invite link.", colour=self.bot.primary_colour,
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f"Here is the invite link: https://discord.gg/{invite[0]['code']}",
                    colour=self.bot.primary_colour,
                )
            )

    @checks.is_admin()
    @commands.command(description="Make me say something.", usage="echo [channel] <message>", hidden=True)
    async def echo(self, ctx, channel: Optional[discord.TextChannel], *, content: str):
        channel = channel or ctx.channel
        await ctx.message.delete()
        await channel.send(content, allowed_mentions=discord.AllowedMentions(everyone=False))

    @checks.is_admin()
    @commands.command(description="Restart a cluster.", usage="restart <cluster>", hidden=True)
    async def restart(self, ctx, *, cluster: int):
        await ctx.send(embed=discord.Embed(description="Restarting...", colour=self.bot.primary_colour))
        await self.bot.cogs["Communication"].handler("restart", 0, scope="launcher", cluster=cluster)

    @checks.is_admin()
    @commands.command(description="Start a cluster.", usage="start <cluster>", hidden=True)
    async def start(self, ctx, *, cluster: int):
        await ctx.send(embed=discord.Embed(description="Starting...", colour=self.bot.primary_colour))
        await self.bot.cogs["Communication"].handler("start", 0, scope="launcher", cluster=cluster)

    @checks.is_admin()
    @commands.command(description="Stop a cluster.", usage="stop <cluster>", hidden=True)
    async def stop(self, ctx, *, cluster: int):
        await ctx.send(embed=discord.Embed(description="Stopping...", colour=self.bot.primary_colour))
        await self.bot.cogs["Communication"].handler("stop", 0, scope="launcher", cluster=cluster)

    @checks.is_admin()
    @commands.command(description="Perform a rolling restart.", usage="rollrestart", hidden=True)
    async def rollrestart(self, ctx):
        await ctx.send(embed=discord.Embed(description="Rolling a restart...", colour=self.bot.primary_colour))
        await self.bot.cogs["Communication"].handler("roll_restart", 0, scope="launcher")

    @checks.is_admin()
    @commands.command(description="Get clusters' statuses.", usage="status", hidden=True)
    async def status(self, ctx):
        data = await self.bot.cogs["Communication"].handler("get_status", self.bot.cluster_count)
        clusters = {}
        for element in data:
            for key, value in element.items():
                clusters[key] = value
        await ctx.send(
            embed=discord.Embed(
                description=f"```json\n{json.dumps(clusters, indent=4)}```", colour=self.bot.primary_colour,
            )
        )


def setup(bot):
    bot.add_cog(Admin(bot))
