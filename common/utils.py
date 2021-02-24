"""Holds helper functions."""
import re
import random

import discord
from PIL import ImageColor
from discord.ext import commands
from discord.ext.commands import CommandError

import common.cfg as cfg
import common.database as db


def to_rgb(hexcode):
    """Convert hexcode to rgb tuple."""
    return ImageColor.getrgb(hexcode)


def heavy_command_not_running(ctx):
    return ctx.guild.id not in cfg.heavy_command_active


class ThemeConverter(commands.Converter):
    """Convert str to theme."""
    async def convert(self, ctx, arg):
        themes = db.get(ctx.guild.id, "themes")

        if not themes:
            raise CommandError("You have no themes")

        theme = theme_lookup(arg, themes)
        if not theme:
            raise CommandError("Theme Not Found")

        return theme


class ColorConverter(commands.Converter):
    async def convert(self, ctx, arg):
        """Find a color in a list of colors based on a query"""
        colors = db.get(ctx.guild.id, "colors")

        print("Converting", arg)

        if not colors:
            raise CommandError("You have no active colors")

        color = color_lookup(arg, colors)
        if not color:
            raise CommandError("Color Not Found")

        return color


def theme_lookup(arg, themes):
    """Find a theme based on a string."""
    # Index lookup
    if arg.isdigit():
        try:
            return themes[int(arg)-1]
        except IndexError:
            pass

    # Name lookup
    for theme in themes:
        if theme["name"].lower() == arg.lower():
            return theme


def color_lookup(arg, colors):
    """Find a color based on a string."""
    # random color
    if arg == "":
        return random.choice(colors)

    # Index lookup
    if arg.isdigit():
        try:
            return colors[int(arg)-1]
        except IndexError:
            pass

    # Name lookup
    for color in colors:
        if color["name"].lower() == arg.lower():
            return color


def validate_hex(hexcode):
    """Validate a hex code."""
    return bool(re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hexcode))


def discord_color(color):
    """converts a color to a discord color for embeds"""
    return discord.Color.from_rgb(*to_rgb(color["hexcode"]))


def find_user_color(user, colors):
    """Extract the color from a list that contains the member id."""
    for color in colors:
        if user.id in color["members"]:
            return color