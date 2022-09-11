import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get
import traceback

from commands.getseed import getseed_hidden
from functions.isRace_room import isRace_room
from functions.constants import TZ, RACETYPE_ASYNC, LOG_TRIVIAL, RACETYPE_SYNC
from classes.Log import Log

async def startrace(interaction, races):
    """
    starts a race in a given guild (server) with the name stored in args

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
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The server the command was called from
    guild = interaction.guild

    # The channel the message is in
    channel = interaction.channel
    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    race = races[channel.name]

    if not race.url:
        emessage = "This race doesn't have a seed yet, so it can't be started."
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    if len(race.members.keys()) == 0 and race.type == RACETYPE_SYNC:
        emessage = "There are no racers yet!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    # Make sure everyone is ready if it's a sync
    if race.type == RACETYPE_SYNC:
        unready = []
        for member in race.members.keys():
            if not race.members[member].ready:
                unready.append(race.members[member].member.name)
        if len(unready) > 0:
            msg = "The race can't start yet because following members are not ready:\n"
            for member in unready:
                msg += f"    {member}\n"
            await interaction.response.send_message(msg)
            return

    if race.race_start_date:
        msg = "This race has already been started. Get going!"
        await interaction.response.send_message(msg)
        return

    # race = races[channel.name] #redundant?
    race.race_start_date = datetime.datetime.now(TZ)

    # It's a hidden sync race, so send everyone the seed at once
    if race.isHidden and race.type == RACETYPE_SYNC:
        for member in race.members.keys():
            user = race.members[member].member
            race.url = await getseed_hidden(user, race)

    # It's a sync race, so everyone starts at the same time
    if race.type == RACETYPE_SYNC:
        for member in race.members.keys():
            race.members[member].start_date = race.race_start_date

    race.log(LOG_TRIVIAL)

    msg = f"Race started at {race.race_start_date.strftime('%m/%d/%Y, %H:%M:%S')} ET. "

    if race.isHidden and race.type == RACETYPE_ASYNC:
        msg += "\nThe race has started. You may request the seed with `/getseed`\n"
        msg += "Your timer will start once you have been DMed.\n"

    if race.type == RACETYPE_ASYNC:
        msg += "Use the following command to enter your finish time: `/done time hh:mm:ss`"
    else:
        msg += "To finish the race and record your time, type `/done` with no arguments."

    await interaction.response.send_message(msg)
    race.log(LOG_TRIVIAL)
    logger = Log()
    pmsg = f"{interaction.guild} -- Race {channel.name} has started!"
    logger.show(pmsg)