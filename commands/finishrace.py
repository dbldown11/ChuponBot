import datetime
import discord
import random
import string
import time
import asyncio
import asqlite
import os
import datetime
import inflect
from multielo import MultiElo
from datetime import timedelta

import functions.constants
from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.constants import TZ
from functions.db_functions import db_update_race, db_update_racerunner
from functions.update_race_listing import update_race_listing
from functions.constants import DATA_PATH


async def finishrace(interaction, races, logmsg=None):
    """
    User command to close out a race room and its spoiler room

    Parameters
    ----------
    interaction : discord.Interaction
        A discord interaction containing our command

    races : dict
        A dictionary containing racerooms

    logmsg : str (optional)
        A message to write out to the log

    Returns
    -------
    Nothing
    """

    if interaction.channel.name not in races.keys():
        await interaction.response.send_message("This is not a race room!", ephemeral=True)
        return

    p = inflect.engine()

    guild = interaction.guild

    msg = "The following runners have not yet finished/forfeited:\n"
    stillrunning = False
    channel_name = interaction.channel.name
    for runner in races[channel_name].members:
        if not races[channel_name].members[runner].forfeit and not races[channel_name].members[runner].finish_date:
            stillrunning = True
            msg += f"\t{runner}\n"

    if stillrunning:
        await interaction.response.send_message(msg)
        return

    #TODO: Calculate ELOs here! Have to do this in ranking order though and need to figure out ties

    # 1. make list of dicts of finishers and their times, elos, etc
    finishes = []
    for member in races[channel_name].members.keys():
        finisher = {}
        finisher['name'] = member
        finisher['time'] = races[channel_name].members[member].time_taken.total_seconds()
        finisher['start_rating_thistype'] = races[channel_name].members[member].start_rating_thistype
        finisher['start_rating_all'] = races[channel_name].members[member].start_rating_all
        finishes.append(finisher)


    # 1a DUMMY DATA
    '''
    finishes = [{'name': 'Fiktah', 'time': 5400, 'start_rating_thistype': 1300, 'start_rating_all': 1400},
                {'name': 'DoctorDT', 'time': 5600, 'start_rating_thistype': 1200, 'start_rating_all': 1450},
                {'name': 'Cid', 'time': 5600, 'start_rating_thistype': 1150, 'start_rating_all': 1380},
                {'name': 'Kergsy', 'time': 5500, 'start_rating_thistype': 1310, 'start_rating_all': 1390},
                {'name': 'Mark', 'time': 5750, 'start_rating_thistype': 1200, 'start_rating_all': 1250}]
    '''

    # 2. sort that and make a list out of the keys
    sorted_finishes = sorted(finishes, key=lambda d: d['time'])
    finishes_list = [d['time'] for d in sorted_finishes]
    finish_ranks = []
    for time in finishes_list:
        finish_ranks.append(finishes_list.index(time) + 1)

    print(f'sorted_finishes = {sorted_finishes}')
    print(f'finishes_list = {finishes_list}')
    print(f'finish_ranks = {finish_ranks}')

    # 3. loop through that list and build elo lists in that order

    start_rating_thistype_list = [d['start_rating_thistype'] for d in sorted_finishes]
    start_rating_all_list = [d['start_rating_all'] for d in sorted_finishes]
    print(f'start_rating_thistype_list = {start_rating_thistype_list}')
    print(f'start_rating_all_list = {start_rating_all_list}')

    # 4. run the elo script

    elo = MultiElo()
    if len(finish_ranks) > 1:
        new_thistype_array = elo.get_new_ratings(start_rating_thistype_list, result_order=finish_ranks)
        new_all_array = elo.get_new_ratings(start_rating_all_list, result_order=finish_ranks)
    else:
        new_thistype_array = start_rating_thistype_list
        new_all_array = start_rating_all_list
    print(new_thistype_array)
    print(new_all_array)

    # 5. run through the list of finishers in order of completion and update their elo's
    for pos, racer in enumerate(sorted_finishes):
        print(f"pos is {pos}")
        print(f"racer is {racer}")
        sorted_finishes[pos]['new_thistype_rating'] = new_thistype_array[pos]
        sorted_finishes[pos]['new_all_rating'] = new_all_array[pos]
        sorted_finishes[pos]['finish_pos'] = pos + 1
        if len(sorted_finishes) > 1:
            sorted_finishes[pos]['gp_earned'] = 50 + (25 * (len(sorted_finishes) - pos - 1))
        else:
            sorted_finishes[pos]['gp_earned'] = 0

    # this is debug info
    for x in sorted_finishes:
        print(f'sorted_finishes = {x}')

    #TODO: Handle GP wager payouts here

    for runner in races[channel_name].members.keys():
        for finisher in sorted_finishes:
            if finisher['name'] == runner:
                member_id = races[channel_name].members[runner].member.id
                races[channel_name].members[runner].finish_pos = finisher['finish_pos']
                races[channel_name].members[runner].gp_earned = finisher['gp_earned']
                races[channel_name].members[runner].finish_rating_thistype = finisher['new_thistype_rating']
                races[channel_name].members[runner].finish_rating_all = finisher['new_all_rating']
                path = os.path.join(DATA_PATH, 'testdata.db')
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as cursor:
                        res = await cursor.execute("SELECT gp FROM players WHERE user_id = :userid", {"userid": member_id})
                        db_data = await res.fetchone()
                        old_gp = db_data[0]
                        new_gp = old_gp + finisher['gp_earned']
                        data = (new_gp, finisher['new_all_rating'], finisher['new_thistype_rating'], member_id)
                        if races[channel_name].type == 'sync':
                            await cursor.execute("UPDATE players SET gp = ?, rating_all = ?, rating_sync = ? "
                                                 "WHERE user_id = ?", data)
                        else:
                            await cursor.execute("UPDATE players SET gp = ?, rating_all = ?, rating_async = ? "
                                                 "WHERE user_id = ?", data)
                        await conn.commit()

    #6. put the results in a string
    output = ''
    for pos, finisher in enumerate(sorted_finishes):
        if timedelta(seconds=(sorted_finishes[pos]["time"])) < timedelta(days=180):
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - {str(timedelta(seconds=(sorted_finishes[pos]["time"]))).split(".")[0]} - ' \
                      f'Earned {sorted_finishes[pos]["gp_earned"]}GP\n'
        else:
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - Forfeited - Earned 0GP\n'
    print(output)

    # await interaction.response.send_message("Race has been completed and race rooms will now close.", ephemeral=True)
    race_channel = get(guild.channels, name=interaction.channel.name)
    spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))

    msg = "This race is over! Here are the results:\n"
    await interaction.channel.send(msg)
    #await interaction.channel.send(races[channel_name].getResults())
    await interaction.channel.send(output)
    await update_race_listing(race_channel.name,races)

    await interaction.channel.send(
        f"This room and its spoiler room will be closed in {functions.constants.RACE_ROOM_CLOSE_TIME} seconds!")
    await asyncio.sleep(functions.constants.RACE_ROOM_CLOSE_TIME)

    if race_channel:
        await race_channel.delete()
    if spoiler_channel:
        await spoiler_channel.delete()

    if race_channel.name in races.keys():
        listing = None
        listings_channel = get(guild.channels, name="active-races")
        async for message in listings_channel.history(around=races[race_channel.name].opened_date):
            if race_channel.name in message.content:
                listing = message
            elif len(message.embeds) > 0:
                for embed in message.embeds:
                    if race_channel.name in embed.title or race_channel.name in message.content:
                        listing = message
        if listing is not None:
            await listing.delete()
        else:
            print(f"tried to delete a listing for {race_channel.name} but didn't find one")

    msg = f"\nRace closed by {interaction.user}"
    if logmsg:
        msg += f"\nClose comments: {logmsg}"
    races[channel_name].comments += msg
    races[channel_name].close()

    await db_update_race(races[channel_name])

    # DM everyone the results and gets member IDs in a list for the admin check
    member_ids = []
    results = f"Race **{channel_name}** has ended. Thanks for playing!\n"
    results += f"Here are the results:\n" + races[channel_name].getResults()
    for member in races[channel_name].members.keys():
        personal_results = ''
        runner = races[channel_name].members[member].member
        if races[channel_name].members[member].finish_pos == 1:
            personal_results = f':trophy: Congratulations on finishing in ' \
                               f'{p.number_to_words(p.ordinal(races[channel_name].members[member].finish_pos))} place! :trophy:\n'
        else:
            personal_results = f'You finished in ' \
                               f'{p.number_to_words(p.ordinal(races[channel_name].members[member].finish_pos))} place.\n'
        personal_results += f'You have earned {races[channel_name].members[member].gp_earned} GP.\n'
        personal_results += f'Your new rating for all race types is {races[channel_name].members[member].finish_rating_all} (a change of ' \
                            f'{races[channel_name].members[member].finish_rating_all-races[channel_name].members[member].start_rating_all}' \
                            f' from your rating of {races[channel_name].members[member].start_rating_all} when you joined the race.)\n'
        personal_results += f'Your new rating for {races[channel_name].type} races is {races[channel_name].members[member].finish_rating_thistype} (a change of ' \
                            f'{races[channel_name].members[member].finish_rating_thistype-races[channel_name].members[member].start_rating_thistype}' \
                            f' from your rating of {races[channel_name].members[member].start_rating_thistype} when you joined the race.)\n'
        member_ids.append(races[channel_name].members[member].member.id)
        await runner.send(results + personal_results)
        await db_update_racerunner(races[channel_name], runner.id)

    if races[channel_name].creator.id not in member_ids:
        await races[channel_name].creator.send(results)
    '''
    for admin_id in races[channel_name].admins:
        if admin_id not in member_ids:
            admin = discord.utils.get(guild.members, id=admin_id)
            await admin.send(results)
    '''
    del races[channel_name]
