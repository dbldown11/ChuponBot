import datetime
import discord
import random
import string
import os
import asqlite

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from classes.Race import Race
from classes.Modals import FlagstringModal
from functions.botconfig import config, env

import functions.constants
from functions.constants import DATA_PATH



async def openrace(interaction, races, args) -> dict:
    """
    Opens a race in a given guild (server) with the name stored in args or generates a name if one isn't provided

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the openrace call
    args : dict
        A dictionary containing the command we've been given
        ex: {'openrace': {'name': ('TestRoom1',)}}
    Returns
    -------
    dict
        A dictionary with the key being the room name and the value being "Sync" or "Async" or None on failure
        ex: {'ff6wc-abcdef-sync': 'Sync'}
    """
    emessage = ""
    if not isinstance(args, dict):
        emessage += f"args is not a Python dict - Found type {type(args)}\n"
    if emessage != "":
        raise Exception(emessage)

    # The channel and guild the command was called in
    guild = interaction.guild
    channel = interaction.channel

    # This next part just pulls the category name for channel creation.
    cat = get(guild.categories, name=config.get(env,"race_category_general"))

    #TODO: If isEvent, then check if user is an event admin and that event is active

    #TODO: Placeholder to find events for the room prefix
    prefix = 'open'

    # This stores the name of the channel, which can be different based on any arguments given by the user
    # args is a dictionary of options mapping to values
    if args['name'] is not None:
        try:
            #name = ('-').join(args['name'])
            name = args['name']
            c_name = parse_roomname(name,prefix)
        except Exception as e:
            emessage = str(e)
            await channel.send(emessage)
            return
    else:
        room_failures = set()
        c_name = parse_roomname(None, prefix)

        # If we some how get a name collision, keep generating until we don't
        while get(guild.channels, name=c_name) or profanity.contains_profanity(c_name):
            room_failures.add(c_name)
            c_name = parse_roomname(None, prefix)

            # Strago help us if this ever fires off
            if len(room_failures) > 36^6:
                emessage = "You have somehow exhausted all 2,176,782,336 possible random room names. You are a monster."
                await channel.send(emessage)
                return None

    if 'sync' in c_name:
        emessage = "Race names cannot include the word 'sync' or 'async'. Please create with a different name."
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    # Add sync or async to our room names
    isHidden = False
    if args['racetype'] == 'async':
        c_name += '-async'
        room_type = functions.constants.RACETYPE_ASYNC
    else:
        c_name += '-sync'
        room_type = functions.constants.RACETYPE_SYNC

    #add hidden to our room name
    if args['hidden'] == 'yes':
        #c_name += '-hidden'
        isHidden = True

    if args['duration'] is not None:
        scheduled_enddate = datetime.datetime.now() + datetime.timedelta(days=args['duration'])

    if profanity.contains_profanity(c_name):
        emessage = "You have attempted to create a channel with a forbidden name."
        await interaction.response.send_message(emessage, ephemeral=True)
        return None

    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT race_name FROM races WHERE race_name = :cname', {"cname": c_name})
            row = await cursor.fetchone()
            if row is not None:
                emessage = "A race with that name has already been created. Please use a different name."
                await interaction.response.send_message(emessage, ephemeral=True)
                return None

    # This makes the channel private
    race_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        interaction.user: discord.PermissionOverwrite(read_messages=True)
    }

    spoiler_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    # This creates the channel, pulling in the channel name (c_name), category (cat) and overwrites (overwrites)
    race_channel = await guild.create_text_channel(c_name, category=cat, overwrites=race_room_overwrites)
    spoiler_channel = await guild.create_text_channel(c_name + "-spoilers", category=cat,
                                                        overwrites=spoiler_room_overwrites)

    add_racerooms(str(interaction.user.id), str(race_channel.id), room_type, str(spoiler_channel.id),
                    str(str(datetime.datetime.utcnow())) + " UTC")

    '''
    # This stores the new channel for the bot to message in after creation
    # new_channel = get(guild.channels, name=c_name)

    # This sends a message in the new channel after a 2-second delay
    # I'd rather change this to a loop to check if the channel exists - I'm just using the timer now to keep from
    # the message firing before the channel is created
    # r_create_msg = f"Welcome to your race room, {interaction.user.name}!\n"
    # r_create_msg += f"You can use the following commands:`\n"
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
    if isHidden and room_type == functions.constants.RACETYPE_SYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
        str_hidden_note = f"\nNOTE: This is a hidden seed race. You will be DMed a link to download the seed when "
        str_hidden_note += f"the race starts. The timer starts as soon as you receive the DM, so be quick when "
        str_hidden_note += f"downloading the seed!\n"

    elif isHidden and room_type == functions.constants.RACETYPE_ASYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
        str_hidden_note = f"\nNOTE: This is a hidden seed race. Once the race admin has started the race with /startrace, "
        str_hidden_note += f"you will be able to request a DM with the seed by typing `/getseed`\n"
        str_hidden_note += f"The timer starts as soon as you receive the DM, so be quick when "
        str_hidden_note += f"downloading the seed!\n"
    elif room_type == functions.constants.RACETYPE_SYNC:
        str_racer_cmds += f"    `/done`                 - Mark that you are done\n"
    else:
        str_racer_cmds += f"    `/done x:xx:xx`         - Mark that you are done\n"

    embed = discord.Embed(
        title = f'Welcome to the race room for **{race_channel.name}**!',
        description = None,
        colour = discord.Colour.blue()
    )

    embed.add_field(name='Race room commands:', value=str_racer_cmds, inline=True)
    embed.add_field(name='Admin-only commands:', value=str_admin_cmds, inline=True)
    if isHidden:
        embed.add_field(name='Important note:', value=str_hidden_note, inline=False)
    if args['duration'] is not None:
        str_end_note = f"This race is scheduled to end on {discord.utils.format_dt(scheduled_enddate, style = 'F')} ({discord.utils.format_dt(scheduled_enddate,style='R')}).\n"
        str_end_note += f"Any racers who have not completed their seed at that time will automatically forfeit.\n"
        embed.add_field(name='Scheduled end:', value=str_end_note, inline=False)

    #infopost = await race_channel.send(r_create_msg,view=RaceroomControlPanel())
    infopost = await race_channel.send(content=None, embed=embed, view=RaceroomControlPanel())
    await infopost.pin()
    '''

    # Creates a placeholder listing in #active-races
    listing_channel = get(guild.channels, name="active-races")
    listing = await listing_channel.send(f"Pending listing for {race_channel.name}")

    race = Race(interaction, race_channel, listing)
    # race.entrants_msg_id = infopost.id

    if args['description'] is not None:
        race.description = args['description']
    else:
        race.description = 'No details available - join the race room or contact the race creator to learn more!'

    race.type = room_type
    race.isHidden = isHidden
    if args['duration'] is not None:
        race.scheduled_close = scheduled_enddate
    race.admins.add(interaction.user.id)

    ### Add restriction info to the race ### DT, 4/6/23
    # Assuming args['restrict'] is a single role name:
    if args['restrict'] is not None:
        race.restrict_role_id = discord.utils.get(interaction.guild.roles, name=args['restrict'])
    ###

    # Write the race to the db - set the path and assemble the original data
    path = os.path.join(functions.constants.DATA_PATH, 'testdata.db')
    data = (race.channel.name, race.guild.id, race.entrants_msg_id, race.entrants_spoiler_msg_id, race.creator.id,
            race.description, race.isHidden, race.type, race.opened_date, race.event_name, race.restrict_role_id)

    # build a list of tuples containing the admins for this race
    admins_data = []
    for admin in race.admins:
        new_admin = (admin, race.channel.name)
        admins_data.append(new_admin)
    print(admins_data)

    # insert the new race into the DB
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""INSERT INTO races (race_name, guild, entrants_msg_id, entrants_spoiler_msg_id,
                creator_id, description, ishidden, type, date_opened, event_name, restrict_role_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
            await cursor.executemany("""INSERT INTO race_admins(user_id, race_name) VALUES(?,?);""",admins_data)
            await conn.commit()

    return race