import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from classes.RaceRunner import RaceRunner
from functions.constants import TZ, RACETYPE_ASYNC

async def joinrace(guild, interaction, room, races):
    """
    Joins a race in a given guild (server) with the name stored in args

    Parameters
    ----------
    guild : discord.guild.Guild
        The server we're on

    interaction : discord.Interaction
        A discord interaction containing our command

    room : str
        A string containing the name of the race room to be joined

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    join_channel = get(guild.channels, name=room)
    if not join_channel:
        emessage = f"No race called {room} found. Check your spelling and try again!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return


    race = races[join_channel.name]

    if interaction.user.name in race.members.keys():
        emessage = "You've already joined this race!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    rr = RaceRunner()
    rr.member = interaction.user
    rr.join_date = datetime.datetime.now(TZ)
    rr.race = race
    rr.guild = guild
    rr.channel = channel
    if race.type == RACETYPE_ASYNC:
        rr.ready = True

    race.addRacer(rr)


    join_msg = f"{interaction.user.name} has joined the race!"
    response_msg = f"You have joined the race room for {join_channel.mention}"
    await join_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    await interaction.response.send_message(response_msg, ephemeral=True)
    await join_channel.send(join_msg)

