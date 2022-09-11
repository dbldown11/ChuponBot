import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.generate_seed import generate_seed
from classes.Log import Log
from classes.Race import Race
import functions.constants


async def getseed(guild, message, args, races) -> False:
    """
    Gets the guarded async seed for this channel and DMs it to the user

    Parameters
    ----------
    guild : discord.guild.Guild
        The server we're on

    message : discord.message.Message
        A discord message containing our command

    args : dict
        A dictionary containing the command we've been given
        ex: {'join': {'room': ('myrace-sync',)}}

    races : dict
        A dictionary containing racerooms
    Returns
    -------
    Nothing
    """
    logger = Log()
    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(message, discord.message.Message):
        emessage += f"message is not a discord.message.Message - Found type {type(message)}\n"
    if not isinstance(args, dict):
        emessage += f"args is not a Python dict - Found type {type(args)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in. This is a discord channel object
    channel = message.channel
    channel_name = str(channel)

    try:
        assert '' in args['getseed'].keys()
    except:
        emessage += "There was an error in the getseed function. Contact WhoDat42 or wrjones18"
        await channel.send(emessage)
        logger.show(emessage, functions.constants.LOG_CRITICAL)
        return None

    # Make sure the user isn't trying to pass anything to the command
    if len(args.keys()) != 1 or 'getseed' not in args.keys() or len(args['getseed']['']) != 0:
        emessage += "Do not pass any commands to the getseed command"
        await channel.send(emessage)
        return None

    # Check to see if this is a racing channel
    if channel_name not in races.keys():
        emessage = f"{channel_name} is not a race channel. Not sending seed."
        await channel.send(emessage)
        return None

    race = races[channel_name]
    if race.isHidden and not race.race_start_date:
        smessage = "You are not allowed to request the seed until the race starts"
        await channel.send(smessage)
        return

    if message.author.name in race.members.keys():
        if race.members[message.author.name].hasSeed:
            emessage = f"@{message.author.name} You should already have the seed! If not please contact a race admin immediately"
            await channel.send(emessage)
            return
    else:
        emessage = f"@{message.author.name} You aren't in this race"
        await channel.send(emessage)
        return

    if not race.url:
        emessage = "The seed has not yet been set"
        await channel.send(emessage)
        return

    url = race.url
    version = race.version
    hash = race.hash

    for member_name in race.members.keys():
        if race.members[member_name].member.id == message.author.id:
            race.members[member_name].hasSeed = True

    if race.isHidden:
        race.members[message.author.name].start_date = datetime.datetime.now(functions.constants.TZ)
        msg = f"User {message.author.name} delivered seed at {race.members[message.author.name].start_date}"
        logger.show(msg)
        race.comments += msg + "\n"

    smessage = f"Here's your Worlds Collide version {version} seed for {race.channel.name}:\n"
    smessage += f"URL: {url}\n"
    smessage += f"Hash: {hash}\n"
    smessage += "\n"
    author = interaction.user
    race.log(functions.constants.LOG_TRIVIAL)
    await interaction.followup.send(smessage)


async def getseed_hidden(user, race) -> str:
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
    version = race.version
    hash = race.hash

    smessage = f"Here's your Worlds Collide version {version} seed:\n"
    smessage += f"URL: {url}\n"
    smessage += f"Hash: {hash}\n"
    smessage += "\n"

    await user.send(smessage)

    return url