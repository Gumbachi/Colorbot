import json
import os
import random

import discord
from discord.ext import commands

from cfg import coll
from classes import Guild
from cogs.colors import color_user
from functions import check_hex, get_prefs, update_prefs, rgb_to_hex
from vars import bot, extensions, get_prefix, waiting_on_hexcode


@bot.event
async def on_ready():
    """Changes presence and collects data from mongo database"""
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.playing,
                                  name=f"@ColorBOT for help"))
    print("Generating Objects...")

    if coll.count_documents():
        await get_prefs()

    # gather new guild ids the bot can see and create Guild objects for them
    new_ids = list(set([guild.id for guild in bot.guilds])
                   -set(list(Guild._guilds.keys())))
    new_guilds = [Guild(id) for id in new_ids]

    print("Updating Database...")
    await update_prefs(new_guilds)  # update mongodb with new guilds
    print("Ready Player One.")


@bot.event
async def on_message(message):
    """Runs whenever a message is sent that the bot can see"""
    # make sure it doesnt run when bot writes message
    if message.author == bot.user:
        return

    # types prefix if bot is mentioned
    if message.mentions and message.mentions[0].id == bot.user.id:
        return await message.channel.send(
            f"Type `{get_prefix(bot, message)}`help for help.")

    # handles message verification if user is adding a color via reaction
    if message.author.id in waiting_on_hexcode.keys():
        id = message.author.id
        hexcode_data = waiting_on_hexcode[id]
        if message.channel.id == hexcode_data["message"].channel.id:
            ctx = await bot.get_context(message)
            if check_hex(message.content):
                await ctx.invoke(bot.get_command("add"),
                                 message.content,
                                 hexcode_data["color"])
            else:
                await ctx.send("Invalid Hexcode. Please try again")
                await hexcode_data["message"].edit(
                    content=f"{hexcode_data['message'].content}**Cancelled**")
        del waiting_on_hexcode[id]  # remove user from pool

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    """Sends a welcome message and attempts to randomly color a user when a
    member joins a server the bot is in"""
    guild = Guild.get_guild(member.guild.id)
    channel = guild.get_welcome()

    # check if welcome channel exists
    if not channel:
        return

    accent = discord.Color.green()

    # make sure embed can be sent with or without colors
    if guild.colors:
        color = guild.rand_color()  # get random color
        accent = discord.Color.from_rgb(*color.rgb)  # discord format

    # generate and send weclome embed message
    embed = discord.Embed(
                title=f"{member.name} has joined the server!",
                description=f"Please give {member.mention} a warm welcome!",
                color=accent)
    embed.set_thumbnail(url=member.avatar_url)
    msg = await channel.send(embed=embed)

    # color the user if applicable
    if guild.colors:
        ctx = await bot.get_context(msg)
        await color_user(ctx, member.name, color.name, trace=False)


@bot.event
async def on_member_remove(member):
    """Sends a goodbye message when a member leaves a server the bot is in"""
    guild = Guild.get_guild(member.guild.id)

    # check if welcome channel exists
    if not guild.welcome:
        return

    welcome_channel = bot.get_channel(guild.welcome)

    # generate and send goodbye message
    embed = discord.Embed(title=f"{member.name} has left the server!",
                          description="They won't be missed",
                          color=discord.Color.red())
    embed.set_thumbnail(url=member.avatar_url)
    await welcome_channel.send(embed=embed)


@bot.event
async def on_guild_join(guild):
    """creates new object and updates database when the bot joins a guild"""
    guild = Guild(guild.id)
    await update_prefs([guild])  # update mongoDB


@bot.event
async def on_guild_remove(guild):
    """Deletes guild object and db document when bot leaves a guild"""
    del Guild._guilds[guild.id]  # remove from internal list
    coll.delete_one({"id": guild.id})  # remove from MongoDB


@bot.event
async def on_guild_update(before, after):
    """Updates Guild object name if changed"""
    guild = Guild.get_guild(before.id)
    guild.name = after.name  # change name
    await update_prefs([guild])  # update mongoDB


@bot.event
async def on_guild_channel_delete(channel):
    """Removes a channel from the Guild object if user deletes it"""
    guild = Guild.get_guild(channel.guild.id)

    # remove from disabled channels
    if channel.id in guild.disabled_channels:
        guild.disabled_channels.remove(channel.id)

    # unsets welcome channel if deleted
    if channel.id == guild.welcome_channel:
        guild.welcome_channel = None

    await update_prefs([guild])  # update MongoDB


@bot.event
async def on_guild_role_delete(role):
    """Removes a role from the Guild object if user deletes it"""
    guild = Guild.get_guild(role.guild.id)

    # sets color role id to none if it is deleted
    if color := guild.get_color('role_id', role.id):
        color.role_id = None

    await update_prefs([guild])  # update MongoDB


@bot.event
async def on_guild_role_update(before, after):
    """Removes a role from the Guild object if user deletes it"""
    guild = Guild.get_guild(before.guild.id)

    # checks if color has role and change color name and hex to reflect change
    if color := guild.get_color('role_id', before.id):
        color.name = after.name
        r, g, b = after.color.r, after.color.g, after.color.b
        color.hexcode = rgb_to_hex((r, g, b))
        color.rgb = (r, g, b)
        await update_prefs([guild])  # update MongoDB

# loads extensions(cogs) listed in vars.py
if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f"Couldnt load {extension}")
            print(e)

bot.run(os.environ["TOKEN"])  # runs the bot
