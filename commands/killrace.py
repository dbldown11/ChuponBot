import datetime
import discord
import random
import string
import time
import asyncio
from pytz import timezone
from functions.botconfig import config, env
from functions.db_functions import db_update_race

from better_profanity import profanity
from discord.utils import get

from classes.Log import Log
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
import functions.constants



async def killrace(interaction, races, logmsg=None):
    """
    Admin only - Immediately removes a race room and its spoiler room

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the killrace call

    races : dict
        A dictionary containing races

    logmsg : str (optional)
        A message to write out to the log

    Returns
    -------
    Nothing
    """
    guild = interaction.guild

    logger = Log()
    if interaction.user.id not in functions.constants.ADMINS:
        await interaction.response.send_message("Races can only be force closed by admins!",ephemeral=True)
        return

    cat = get(guild.categories, name=config.get(env,"race_category_general"))
    if interaction.channel.category == cat:
        race_channel = get(guild.channels, name=interaction.channel.name)
        spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))
        await interaction.response.send_message("This room and its spoiler room will be closed in 5 second!")
        await asyncio.sleep(5)

        if race_channel:
            await race_channel.delete()
        if spoiler_channel:
            await spoiler_channel.delete()

        # Remove the listing from #active-races
        if race_channel.name in races.keys():
            listing = None
            listings_channel = get(guild.channels, name="active-races")
            async for message in listings_channel.history(around=races[race_channel.name].opened_date):
                if race_channel.name in message.content:
                    listing = message
                elif len(message.embeds) > 0:
                    for embed in message.embeds:
                        if race_channel.name in embed.title or race_channel.name in message.content:
                            listing = message
            if listing is not None:
                await listing.delete()
            else:
                print(f"tried to delete a listing for {race_channel.name} but didn't find one")

        # Remove this room from the list of races and log it to the JSON
        if race_channel.name in races.keys():
            msg = ''
            tz = timezone('US/Eastern')
            msg += f"Race force killed by {interaction.user.name}"
            if logmsg:
                msg += f"\nClose comments: {logmsg}"
            races[race_channel.name].comments += msg
            races[race_channel.name].close()
            await db_update_race(races[race_channel.name])
            del races[race_channel.name]
        else:
            msg = f"{interaction.guild} -- {interaction.user.name} killed an untracked race - {race_channel.name}"
            logger.show(msg)


    else:
        await interaction.response.send_message("This is not a race room!",ephemeral=True)
