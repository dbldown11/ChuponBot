import functions.constants

async def getraces(interaction, races):
    """
    Gets a list of active races. Must be an admin
    Parameters
    ----------
    interaction : discord.interaction.Interaction
        A discord interaction containing our command
    races : dict
        A dictionary containing racerooms
    Returns
    -------
    Nothing
    """

    if interaction.user.id not in functions.constants.ADMINS:
        return
    rmessage = ""
    if len(races.keys()) == 0:
        rmessage = "There are no active races"
    else:
        rmessage = f"Currently there are {len(races.keys())} active races:\n\n"
        await interaction.response.send_message(rmessage, ephemeral=True)
        for race in races:
            await interaction.followup.send(f"    {race}:\n{races[race]}\n",ephemeral=True)
    # await interaction.response.send_message(rmessage, ephemeral=True)