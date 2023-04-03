import os
import discord
from discord.utils import get
import aiohttp
import asqlite
import inflect

from functions.constants import DATA_PATH

async def getstreams(interaction, races, room):
    """
    User command to mark themselves as being ready

    Parameters
    ----------
    interaction : discord.Interaction
        The Interaction that generated the ready call

    races : dict
        A dictionary containing racerooms

    room : str
        A string containing the name of the race room to be joined

    Returns
    -------
    Nothing
    """

    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_SECRET")

    p = inflect.engine()

    if room == None:
        join_channel = interaction.channel
        room = join_channel.name
    else:
        join_channel = get(interaction.guild.channels, name=room)
    if not join_channel:
        emessage = f"No race called {room} found!"
        await interaction.response.send_message(emessage, ephemeral=True)
        return

    race = races[room]

    # set up the body to get a set of credentials
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        "grant_type": 'client_credentials'
    }

    # Get credentials
    async with aiohttp.ClientSession() as session:
        async with session.post('https://id.twitch.tv/oauth2/token', params=body) as r:
            if r.status == 200:
                keys = await r.json()

    # Set up headers for the get streams request
    headers = {
        'Client-ID': client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }

    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            res = await cursor.execute('''SELECT players.stream_url FROM players LEFT JOIN race_members 
            ON race_members.user_id = players.user_id WHERE players.stream_url IS NOT NULL 
            AND race_members.race_name = :room_name''', {"room_name": room})
            streamers = []
            data = await res.fetchall()
            for x in data:
                streamers.append(str(x[0]))

    # Get the live streams
    # streamers = ['iamgaahr', 'dbldown11', 'Taco_Magic', 'asilverthorn', 'pootskootie']
    query = 'https://api.twitch.tv/helix/streams?'
    for streamer_name in streamers:
        query += 'user_login=' + streamer_name + '&'
    query = query[:-1]

    stream_data = None
    async with aiohttp.ClientSession() as session:
        async with session.get(query, headers=headers) as r:
            if r.status == 200:
                stream_data = await r.json()

    stream_count = 0
    msg_body = ''
    if stream_data['data'] is not None and len(stream_data['data']) > 0:
        # Summarize who's live and generate a multistream link
        multi_url = '\n**Multistream link**: https://multistre.am'
        for stream in stream_data['data']:
            stream_count += 1
            async with asqlite.connect(path) as conn:
                async with conn.cursor() as cursor:
                    res = await cursor.execute('''SELECT user_id FROM players WHERE stream_url = :in_url''', {"in_url": stream["user_login"]})
                    streamers = []
                    data = await res.fetchall()
                    for x in data:
                        member_id = int(x[0])
                    stream_member = get(interaction.guild.members, id = member_id)

            msg_body += f'**{stream_member.name}**: https://www.twitch.tv/{stream["user_login"]}\n'
            multi_url += '/' + stream["user_login"]
    else:
        msg_body = "No racers in this room are currently live on Twitch."

    msg_header = f'The following {p.plural_noun("racer", stream_count)} in **{room}** {p.plural_verb("is", stream_count)} currently live on Twitch:\n'

    if stream_count > 1:
        msg_body += f'{multi_url}'
    stream_msg = msg_header + msg_body

    await interaction.response.send_message(stream_msg, ephemeral=True,suppress_embeds=True)

    # Revoke the token
    body = {
        'client_id': client_id,
        'token': keys['access_token']
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://id.twitch.tv/oauth2/revoke', params=body) as r:
            if r.status == 200:
                None

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# asyncio.run(get_streams())
