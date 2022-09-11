import discord
from functions.isRace_room import isRace_room

async def unready(interaction, races) -> dict:
    """
    User command to mark themselves as not being ready

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the unready call

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    # Is the user in this race?
    race = races[channel.name]
    if interaction.user.name not in race.members.keys():
        msg = f"User {interaction.user.name} is not in this race"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    race.members[interaction.user.name].ready = False
    msg = f"User {interaction.user.name} is not ready! "

    unready = 0
    for member in race.members.keys():
        if not race.members[member].ready:
            unready += 1

    msg += f"{unready} players are not ready."

    await interaction.response.send_message(msg)