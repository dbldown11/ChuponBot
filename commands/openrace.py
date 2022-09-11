import datetime
import discord
import random
import string

from better_profanity import profanity
from discord.utils import get
from functions.add_racerooms import add_racerooms
from functions.string_functions import parse_roomname
from classes.Race import Race

import functions.constants



async def openrace(interaction, args) -> dict:
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
    cat = get(guild.categories, name="Racing")

    # This stores the name of the channel, which can be different based on any arguments given by the user
    # args is a dictionary of options mapping to values
    if args['name'] is not None:
        try:
            #name = ('-').join(args['name'])
            name = args['name']
            c_name = parse_roomname(name)
        except Exception as e:
            emessage = str(e)
            await channel.send(emessage)
            return
    else:
        room_failures = set()
        c_name = parse_roomname()

        # If we some how get a name collision, keep generating until we don't
        while get(guild.channels, name=c_name) or profanity.contains_profanity(c_name):
            room_failures.add(c_name)
            c_name = parse_roomname()

            # Strago help us if this ever fires off
            if len(room_failures) > 36^6:
                emessage = "You have somehow exhausted all 2,176,782,336 possible random room names. You are a monster."
                await channel.send(emessage)
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
        c_name += '-hidden'
        isHidden = True

    if profanity.contains_profanity(c_name):
        emessage = "You have attempted to create a channel with a forbidden name."
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


    # This stores the new channel for the bot to message in after creation
    # new_channel = get(guild.channels, name=c_name)

    # This sends a message in the new channel after a 2-second delay
    # I'd rather change this to a loop to check if the channel exists - I'm just using the timer now to keep from
    # the message firing before the channel is created
    r_create_msg = f"Welcome to your race room, {interaction.user.name}!\n"
    r_create_msg += f"You can use the following commands:`\n"
    r_create_msg += f"    /raceinfo             - See information about this race\n"
    r_create_msg += f"    /entrants             - Shows the entrants for this race\n"
    r_create_msg += f"    /ready                - Mark yourself ready\n"
    r_create_msg += f"    /unready              - Mark yourself unready\n"
    r_create_msg += f"    /ff or /forfeit       - Forfeit\n"
    r_create_msg += f"    /quit                 - Quit the race\n"
    r_create_msg += f"    /getseed              - DMs you a link to download the seed for this race\n"
    r_create_msg += f"    /setseed flagstring   - If you're a race admin, use this to set the flags for the race seed\n"
    r_create_msg += f"    /setseed url          - If you're a race admin, use this to set the URL for the race seed\n"
    r_create_msg += f"    /startrace            - Start the race\n"
    r_create_msg += f"    /done                 - Mark that you are done\n"
    r_create_msg += f"    /finishrace            - Close this raceroom after a brief delay\n"
    r_create_msg += f"`\n"
    if isHidden and room_type == functions.constants.RACETYPE_SYNC:
        r_create_msg += f"\nNOTE: This is a hidden seed race. You will be DMed a link to download the seed when "
        r_create_msg += f"the race starts. The timer starts as soon as you receive the DM, so be quick when "
        r_create_msg += f"downloading the seed!\n"

    elif isHidden and room_type == functions.constants.RACETYPE_ASYNC:
        r_create_msg += f"\nNOTE: This is a hidden seed race. Once the race admin has started the race with !startrace, "
        r_create_msg += f"you will be able to request a DM with the seed by typing `!getseed`\n"
        r_create_msg += f"The timer starts as soon as you receive the DM, so be quick when "
        r_create_msg += f"downloading the seed!\n"

    infopost = await race_channel.send(r_create_msg)
    await infopost.pin()

    # This sends the confirmation and join message to the requestor's channel
    create_msg = f"Your race room has been created. To join, type: `/join {c_name}`"
    await interaction.response.send_message(create_msg, ephemeral=True)

    race = Race(interaction, race_channel)
    race.type = room_type
    race.isHidden = isHidden
    race.admins.add(interaction.user.id)
    return race