import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname


async def raceinfo(interaction, races):
    """
    Gets information about the race in this room

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the command

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    guild = interaction.guild
    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.message.Message - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    msg = ''
    cat = get(guild.categories, name="Racing")
    if interaction.channel.category == cat:
        race_channel = get(guild.channels, name=interaction.channel.name)
        if race_channel.name in races.keys():
            race = races[race_channel.name]
            msg += str(race)
            await interaction.response.send_message(msg, ephemeral=True)

    else:
        await interaction.response.send_message("This is not a race room!", ephemeral=True)
