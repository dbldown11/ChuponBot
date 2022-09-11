import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get

from classes.Log import Log
import functions.constants
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.generate_seed import generate_seed
from functions.isRace_room import isRace_room
from functions.get_seedinfo import get_seedinfo
from functions.get_flags import get_flags


async def setseed(interaction, races, **kwargs):
    """
    Sets the guarded async seed for this channel
    Parameters
    ----------
    interaction : discord.Interaction
        A discord interaction containing our command. This interaction has been followed up on!

    races : dict
        A dictionary containing racerooms

    **kwargs: dict
        Keyword arguments for the function

    Keyword arguments
    -----------------
    flagstring : str
        A string containing a flagstring for ff6wc.py

    url: str
        A URL containing a link to a flag to an FF6WC seed

    Returns
    -------
    Nothing
    """
    logger = Log()

    emessage = ""
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    if not isinstance(kwargs, dict):
        emessage += f"args is not a Python dict - Found type {type(args)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in. This is a discord channel object
    channel = interaction.channel
    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.followup.send(msg, ephemeral=True)
        return
    channel_name = str(channel)

    '''
    # Check to see if this is a racing channel - think this is redundant with above
    if channel_name not in races.keys():
        emessage = f"{channel_name} is not a race channel. Not sending seed."
        await channel.send(emessage)
        return None
    '''

    race = races[channel_name]

    # Make sure the user here is an admin
    if not interaction.user.id in race.admins:
        emessage = f"You are not an admin of the race in channel {channel_name}"
        await interaction.followup.send(emessage, ephemeral=True)
        return None

    isFlagset = False
    # Use this to parse a flagset
    if 'flagstring' in kwargs.keys():
        flagstr = kwargs['flagstring']

        try:
            seed = generate_seed(flagstr)
            assert seed["url"]
            race.flags = flagstr
            race.url = seed['url']
            race.version = seed['version']
            race.hash = seed['hash']

        except Exception as e:
            emessage = f"Unable to generate seed from the given flags:\n{flagstr}\n"
            await interaction.followup.send(emessage)
            logger.show(emessage, functions.constants.LOG_CRITICAL)
            logger.show(str(e), functions.constants.LOG_CRITICAL)
            return

        isFlagset = True


    if not isFlagset:
        seed = get_seedinfo(kwargs['url'])
        # assert seed["url"]
        race.flags = get_flags(seed['flags_id'])
        race.url = seed['url']
        race.version = seed['version']
        race.hash = seed['hash']
        msg = "Seed URL accepted!"
        await interaction.followup.send(msg)
        '''
        try:
            seed = get_seedinfo(kwargs['url'])
            # assert seed["url"]
            race.flags = get_flags(seed['flags_id'])
            race.url = seed['url']
            race.version = seed['version']
            race.hash = seed['hash']
            msg = "Seed URL accepted!"
            await interaction.followup(msg)
        except Exception as e:
            msg = "Set a seed using the following syntax:\n"
            msg += "/setseed url <URL>\n"
            msg += "    *ex: /setseed url https://ff6wc.com/seed/E6n93pxzhYEs*\n\n"
            await interaction.followup.send(msg, ephemeral=True)
            return
        '''

    if race.isHidden:
        #await message.delete()
        msg = f"The seed has been set!\n"
        await interaction.followup.send(msg)
    else:
        msg = f"The seed has been set!\n"
        if not isFlagset:
            msg += f"Here is the seed link for this race -- {race.url}"
        else:
            msg += f"Here are the flags:\n{race.flags}\n"
            msg += f"Here is the seed link for this race -- {race.url}"
        seedmsg = await interaction.followup.send(msg)
        await seedmsg.pin()




