import datetime
import discord
import os
import random
import string

from better_profanity import profanity
from discord.utils import get

from classes.Log import Log
from commands.getpresets import getpresets
import functions.constants
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.generate_seed import generate_seed
from functions.isRace_room import isRace_room
from functions.get_seedinfo import get_seedinfo
from functions.get_flags import get_flags
from functions.db_functions import db_update_race



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

    file : discord.Attachment
        A discord file containing an FF6WC ROM (we hope)

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

    if race.race_start_date is not None:
        emessage = f"Seed cannot be changed once a race has already been started."
        await interaction.followup.send(emessage, ephemeral=True)
        return None

    isFlagset = False
    # Use this to parse a flagset
    if 'flagstring' in kwargs.keys():
        flagstr = kwargs['flagstring']

        try:
            seed = generate_seed(flagstr)
            #assert seed["url"]
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

    if 'preset' in kwargs.keys():
        presets = getpresets()
        if kwargs['preset'] in presets.keys():
            flagstr = presets[kwargs['preset']]['flags']
        else:
            emessage = f"Unable to find flags for preset {kwargs['preset']}"
            await interaction.followup.send_message(emessage,ephemeral=True)

        try:
            seed = generate_seed(flagstr)
            assert seed["url"]
            race.flags = flagstr
            race.url = seed['url']
            race.version = seed['version']
            race.hash = seed['hash']
            race.preset = kwargs['preset']

        except Exception as e:
            emessage = f"Unable to generate seed from the given flags:\n{flagstr}\n"
            await interaction.followup.send(emessage)
            logger.show(emessage, functions.constants.LOG_CRITICAL)
            logger.show(str(e), functions.constants.LOG_CRITICAL)
            return

        isFlagset = True

    if 'file' in kwargs.keys():
        path = os.path.join(functions.constants.UPLOADS_PATH,channel_name)
        # Make the race's uploads folder if it doesn't exist
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f"Made directories: {path}")
            except Exception as e:
                emessage = f"Unable to create directory {path}"
                raise Exception(emessage)
        # Save the seed to the race's folder in the uploads folder
        race.filename = kwargs['file'].filename
        await kwargs['file'].save(os.path.join(path,race.filename))
        msg = "Seed file accepted!"
        race.url = None
        race.flags = None
        race.preset = None
        if interaction.response != None:
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral = True)

    if not isFlagset and 'url' in kwargs.keys():
        try:
            seed = get_seedinfo(kwargs['url'])
            # assert seed["url"]
            race.flags = seed['flags']
            race.url = seed['url']
            race.version = seed['version']
            race.hash = seed['hash']
            msg = "Seed URL accepted!"
            race.filename = None
            race.preset = None
            if interaction.response != None:
                await interaction.followup.send(msg)
            else:
                await interaction.response.send_message(msg)

        except Exception as e:
            emessage = f"Unable to generate seed from the provided url: `{kwargs['url']}`\n"
            emessage += f"Correct URLs will follow this format: `https://ff6wc.com/seed/<12 character identifier>`"
            await interaction.followup.send(emessage, ephemeral=True)
            logger.show(emessage, functions.constants.LOG_CRITICAL)
            logger.show(str(e), functions.constants.LOG_CRITICAL)
            print(str(e))
            return

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
        if interaction.response != None:
            await interaction.followup.send(msg)
        else:
            await interaction.response.send_message(msg)
    else:
        msg = f"The seed has been set!\n"
        if race.filename:
            msg += f"Here is the seed for this race"
        elif not isFlagset:
            msg += f"Here is the seed link for this race -- {race.url}"
        else:
            if 'preset' in kwargs.keys():
                msg+= f"This seed was rolled from Seedbot's `{race.preset}` preset. "
            msg += f"The flags for this seed are:\n```{race.flags}```\n"
            msg += f"Here is the seed link for this race -- {race.url}"
        if race.filename == None:
            if interaction.response != None:
                seedmsg = await interaction.followup.send(msg,ephemeral=False,suppress_embeds=True)
            else:
                seedmsg = await interaction.response.send_message(msg,ephemeral=False,suppress_embeds=True)
        else:
            path = os.path.join(functions.constants.UPLOADS_PATH,channel_name)
            seed = discord.File(os.path.join(path,race.filename))
            seedmsg = await channel.send(content=msg,file=seed,suppress_embeds=True)
        await seedmsg.pin()

    await db_update_race(race)




