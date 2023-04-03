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
from functions.update_raceroom_pin import update_raceroom_pin
from functions.update_spoiler_room_pin import update_spoiler_room_pin
from functions.update_race_listing import update_race_listing
from functions.db_functions import db_update_race, db_update_racerunner
from classes.Log import Log

async def event_start(interaction, races, event_name, event_prefix, event_desc):
    """
    Starts an event in a given guild (server) with the provided info

    Parameters
    ----------
    interaction : discord.Interaction
        A discord interaction containing our command

    races : dict
        A dictionary containing racerooms

    event_name : str
        A string containing the event's name

    event_prefix : str
        A string containing the event's raceroom prefix

    event_desc : str
        A string containing the event's description

    Returns
    -------
    Nothing
    """
    name = event_name
    prefix = event_prefix
    desc = event_desc

    emessage = ""
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    if profanity.contains_profanity(name):
        await interaction.followup.send('You have attempted to create an event with an inappropriate name')
        return
    if profanity.contains_profanity(prefix):
        await interaction.followup.send('You have attempted to create an event with an inappropriate prefix')
        return
    if profanity.contains_profanity(desc):
        await interaction.followup.send('You have attempted to create an event with an inappropriate description')
        return

    # The server the command was called from
    guild = interaction.guild

    # The channel the message is in
    channel = interaction.channel
    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    race = races[channel.name]

    if race.url is None and race.filename is None and race.isHidden is True:
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
    race.race_start_date = datetime.datetime.now()

    # It's a hidden sync race, so send everyone the seed at once
    if race.isHidden and race.type == RACETYPE_SYNC:
        for member in race.members.keys():
            user = race.members[member].member
            race.url = await getseed_hidden(user, race, races)
            await db_update_racerunner(race, race.members[member].member.id)

    # It's a sync race, so everyone starts at the same time
    if race.type == RACETYPE_SYNC:
        for member in race.members.keys():
            race.members[member].start_date = race.race_start_date
            await db_update_racerunner(race, race.members[member].member.id)

    race.log(LOG_TRIVIAL)

    msg = f"Race started at {race.race_start_date.strftime('%m/%d/%Y, %H:%M:%S')} ET. "
    if race.scheduled_close is not None:
        msg += f'\nThis race is scheduled to close automatically {discord.utils.format_dt(race.scheduled_close,style="R")}'
        msg += "\nAny racers who have not submitted a time by then will automatically forfeit the race!\n"

    if race.isHidden is True and race.type == RACETYPE_ASYNC:
        msg += "\nThe race has started. You may request the seed with `/getseed`\n"
        msg += "Your timer will start once you have been DMed.\n"

    if race.type == RACETYPE_ASYNC and race.isHidden is False:
        msg += "Use the following command to enter your finish time: `/done time hh:mm:ss`"
    else:
        msg += "To finish the race and record your time, type `/done` with no arguments."

    raceblurb = await interaction.channel.send(msg)
    await raceblurb.pin()
    await db_update_race(race)
    await update_raceroom_pin(race.channel_name,races)
    await update_spoiler_room_pin(race.channel_name,races)
    await update_race_listing(race.channel_name,races)
    await interaction.response.send_message('You have started the race!')


    race.log(LOG_TRIVIAL)
    logger = Log()
    pmsg = f"{interaction.guild} -- Race {channel.name} has started!"
    logger.show(pmsg)