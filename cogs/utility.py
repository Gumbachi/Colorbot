import discord
from discord.ext import commands

from classes import Guild
from functions import update_prefs
from vars import bot


class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update")
    async def update_mongo(self, ctx):
        await update_prefs()

    @commands.command(name="guildinfo")
    async def show_guild_info(self, ctx):
        """Shows guild info in an embed and in terminal"""
        guild = Guild.get_guild(ctx.guild.id)
        print(guild)
        embed = discord.Embed(title="Guild info", description=repr(guild))
        await ctx.send(embed=embed)

    @commands.command(name="colorinfo")
    async def show_all_color_info(self, ctx):
        """Shows the info of all colors in a guild"""
        guild = Guild.get_guild(ctx.guild.id)
        s = "Colors\n"
        for color in guild.colors:
            s += f"    {repr(color)}\n"
        embed = discord.Embed(title="Colors info", description=s)
        print(s)
        await ctx.send(embed=embed)

    @commands.command(name='purge')
    async def delete_messages(self, ctx, amount):
        verified_ids = [
            224506294801793025,
            244574519027564544,
            187273639874396160,
            128595549975871488
        ]
        if ctx.author.id in verified_ids:
            await ctx.channel.purge(limit=int(amount)+1)
            await ctx.send(f"purged {amount} messages", delete_after=2)

    @commands.command(name="repeat", aliases=["print", "write"])
    async def repeat(self, ctx, *msg):
        await ctx.send(" ".join(msg))

    @commands.command(name="check")
    async def is_visible(self, ctx, id):
        if ctx.author.id != 128595549975871488:
            return
        id = int(id)
        if id in [guild.id for guild in bot.guilds]:
            return await ctx.send("Is visible")
        else:
            return await ctx.send("Is not visible")

    @commands.command(name="servers")
    async def count_guilds(self, ctx):
        await ctx.send(len(bot.guilds))

    @commands.command(name="announce")
    async def send_to_all_guilds(self, ctx, *message):
        if ctx.author.id != 128595549975871488:
            return
        #announce_embed = discord.Embed(title="ColorBOT Announcement", description=" ".join(message))
        # unfinished

    @commands.command(name='embed')
    async def test_command(self, ctx):
        embed = discord.Embed(
            title="Test", description="* One\n* Two\n* One\n* Two")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UtilityCommands(bot))
