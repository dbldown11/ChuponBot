from asyncio import constants
import datetime
from commands.finishrace import finishrace
import discord
import random
import string
from functions.constants import TZ, RACETYPE_ASYNC, LOG_TRIVIAL

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname, parse_done_time, timedelta_to_str
from functions.isRace_room import isRace_room


async def done(interaction, races, **kwargs) -> dict:
    """
    Sets the user's finish time

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the command

    races : dict
        A dictionary containing racerooms

    kwargs : dict
        A dictionary containing the arguments we've been given

    Keyword Arguments
    -----------------
    time : str
        A string indicating the elapsed time of a completed race

    Returns
    -------
    Nothing
    """
    guild = interaction.guild

    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    #if not isinstance(kwargs, dict):
    #    emessage += f"args is not a Python dict - Found type {type(args)}\n"
    #elif 'done' not in args.keys():
    #    emessage += f"args did not contain a 'done' key\n"
    #elif 'time' not in args['done'].keys():
    #    emessage += f"args['done'] did not contain a 'time' key\n"

    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await channel.send(msg)
        return

    # Is the user in this race?
    race = races[channel.name]
    if interaction.user.name not in race.members.keys():
        msg = f"User {interaction.user.name} is not in this race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    if not race.members[interaction.user.name].start_date and not race.type == RACETYPE_ASYNC:
        msg = f"User {interaction.user.name} has not started this race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    if race.members[interaction.user.name].finish_date:
        msg = f"User {interaction.user.name} has already finished the race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    # There are many ways the user can screw this up, so we'll have to show this message a lot
    bad_time_message = "Use `/done` with the `time` option and your final time in hh:mm:ss to submit your time. Example: \n    `/done time 00:34:18`\n"

    ## First, if there's some sort of weird error on our part or they didn't submit a string. If this is not
    ## an async, we don't need to do any of this since we just care about when they typed !done
    dt = None
    done_str = None
    if race.type == RACETYPE_ASYNC:
        if not isinstance(kwargs['time'], str) or len(kwargs['time']) < 1:
            await interaction.response.send_message(bad_time_message, ephemeral=True)
            return None

        done_time = kwargs['time']
        print(done_time)

        # This function returns a datetime.timedelta and passes it to our string parser
        try:
            dt = parse_done_time(done_time)
        except Exception as e:
            await interaction.response.send_message(bad_time_message, ephemeral=True)
            return None

    race.members[interaction.user.name].forfeit = False
    race.members[interaction.user.name].finish_date = datetime.datetime.now(TZ)


    # If this is a hidden seed or sync, the racers don't report their own time
    if race.type == RACETYPE_ASYNC:
        race.members[interaction.user.name].start_date = race.members[interaction.user.name].finish_date - dt

    done_str = timedelta_to_str(race.members[interaction.user.name].time_taken)
    race.log(LOG_TRIVIAL)

    # Finally we should have a reasonable time
    done_msg = f"{interaction.user.name} has finished the race with a time of {done_str}!"
    await interaction.response.send_message(f"You have finished the race with a time of {done_str}!", ephemeral=True)
    spoiler_channel = get(guild.channels, name=interaction.channel.name + "-spoilers")
    await spoiler_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    spoil_msg = await spoiler_channel.send(done_msg)
    await spoil_msg.pin()

    # Delete the message if it's a hidden race
    if race.isHidden:
        await message.delete()

    # If it's an async, don't close the room when the last person is done
    if race.type == RACETYPE_ASYNC:
        return

    # Check to see if everyone is done
    for member in race.members.keys():
        if not race.members[member].finish_date:
            return

    # Everyone is done, print the results and close the race
    msg = "This race is over! Here are the results:\n"
    await channel.send(msg)
    await channel.send(race.getResults())
    await finishrace(interaction, races, "Race ended normally")

