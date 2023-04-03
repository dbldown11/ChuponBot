import dateutil.parser
import datetime
from datetime import datetime, timedelta
import discord
from discord.utils import get

from commands.finishrace import finishrace
from functions.constants import RACETYPE_ASYNC
from functions.isRace_room import isRace_room
from functions.update_raceroom_pin import update_raceroom_pin
from functions.update_spoiler_room_pin import update_spoiler_room_pin
from functions.db_functions import db_update_race, db_update_racerunner


async def forfeit(interaction, races) -> dict:
    """
    Forfeits the race

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

    guild = interaction.guild

    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"

    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # Is the user in this race?
    race = races[channel.name]
    if interaction.user.name not in race.members.keys():
        msg = f"User {interaction.user.name} is not in this race"
        await interaction.response.send_message(msg, ephemeral=True)
        return

    if not race.race_start_date:
        msg = f"{interaction.user.name}, the race hasn't been started yet, use `/quit` to leave instead."
        await interaction.response.send_message(msg, ephemeral=True)
        return

    # Has the user started the race yet?
    if not race.members[interaction.user.name].start_date and race.type == 'sync':
        msg = f"{interaction.user.name}, the race hasn't been started yet, use `/quit` to leave instead."
        await interaction.response.send_message(msg, ephemeral=True)
        return

    racer = race.members[interaction.user.name]
    racer.forfeit = True
    # racer.finish_date = dateutil.parser.parse('2099-12-31 23:59:59.999-05:00')
    # give the racer a dummy start time so time_taken will have a value for results/elo purposes
    if race.type == RACETYPE_ASYNC:
        racer.start_date = race.race_start_date
    racer.finish_date = datetime.now() + timedelta(days=180)

    msg = f"User {interaction.user.name} has forfeited the race."
    await interaction.response.send_message(msg)
    race.comments += "\n" + msg
    # race.log()

    done_msg = f":flag_white: {interaction.user.name} has forfeited the race. :flag_white: "
    spoiler_channel = get(guild.channels, name=interaction.channel.name + "-spoilers")
    await spoiler_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    spoil_msg = await spoiler_channel.send(done_msg)

    print(racer.time_taken)
    print(type(racer.time_taken))

    await db_update_race(race)
    await db_update_racerunner(race, racer.member.id)
    await update_raceroom_pin(race.channel_name, races)
    await update_spoiler_room_pin(race.channel_name, races)

    # If it's an async, we don't need to automatically close the race
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
