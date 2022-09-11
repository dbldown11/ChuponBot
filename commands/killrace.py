import datetime
import discord
import random
import string
import time
import asyncio
from pytz import timezone


from better_profanity import profanity
from discord.utils import get

from classes.Log import Log
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
import functions.constants



async def killrace(interaction, races):
    """
    Admin only - Immediately removes a race room and its spoiler room

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the killrace call

    races : dict
        A dictionary containing races
    Returns
    -------
    Nothing
    """
    guild = interaction.guild

    logger = Log()
    if interaction.user.id not in functions.constants.ADMINS:
        await interaction.response.send_message("Races can only be force closed by admins!",ephemeral=True)
        return

    cat = get(guild.categories, name="Racing")
    if interaction.channel.category == cat:
        race_channel = get(guild.channels, name=interaction.channel.name)
        spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))
        await interaction.response.send_message("This room and its spoiler room will be closed in 5 second!")
        await asyncio.sleep(5)

        if race_channel:
            await race_channel.delete()
        if spoiler_channel:
            await spoiler_channel.delete()


        # Remove this room from the list of races
        if race_channel.name in races.keys():
            tz = timezone('US/Eastern')
            races[race_channel.name].comments += f"Race force killed by {interaction.user.name}"
            races[race_channel.name].close()



            del races[race_channel.name]
        else:
            msg = f"{message.guild} -- {message.author} killed an untracked race - {race_channel.name}"
            logger.show(msg)
    else:
        await interaction.response.send_message("This is not a race room!",ephemeral=True)
