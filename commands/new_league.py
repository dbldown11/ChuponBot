import datetime
import discord
import random
import string
import os
import asqlite

from classes.Buttons import LeagueBuilderView
from classes.Modals import LeagueBasicModal, LeagueScheduleModal
from better_profanity import profanity
from discord.utils import get

import functions.constants
from functions.constants import DATA_PATH

async def new_league(interaction) -> None:
    """
    Opens a race in a given guild (server) with the name stored in args or generates a name if one isn't provided

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    Returns
    -------
    Nothing
    """
    # Check for admin privs
    if interaction.user.id not in functions.constants.ADMINS:
        await interaction.response.send_message("Races can only be force closed by admins!",ephemeral=True)
        return

    #modal = LeagueBasicModal('Basic League Info')
    #await interaction.response.send_modal(modal)

    #modal = LeagueScheduleModal('League schedule')
    #await interaction.response.send_modal(modal)
    await interaction.response.defer(ephemeral=True)
    await interaction.user.send(content='Please use these buttons to input the info for your new league!', view=LeagueBuilderView(interaction))


