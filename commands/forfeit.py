import datetime
from commands.finishrace import finishrace
import discord
import random
import string
import dateutil.parser
from functions.constants import TZ, RACETYPE_ASYNC

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname, parse_done_time, timedelta_to_str
from functions.isRace_room import isRace_room


async def forfeit(interaction, races) -> dict:
    """
    Forfeits the race

    Parameters
    ----------
    interaction : discord.Interaction
        A discord interaction containing our command

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    emessage = ""
    guild = interaction.guild

    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"

    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    # Is the user in this race?
    race = races[channel.name]
    if interaction.user.name not in race.members.keys():
        msg = f"User {interaction.user.name} is not in this race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    if not race.members[interaction.user.name].start_date:
        msg = f"User {interaction.user.name} has not started this race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    racer = race.members[interaction.user.name]
    racer.forfeit = True
    racer.finish_date = dateutil.parser.parse('2099-12-31 23:59:59.999-05:00')

    msg = f"User {interaction.user.name} has forfeit"
    await interaction.response.send_message(msg)
    race.comments += "\n" + msg
    race.log()

    # If it's an async, we don't need to automatically close the race
    if race.type == RACETYPE_ASYNC:
        return

    # Check to see if everyone is done
    for member in race.members.keys():
        if not race.members[member].finish_date:
            return

    # Everyone is done, print the results and close the race
    msg = "This race is over! Here are the results:\n"
    await channel.send(msg)
    await channel.send(race.getResults())
    await finishrace(interaction, races, "Race ended normally")
