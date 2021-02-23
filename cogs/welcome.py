"""Holds commands and listeners related to 
someone joining or the bot joining a server.
"""
import common.database as db
from discord.ext import commands


class WelcomeCommands(commands.Cog):
    """Handles all commands and listeners related to people joining and leaving"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="welcome")
    @commands.has_guild_permissions(manage_channels=True)  # check permissions
    async def set_welcome_channel(self, ctx):
        """Sets or unsets a welcome channel."""
        # Unset channel
        if db.get(ctx.guild.id, "wc") == ctx.channel.id:
            db.guilds.update_one({"_id": ctx.guild.id}, {"$set": {"wc": None}})
            await ctx.send(f"{ctx.channel.mention} is no longer the welcome channel")
        # Set channel
        else:
            db.guilds.update_one(
                {"_id": ctx.guild.id},
                {"$set": {"wc": ctx.channel.id}}
            )
            await ctx.send(f"{ctx.channel.mention} is set as the welcoming channel")

    @commands.Cog.listener()
    async def on_guild_join(guild):
        """Add new guild to database."""
        db.guilds.insert_one(
            {
                "_id": guild.id,
                "prefix": "$",
                "wc": None,
                "colors": [],
                "themes": []
            }
        )

    @commands.Cog.listener()
    async def on_guild_remove(guild):
        """Delete guild from database if bot is kicked/removed"""
        db.guilds.delete_one({"_id": guild.id})

    @commands.Cog.listener()
    async def on_guild_channel_delete(channel):
        """Update database if welcome channel is deleted."""
        db.guilds.update_one(
            {"_id": channel.guild.id, "wc": channel.id},
            {"$set": {"wc": None}}
        )


def setup(bot):
    bot.add_cog(WelcomeCommands(bot))
