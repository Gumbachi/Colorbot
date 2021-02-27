from discord.ext import commands
from common.cfg import admin_ids

import common.database as db
from .catalog import Catalog


class AdminCommands(commands.Cog):
    """Handles all admin restricted commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="purge")
    async def delete_messages(self, ctx, amount):
        """purge a set amount of messages!"""
        if ctx.author.id in admin_ids:
            await ctx.channel.purge(limit=int(amount)+1)
            await ctx.send(f"purged {amount} messages", delete_after=2)

    @commands.command(name="test")
    async def test_database(self, ctx):
        print(Catalog.instances)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
