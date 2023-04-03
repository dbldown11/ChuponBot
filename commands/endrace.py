import datetime
import discord
import random
import string
import time
import asyncio
import inflect
from pytz import timezone
from multielo import MultiElo
from datetime import timedelta


from better_profanity import profanity
from discord.utils import get

from classes.Log import Log
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from functions.db_functions import db_update_race, db_update_racerunner
import functions.constants



async def endrace(race, races, logmsg=None):
    """
    Used by the scheduler to end a race at its scheduled time

    Parameters
    ----------
    race : Race
        An FF6WC Raceroom bot Race object

    races : dict
        A dictionary containing races

    logmsg : str (optional)
        A message to write out to the log

    Returns
    -------
    Nothing
    """
    guild = race.guild
    logger = Log()

    p = inflect.engine()

    cat = get(guild.categories, name="Racing")

    race_channel = race.channel
    spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))

    if race_channel:
        await race_channel.send(
            "This race has reached its scheduled end time! \nThe room and its spoiler room will be closed in one minute.")
        await asyncio.sleep(60)
        await race_channel.delete()
    if spoiler_channel:
        await spoiler_channel.delete()

    # Remove the listing from #active-races
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

    # Update the DB entries
    await db_update_race(race)

    # DM everyone the results and gets member IDs in a list for the admin check
    member_ids = []
    results = f"Race {race_channel} has ended. Thanks for playing!\n"

    channel_name = race_channel.name
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
        sorted_finishes[pos]['new_thistype_rating'] = new_thistype_array[pos]
        sorted_finishes[pos]['new_all_rating'] = new_all_array[pos]
        if len(sorted_finishes) > 1:
            sorted_finishes[pos]['earned_gp'] = 50 + (25 * (len(sorted_finishes) - pos - 1))
        else:
            sorted_finishes[pos]['earned_gp'] = 0

    for x in sorted_finishes:
        print(f'sorted_finishes = {x}')

    # TODO: Handle GP wager payouts here

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

    # 6. put the results in a string
    output = ''
    for pos, finisher in enumerate(sorted_finishes):
        if timedelta(seconds=(sorted_finishes[pos]["time"])) < timedelta(days=180):
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - {str(timedelta(seconds=(sorted_finishes[pos]["time"]))).split(".")[0]} - ' \
                      f'Earned {sorted_finishes[pos]["earned_gp"]}GP\n'
        else:
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - Forfeited - Earned 0GP\n'
    print(output)

    # await interaction.response.send_message("Race has been completed and race rooms will now close.", ephemeral=True)
    #race_channel = get(guild.channels, name=interaction.channel.name)
    #spoiler_channel = get(guild.channels, name=''.join([str(race_channel), "-spoilers"]))
    race_channel = channel_name
    results += f"Here are the results:\n" + output
    for member in races[race_channel].members.keys():
        runner = races[race_channel].members[member].member
        member_ids.append(races[race_channel].members[member].member.id)
        await runner.send(results)
        await db_update_racerunner(races[race_channel], runner.id)

    if races[race_channel].creator.id not in member_ids:
        await races[race_channel].creator.send(results)
    #TODO Fix the rating math - add the difference to the racer's actual current rating or else you overwrite it

    # Remove this room from the list of races and log it to the JSON
    if race_channel in races.keys():
        msg = ''
        tz = timezone('US/Eastern')
        msg += f"Race ended by scheduler"
        if logmsg:
            msg += f"\nClose comments: {logmsg}"
        races[race_channel].comments += msg
        races[race_channel].close()
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
                                f'{races[channel_name].members[member].finish_rating_all - races[channel_name].members[member].start_rating_all}' \
                                f' from your rating of {races[channel_name].members[member].start_rating_all} when you joined the race.)\n'
            personal_results += f'Your new rating for {races[channel_name].type} races is {races[channel_name].members[member].finish_rating_thistype} (a change of ' \
                                f'{races[channel_name].members[member].finish_rating_thistype - races[channel_name].members[member].start_rating_thistype}' \
                                f' from your rating of {races[channel_name].members[member].start_rating_thistype} when you joined the race.)\n'
            member_ids.append(races[channel_name].members[member].member.id)
            await runner.send(results + personal_results)
            await db_update_racerunner(races[channel_name], runner.id)

        if races[channel_name].creator.id not in member_ids:
            await races[channel_name].creator.send(results)
        del races[race_channel]
    else:
        msg = f"{guild} -- the scheduler ended an untracked race - {race_channel}"
        logger.show(msg)
