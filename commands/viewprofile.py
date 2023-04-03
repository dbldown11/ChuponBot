import discord
from functions.db_functions import db_player_retrieve
from discord.utils import get
from classes.Race import Race
from classes.Buttons import ListingButtonsWithJoin
from datetime import datetime
from functions.constants import LOG_CRITICAL, TZ, RACETYPE_ASYNC, RACETYPE_SYNC

async def viewprofile(interaction, user, races):
    """
    Gets the guarded async seed for this channel and DMs it to the user

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call

    user : discord.Member
        A Member to look up a racer profile for

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    racer = await db_player_retrieve(user)
    if racer["pronouns"]:
        embed = discord.Embed(
            title=f'Racer profile: **{user.name}** ({racer["pronouns"]})',
            colour=discord.Colour.blue()
        )
    else:
        embed = discord.Embed(
            title=f'Racer profile: **{user.name}**',
            colour=discord.Colour.blue()
        )

    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name='Stream',value=f'https://www.twitch.tv/{racer["stream_url"]}',inline=False)
    embed.add_field(name='Races Joined (All Races)', value=racer["total_races_all"], inline=True)
    embed.add_field(name='Total Wins (All Races)', value=racer["total_wins_all"], inline=True)
    embed.add_field(name='Current Rating (All Races)', value=racer["rating_all"], inline=True)
    embed.add_field(name='Races Joined (Sync Only)', value=racer["total_races_sync"], inline=True)
    embed.add_field(name='Total Wins (Sync Only)', value=racer["total_wins_sync"], inline=True)
    embed.add_field(name='Current Rating (Sync Only)', value=racer["rating_sync"], inline=True)
    embed.add_field(name='Races Joined (Async Only)', value=racer["total_races_async"], inline=True)
    embed.add_field(name='Total Wins (Async Only)', value=racer["total_wins_async"], inline=True)
    embed.add_field(name='Current Rating (Async Only)', value=racer["rating_async"], inline=True)
    embed.add_field(name='Current GP', value=racer["gp"], inline=False)
    await interaction.response.send_message(content=None, embed=embed, ephemeral=True)