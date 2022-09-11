import discord
from functions.isRace_room import isRace_room

async def ready(interaction, races) -> dict:
    """
    User command to mark themselves as being ready

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the ready call

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    guild = interaction.guild
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

    if not race.isHidden and not race.url:
        emessage = "There is no seed set for this race yet. Cannot ready up."
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    race.members[interaction.user.name].ready = True
    msg = f"User {interaction.user.name} is ready! "

    unready = []
    for member in race.members.keys():
        if not race.members[member].ready:
            unready.append(race.members[member].member.name)
    if len(unready) > 0:
        msg += f"{len(unready)} players are still preparing."
    else:
        msg += "Everyone is ready! Use `/startrace` to start the race."

    await interaction.response.send_message(msg)