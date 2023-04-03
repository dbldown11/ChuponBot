import discord
from discord.utils import get
from classes.Race import Race
#from classes.Buttons import JoinButton, RaceroomControlPanel
import classes.Buttons
from datetime import datetime
import functions.constants
from functions.constants import LOG_CRITICAL, TZ
from functions.db_functions import db_update_race

async def update_raceroom_pin(race_channel, races):
    """
    Updates the post pinned at the top of the race channel (or replaces it if none exists)

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

    str_racer_cmds = f"    `/raceinfo`             - See information about this race\n"
    str_racer_cmds += f"    `/entrants`             - Shows the entrants for this race\n"
    str_racer_cmds += f"    `/ready`                - Mark yourself ready\n"
    str_racer_cmds += f"    `/unready`              - Mark yourself unready\n"
    str_racer_cmds += f"    `/ff or /forfeit`       - Forfeit\n"
    str_racer_cmds += f"    `/quit`                 - Quit the race\n"
    str_racer_cmds += f"    `/getseed`              - DMs you a link to download the seed for this race\n"



    str_admin_cmds = f"    `/setseed flagstring`   - If you're a race admin, use this to set the flags for the race seed\n"
    str_admin_cmds += f"    `/setseed url`          - If you're a race admin, use this to set the URL for the race seed\n"
    str_admin_cmds += f"    `/startrace`            - Start the race\n"
    str_admin_cmds += f"    `/finishrace`           - Close this race room after a brief delay\n"
    if race.isHidden and race.type == functions.constants.RACETYPE_SYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
        str_hidden_note = f"\nNOTE: This is a hidden seed race. You will be DMed a link to download the seed when "
        str_hidden_note += f"the race starts. The timer starts as soon as you receive the DM, so be quick when "
        str_hidden_note += f"downloading the seed!\n"

    elif race.isHidden and race.type == functions.constants.RACETYPE_ASYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
        str_hidden_note = f"\nNOTE: This is a hidden seed race. Once the race admin has started the race with /startrace, "
        str_hidden_note += f"you will be able to request a DM with the seed by typing `/getseed`\n"
        str_hidden_note += f"The timer starts as soon as you receive the DM, so be quick when "
        str_hidden_note += f"downloading the seed!\n"
        str_hidden_note += f"To finish the race and record your time, type `/done` with no arguments."
    elif race.type == functions.constants.RACETYPE_SYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
    else:
        str_racer_cmds += f"    `/done x:xx:xx`         - Mark that you are done\n"

    embed = discord.Embed(
        title = f'Welcome to the race room for **{race.channel_name}**!',
        description = None,
        colour = discord.Colour.blue()
    )

    embed.add_field(name='Race room commands:', value=str_racer_cmds, inline=True)
    embed.add_field(name='Admin-only commands:', value=str_admin_cmds, inline=True)
    if race.isHidden == True:
        embed.add_field(name='Important note:', value=str_hidden_note, inline=False)
    if race.scheduled_close is not None:
        str_end_note = f"This race is scheduled to end on {discord.utils.format_dt(race.scheduled_close, style = 'F')} ({discord.utils.format_dt(race.scheduled_close,style='R')}).\n"
        str_end_note += f"Any racers who have not completed their seed at that time will automatically forfeit.\n"
        embed.add_field(name='Scheduled end:', value=str_end_note, inline=False)

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
    embed.add_field(name='Entrants:',value=entrants_msg,inline=False)

    #get the posting id from the race, else make a new one
    if race.entrants_msg_id:
        #TODO: fix it if the pinned post is gone, basically make a new one and update the race entrantsmsgid
        infopost = race.channel.get_partial_message(race.entrants_msg_id)
    else:
        infopost = await race.channel.send(content=None, embed=embed, view=classes.Buttons.RaceroomControlPanel(races))
        await infopost.pin()
        race.entrants_msg_id = infopost.id
        await db_update_race(races[race_channel])

    # This is my cludgy way of making it make a new infopost if the old post is gone (except triggers if try 404's)
    try:
        await infopost.edit(content=None, embed=embed, view=classes.Buttons.RaceroomControlPanel(races))
    except:
        infopost = await race.channel.send(content=None, embed=embed, view=classes.Buttons.RaceroomControlPanel(races))
        await infopost.pin()
        race.entrants_msg_id = infopost.id
        await db_update_race(races[race_channel])

