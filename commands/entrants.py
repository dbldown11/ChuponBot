import discord

from functions.isRace_room import isRace_room


async def entrants(interaction, races):
    """
    Get list of entrants

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
    channel = interaction.channel

    if not isRace_room(channel, races):
        msg = "This is not a race room!"
        await interaction.response.send_message(msg,ephemeral=True)
        return

    race = races[channel.name]

    msg = '`'
    if len(race.members) == 0:
        msg = "This race doesn't have any entrants yet!"
    else:
        for member in race.members.keys():
            status = "Not Ready"
            if race.members[member].ready:
                status = "Ready"
            if race.members[member].start_date:
                status = "Running"
            if race.members[member].finish_date:
                status = "Finished"
            if race.members[member].forfeit:
                status = "Forfeited"

            msg += race.members[member].member.name + '--'+ status + '\n'
        msg += '`\n'

    embed = discord.Embed(
    title=f'Current enrants: **{race.channel_name}**',
    colour=discord.Colour.blue(),
    description=msg)

    await interaction.response.send_message(content=None, embed=embed, ephemeral=True)
    #await interaction.response.send_message(msg)