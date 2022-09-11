import datetime
import discord
import random
import string
import time
import asyncio
import datetime

import functions.constants
from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.constants import TZ


async def finishrace(interaction, races, logmsg=None):
    """
    User command to close out a race room and its spoiler room

    Parameters
    ----------
    interaction : discord.Interaction
        A discord interaction containing our command

    races : dict
        A dictionary containing racerooms

    logmsg : str (optional)
        A message to write out to the log

    Returns
    -------
    Nothing
    """

    if interaction.channel.name not in races.keys():
        await interaction.response.send_message("This is not a race room!", ephemeral=True)
        return

    guild = interaction.guild

    msg = "The following runners have not yet finished/forfeited:\n"
    stillrunning = False
    channel_name = interaction.channel.name
    for runner in races[channel_name].members:
        if not races[channel_name].members[runner].forfeit and not races[channel_name].members[runner].finish_date:
            stillrunning = True
            msg += f"\t{runner}\n"

    if stillrunning:
        await interaction.response.send_message(msg)
        return

    race_channel = get(guild.channels, name=interaction.channel.name)
    spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))

    msg = "This race is over! Here are the results:\n"
    await interaction.channel.send(msg)
    await interaction.channel.send(races[channel_name].getResults())

    await interaction.channel.send(
        f"This room and its spoiler room will be closed in {functions.constants.RACE_ROOM_CLOSE_TIME} seconds!")
    await asyncio.sleep(functions.constants.RACE_ROOM_CLOSE_TIME)

    if race_channel:
        await race_channel.delete()
    if spoiler_channel:
        await spoiler_channel.delete()

    msg = f"\nRace closed by {interaction.user}"
    if logmsg:
        msg += f"\nClose comments: {logmsg}"
    races[channel_name].comments += msg
    races[channel_name].close()

    # DM everyone the results
    results = f"Race {channel_name}:\n" + races[channel_name].getResults()
    for member in races[channel_name].members.keys():
        runner = races[channel_name].members[member].member
        await runner.send(results)

    for admin_id in races[channel_name].admins:
        admin = await guild.query_members(user_ids=[admin_id])
        admin = admin[0]
        await admin.send(results)

    del races[channel_name]
