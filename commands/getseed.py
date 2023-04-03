import datetime
import discord
import os
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.generate_seed import generate_seed
from classes.Log import Log
from classes.Race import Race
from functions.update_raceroom_pin import update_raceroom_pin
from functions.db_functions import db_update_racerunner
import functions.constants
from functions.constants import TZ


async def getseed(interaction, races) -> False:
    """
    Gets the guarded async seed for this channel and DMs it to the user

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    races : dict
        A dictionary containing racerooms
    Returns
    -------
    Nothing
    """
    logger = Log()
    emessage = ""
    if not isinstance(interaction, discord.Interaction):
        emessage += f"interaction is not a discord.Interaction - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in. This is a discord channel object
    channel = interaction.channel
    channel_name = str(channel)
    guild = interaction.guild

    '''
    try:
        assert '' in args['getseed'].keys()
    except:
        emessage += "There was an error in the getseed function. Contact WhoDat42 or wrjones18"
        await interaction.response.send_message(emessage, ephemeral=True)
        logger.show(emessage, functions.constants.LOG_CRITICAL)
        return None


    # Make sure the user isn't trying to pass anything to the command
    if len(args.keys()) != 1 or 'getseed' not in args.keys() or len(args['getseed']['']) != 0:
        emessage += "Do not pass any commands to the getseed command"
        await interaction.response.send_message(emessage, ephemeral=True)
        return None
    '''

    # Check to see if this is a racing channel
    if channel_name not in races.keys():
        emessage = f"{channel_name} is not a race channel. Not sending seed."
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    race = races[channel_name]
    if race.isHidden and not race.race_start_date:
        smessage = "You are not allowed to request the seed until the race starts"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    if interaction.user.name in race.members.keys():
        if race.members[interaction.user.name].hasSeed:
            emessage = f"@{interaction.user.name}, you should already have the seed! If not, please contact a race admin immediately."
            await interaction.response.send_message(emessage, ephemeral=True)
            return
    else:
        emessage = f"@{interaction.user.name}, you aren't in this race"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    if not race.url and not race.filename:
        emessage = "The seed has not yet been set"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    file = None
    if race.url:
        url = race.url
    elif race.filename:
        path = os.path.join(functions.constants.UPLOADS_PATH, channel_name)
        file = discord.File(os.path.join(path, race.filename))
    version = race.version
    hash = race.hash

    for member_name in race.members.keys():
        if race.members[member_name].member.id == interaction.user.id:
            race.members[member_name].hasSeed = True

    if race.isHidden:
        race.members[interaction.user.name].start_date = datetime.datetime.now(functions.constants.TZ)
        msg = f"User {interaction.user.name} requested seed at {race.members[interaction.user.name].start_date}"
        logger.show(msg)
        race.comments += msg + "\n"

    if race.isHidden:
        await interaction.response.send_message(f"Your seed has been sent! Your timer started approximately {discord.utils.format_dt(datetime.datetime.now(tz=TZ),style='R')}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Your seed has been sent!")

    if race.filename is None:
        smessage = f"Here's your Worlds Collide version {version} seed for **{race.channel.name}**:\n"
        smessage += f"URL: {url}\n"
        smessage += f"Hash: {hash}\n"
    else:
        smessage = f"Here's your custom Worlds Collide seed for **{race.channel.name}**:\n"
        smessage += f"Please note that this file was uploaded by {race.creator} and its contents have not been tested or verified. "
        smessage += f"Only use downloaded files from trusted sources!"
    smessage += "\n"
    if race.isHidden:
        smessage += f"**Your timer has started!** "
        smessage += f"Your official start time is: {discord.utils.format_dt(datetime.datetime.now(tz=TZ),style='T')}\n"
        smessage += f'Good luck and have fun!'

    race.log(functions.constants.LOG_TRIVIAL)
    await update_raceroom_pin(race.channel_name, races)
    await interaction.user.send(content=smessage,file=file)
    await db_update_racerunner(race, interaction.user.id)


async def getseed_hidden(user, race, races) -> str:
    """
    Sends the hidden seed to user. This function should only be called by startrace

    Parameters
    ----------
    guild : discord.guild.Guild
        The server we're on

    user : discord.member.Member
        The person to send the seed to

    race : Race
        An FF6WC-raceroom Race

    races : dict
        A dictionary containing racerooms
    Returns
    -------
    Race URL
    """
    logger = Log()
    emessage = ""
    if not isinstance(user, discord.member.Member):
        emessage += f"user should be a discord.member.Member - Found type {type(user)}\n"
    if not isinstance(race, Race):
        emessage += f"race is not a Race - Found type {type(race)}\n"
    if emessage != "":
        raise Exception(emessage)

    url = race.url
    file = None
    if race.filename:
        path = os.path.join(functions.constants.UPLOADS_PATH, channel_name)
        file = discord.File(os.path.join(path, race.filename))
    version = race.version
    hash = race.hash

    smessage = f"{race.channel_name} has begun! Good luck and have fun!\n\n"
    if race.filename is None:
        smessage += f"Here's your Worlds Collide version {version} seed for **{race.channel.name}**:\n"
        smessage += f"URL: {url}\n"
        smessage += f"Hash: {hash}\n"
        smessage += "\nGood luck and have fun!\n"
    else:
        smessage = f"Here's your custom Worlds Collide seed for **{race.channel.name}**.\n"
        smessage += f"Please note that this file was uploaded by {race.creator} and its contents have not been tested or verified.\n"
        smessage += f"Only use downloaded files from trusted sources!"

    await db_update_racerunner(race, user.id)
    await update_raceroom_pin(race.channel_name, races)
    await user.send(content=smessage, file=file)

    return url