import datetime
import discord
import os
import asqlite
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.botconfig import config, env
from classes.RaceRunner import RaceRunner
from functions.db_functions import db_player_check_init
from functions.constants import TZ, RACETYPE_SYNC, RACETYPE_ASYNC, DATA_PATH

async def joinrace(guild, interaction, room, races):
    """
    Joins a race in a given guild (server) with the name stored in args

    Parameters
    ----------
    guild : discord.guild.Guild
        The server we're on

    interaction : discord.Interaction
        A discord interaction containing our command

    room : str
        A string containing the name of the race room to be joined

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    Nothing
    """
    emessage = ""
    if not isinstance(guild, discord.guild.Guild):
        emessage += f"guild is not a discord.guild.Guild - Found type {type(guild)}\n"
    if not isinstance(interaction, discord.Interaction):
        emessage += f"message is not a discord.Interaction - Found type {type(interaction)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel the message is in
    channel = interaction.channel

    join_channel = get(guild.channels, name=room)
    if not join_channel:
        emessage = f"No race called {room} found. Check your spelling and try again!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return


    race = races[join_channel.name]

    if interaction.user.name in race.members.keys():
        emessage = "You've already joined this race!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    ### Add a check for race restriction ### DT 4/6/23
    if race.restrict_role_id is not None:
        # Get guild members with this role
        role = discord.guild.get(interaction.guild.roles, id=race.restrict_role_id)
        if interaction.user not in role.members:
            emessage = "You are not eligible to join this race!"
            await interaction.response.send_message(emessage, ephemeral=True)
            return
    ###

    # check if player is registered in the guild's playerbase
    await db_player_check_init(interaction.user) #this might fail due to users not having guilds, we'll see

    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            if race.type == RACETYPE_SYNC:
                row = await cursor.execute("SELECT rating_sync, rating_all FROM players WHERE user_id = ?", (interaction.user.id,))
            else:
                row = await cursor.execute("SELECT rating_async, rating_all FROM players WHERE user_id = ?", (interaction.user.id,))
            ratings = await row.fetchone()

    rr = RaceRunner()
    rr.member = interaction.user
    rr.join_date = datetime.datetime.now()
    rr.race = race
    rr.guild = guild
    rr.channel = channel
    rr.start_rating_thistype = ratings[0]
    rr.start_rating_all = ratings[1]
    if race.type == RACETYPE_ASYNC:
        rr.ready = True

    race.addRacer(rr)
    # add the race entrant to the db
    path = os.path.join(DATA_PATH, 'testdata.db')
    data = (rr.member.id, rr.race.channel_name, rr.join_date, rr.start_date, rr.finish_date, rr.ready, rr.forfeit,
            rr.time_taken, rr.guild.id, rr.hasSeed, rr.start_rating_thistype, rr.start_rating_all)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""INSERT INTO race_members (user_id, race_name, join_date, start_date, finish_date,
            isready, isforfeit, time_taken, guild, hasseed, start_rating_thistype, start_rating_all) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
            await conn.commit()

    join_msg = f"{interaction.user.name} has joined the race!"
    response_msg = f"You have joined the race room for {join_channel.mention}"
    await join_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    await interaction.response.send_message(response_msg, ephemeral=True)
    await join_channel.send(join_msg)

