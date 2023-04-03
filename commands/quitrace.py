import datetime
#from commands.finishrace import finishrace
import discord
import os
import asqlite
import random
import string
from functions.constants import TZ, RACETYPE_ASYNC, DATA_PATH

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname, parse_done_time, timedelta_to_str
from functions.isRace_room import isRace_room
from functions.update_raceroom_pin import update_raceroom_pin
from functions.update_spoiler_room_pin import update_spoiler_room_pin


async def quitrace(interaction, races) -> dict:
    """
    Quits the race

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
        emessage += f"command is not a discord.Interaction - Found type {type(interaction)}\n"

    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # The race being quit from
    race = races[channel.name]

    # Is the user in this race?
    if interaction.user.name not in race.members.keys():
        msg = f"User {interaction.user.name} is not in this race"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # If it's an async, don't close the room when the last person is done
    if race.type == RACETYPE_ASYNC:
        # to be added
        return

    racer = race.members[interaction.user.name]
    if racer.start_date:
        msg = f"User {interaction.user.name}, you have already started the race, you must `/forfeit` instead."
        await interaction.response.send_message(msg, ephemeral=True)
        return

    race.removeRacer(racer)
    # Remove the racer from the db
    path = os.path.join(DATA_PATH, 'testdata.db')
    data = (channel.name, interaction.user.id)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""DELETE FROM race_members WHERE race_name = ? AND user_id = ?""", data)
            await conn.commit()

    msg = f"User {interaction.user.name} has exited the race."
    await update_raceroom_pin(race.channel_name,races)
    await update_spoiler_room_pin(race.channel_name,races)
    await interaction.response.send_message(msg)
