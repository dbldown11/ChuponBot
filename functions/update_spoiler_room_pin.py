import discord
from functions.db_functions import db_update_race
from discord.utils import get
from classes.Race import Race
#from classes.Buttons import JoinButton, RaceroomControlPanel
import classes.Buttons
from datetime import datetime, timedelta
import functions.constants
from functions.constants import LOG_CRITICAL, TZ

async def update_spoiler_room_pin(race_channel, races):
    """
    Updates the post pinned at the top of the spoiler channel (or replaces it if none exists)

    Parameters
    ----------
    guild : discord.Guild
        The Discord guild that the race lives in

    race_channel : str
        An FF6WC Raceroom bot Race's name

    races : dict
        A dictionary containing racerooms

    Returns

    -------
    dict:
        json data
    """
    race = races[race_channel]
    spoiler_room = discord.utils.get(race.guild.text_channels, name=race.channel_name+'-spoilers')

    finishes = []
    for member in race.members.keys():
        finisher = {}
        if race.members[member].finish_date:
            finisher['name'] = member
            finisher['time'] = race.members[member].time_taken.total_seconds()
            finisher['status'] = 'Finished'
            finishes.append(finisher)
        elif race.members[member].forfeit:
            finisher['name'] = member
            finisher['time'] = timedelta(days=180).total_seconds()
            finisher['status'] = 'Forfeited'
            finishes.append(finisher)

    sorted_finishes = sorted(finishes, key=lambda d: d['time'])

    output = ''
    for pos, finisher in enumerate(sorted_finishes):
        if timedelta(seconds=(sorted_finishes[pos]["time"])) < timedelta(days=180):
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - {str(timedelta(seconds=(sorted_finishes[pos]["time"]))).split(".")[0]}\n'
        else:
            output += f'{pos + 1} - {sorted_finishes[pos]["name"]} - Forfeited\n'

    # add boilerplate if nobody is done yet
    if output == '':
        output += 'No racers have finished or forfeited the race yet.'

    # embed.add_field(name='Current Standings:',value=output,inline=False)
    # spoiler_embed.description = output

    spoiler_embed = discord.Embed(
        title = f'Current results for **{race.channel_name}**',
        description = output,
        colour = discord.Colour.dark_red()
    )

    if race.scheduled_close is not None:
        str_end_note = f"This race is scheduled to end on {discord.utils.format_dt(race.scheduled_close, style = 'F')} ({discord.utils.format_dt(race.scheduled_close,style='R')}).\n"
        str_end_note += f"Any racers who have not completed their seed at that time will automatically forfeit.\n"
        spoiler_embed.add_field(name='Scheduled end:', value=str_end_note, inline=False)

    '''
    counter = 1
    for time in sorted(times.keys()):
        # displaytime = str(time).split(".")[0]
        if time < datetime.timedelta(days=1000):
            output += f'{counter} - {times[time]} -- {time}\n'
        else:
            output += f'{counter} - {times[time]} -- Forfeited\n'
        counter += 1
    # Now show the forfeits
    output += "`\n"

    entrants_msg = '`'
    if len(race.members) == 0:
        entrants_msg = "This race doesn't have any entrants yet!"
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

            entrants_msg += race.members[member].member.name + '--'+ status + '\n'
        entrants_msg += '`\n'
    '''

    #get the posting id from the race, else make a new one
    if race.entrants_spoiler_msg_id:
        #TODO: fix it if the pinned post is gone, basically make a new one and update the race entrantsmsgid
        infopost = spoiler_room.get_partial_message(race.entrants_spoiler_msg_id)
    else:
        infopost = await spoiler_room.send(content=None, embed=spoiler_embed, view=None)
        await infopost.pin()
        race.entrants_spoiler_msg_id = infopost.id
        await db_update_race(races[race_channel])

    # This is my cludgy way of making it make a new infopost if the old post is gone (except triggers if try 404's)
    try:
        await infopost.edit(content=None, embed=spoiler_embed, view=None)
    except:
        infopost = await spoiler_room.send(content=None, embed=spoiler_embed, view=None)
        await infopost.pin()
        race.entrants_spoiler_msg_id = infopost.id
        await db_update_race(races[race_channel])

