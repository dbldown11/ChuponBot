import asqlite
import sqlite3
import os
import datetime
import asyncio
from classes.Race import Race
from classes.RaceRunner import RaceRunner
from functions.constants import DATA_PATH, TZ


# define connection and cursor
async def db_init():
    path = os.path.join(DATA_PATH, 'testdata.db')
    if not os.path.exists(DATA_PATH):
        try:
            os.makedirs(DATA_PATH)
            print(f"Created db directories: {DATA_PATH}. This should only happen on ChuponBot's first run!")
        except Exception as e:
            emessage = f"Unable to create directory {DATA_PATH}"
            raise Exception(emessage)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            ### this builds the db if it doesn't exist
            # create races table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS races
                (index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_name TEXT UNIQUE, 
                guild INTEGER, 
                race_listing_msg_id INTEGER,
                entrants_msg_id INTEGER, 
                entrants_spoiler_msg_id INTEGER,
                creator_id INTEGER, 
                description TEXT, 
                stream_url TEXT, 
                filename TEXT, 
                preset TEXT, 
                url TEXT, 
                ishidden INTEGER, 
                hash TEXT, 
                version TEXT, 
                flags TEXT, 
                type TEXT, 
                date_opened TEXT, 
                date_started TEXT, 
                date_closed TEXT, 
                scheduled_close TEXT, 
                comments TEXT, 
                event_name TEXT,
                gp_pool INTEGER,
                restrict_role_id INTEGER
                );""")

            # create race_admins table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS race_admins
                (index_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                race_name TEXT,
                FOREIGN KEY(race_name) REFERENCES races(race_name)
                );""")

            # create race_members table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS
                race_members(index_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER,    
                race_name TEXT,    
                join_date TEXT, 
                start_date TEXT, 
                finish_date TEXT, 
                isready INTEGER, 
                isforfeit INTEGER, 
                time_taken TEXT, 
                guild INTEGER, 
                hasseed INTEGER, 
                start_rating_thistype REAL,
                start_rating_all REAL,
                finish_rating_thistype REAL,
                finish_rating_all REAL,
                finish_pos INTEGER,
                event_points INTEGER,
                gp_earned INTEGER,
                FOREIGN KEY(user_id) REFERENCES players(user_id), 
                FOREIGN KEY(race_name) REFERENCES races(race_name)
                ); """)

            # create players table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS
                players(index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                pronouns TEXT,
                created_date TEXT, 
                stream_url TEXT, 
                gp INTEGER, 
                rating_all REAL,
                rating_sync REAL,
                rating_async REAL
                );""")

            # create events table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS
                events(index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT UNIQUE,
                guild INTEGER,
                eventtype TEXT,
                isinviteonly INTEGER,
                start_date TEXT, 
                finish_date TEXT,
                description TEXT,
                prefix TEXT,
                creator_id INTEGER,
                standard_flagset TEXT,
                standard_type TEXT,
                standard_isHidden INTEGER,
                weekly_rollover TEXT,
                thumbnail_filename TEXT
                );""")

            # create event_admins table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS event_admins
                (index_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                user_id INTEGER, 
                event_name TEXT,
                FOREIGN KEY(event_name) REFERENCES events(event_name)
                );""")

            # create event_members table
            await cursor.execute("""CREATE TABLE IF NOT EXISTS event_members
                (index_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_index_id INTEGER,
                user_id INTEGER,
                total_races INTEGER,
                wins INTEGER,
                points INTEGER,
                join_date TEXT,
                FOREIGN KEY(event_index_id) REFERENCES events(index_id)
                );""")

            await conn.commit()


async def db_update_race(race) -> None:
    """
    Updates an existing race record in the db with the contents of a race object

    Parameters
    ----------
    race:
        A FF6WC race object

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'testdata.db')
    data = (race.guild.id, race.entrants_msg_id, race.entrants_spoiler_msg_id, race.creator.id,
            race.description, race.stream_url, race.filename, race.preset, race.url, race.isHidden, race.hash,
            race.version, race.flags, race.type, race.opened_date, race.race_start_date, race.closed_date,
            race.scheduled_close, race.comments, race.event_name, race.restrict_role_id, race.channel.name)
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("""UPDATE races
                SET guild=?, entrants_msg_id=?, entrants_spoiler_msg_id=?, creator_id=?, description=?, 
                stream_url=?, filename=?, preset=?, url=?, ishidden=?, hash=?, version=?, flags=?, type=?, 
                date_opened=?, date_started=?, date_closed=?, scheduled_close=?, comments=?, event_name=?, 
                restrict_role_id=? WHERE race_name=?
                """, data)
            await conn.commit()


async def db_update_racerunner(race, user_id) -> None:
    """
    Updates a racer's record for a specific race in the db

    Parameters
    ----------
    race :
        A FF6WC race object

    user_id : int
        An id for the discord.User/discord.Member in the race

    Returns
    -------
    Nothing
    """
    for key in race.members:
        if race.members[key].member.id == user_id:
            rr = race.members[key]

    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM race_members WHERE user_id = ? AND race_name = ?",
                                 (user_id, race.channel_name))
            count = await cursor.fetchall()
            if len(count) == 0:
                emessage = "Tried to update a race record for someone who has not joined the race."
                raise Exception(emessage)
            else:
                data = (rr.join_date, rr.start_date, rr.finish_date, rr.ready, rr.forfeit, str(rr.time_taken),
                        rr.hasSeed, rr.start_rating_thistype, rr.start_rating_all, rr.finish_rating_thistype,
                        rr.finish_rating_all, rr.finish_pos, rr.event_points, rr.gp_earned, race.channel_name,
                        rr.member.id)
                async with asqlite.connect(path) as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute("""UPDATE race_members
                            SET join_date = ?, start_date = ?, finish_date = ?, isready = ?, isforfeit = ?,
                            time_taken = ?, hasseed = ?, start_rating_thistype = ?, start_rating_all = ?,
                            finish_rating_thistype = ?, finish_rating_all = ?,
                            finish_pos = ?, event_points = ?, gp_earned = ?
                            WHERE race_name = ? AND user_id = ?
                            """, data)
                        await conn.commit()


async def db_player_check_init(member) -> None:
    """
    Checks if we have a profile in the player db for this player, and if not, initialize one

    Parameters
    ----------
    user: discord.Member
        The user being checked (and possibly added)

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM players WHERE user_id = ?", (member.id,))
            count = await cursor.fetchall()
            if len(count) == 0:
                data = (member.id, None, datetime.datetime.now(TZ), None, 0, 1000, 1000, 1000)
                await cursor.execute("""INSERT INTO players (user_id, pronouns, created_date, stream_url, gp,
                rating_all, rating_sync, rating_async) VALUES (?, ?, ?, ?, ?, ?, ?, ?);""", data)
                await conn.commit()

async def db_player_update_stream(member, streamname) -> None:
    """
    Checks if we have a profile in the player db for this player, and if not, initialize one

    Parameters
    ----------
    member: discord.Member
        The user being checked (and possibly added)

    streamname: str
        The user's Twitch username

    Returns
    -------
    Nothing
    """
    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            data = (streamname, member.id)
            await cursor.execute("UPDATE players SET stream_url = ? WHERE user_id = ?",data)
            await conn.commit()

async def db_player_update_pronouns(member, pronouns) -> None:
    """
    Updates a player's pronouns

    Parameters
    ----------
    member: discord.Member
        The user being checked (and possibly added)

    pronouns: str
        The user's preferred pronouns

    Returns
    -------
    Nothing
    """
    if pronouns == "Other":
        new_pronouns = None
    else:
        new_pronouns = pronouns
    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            data = (new_pronouns, member.id)
            await cursor.execute("UPDATE players SET pronouns = ? WHERE user_id = ?",data)
            await conn.commit()

async def db_player_retrieve(member) -> dict:
    """
    Creates a dict using the current db info for a racer

    Parameters
    ----------
    member: discord.Member
        The user being checked (and possibly added)

    Returns
    -------
    A dict of the racer's info
    """
    path = os.path.join(DATA_PATH, 'testdata.db')
    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            res = await cursor.execute("SELECT * FROM players WHERE user_id = :member_id", {"member_id": member.id})
            row = await res.fetchone()
    output = {k: row[k] for k in row.keys()}

    async with asqlite.connect(path) as conn:
        async with conn.cursor() as cursor:
            res = await cursor.execute('''SELECT race_members.user_id, race_members.race_name, race_members.finish_pos, 
            races.type FROM race_members LEFT JOIN races ON race_members.race_name = races.race_name 
            WHERE finish_date > 0 AND user_id = :member_id''', {"member_id": member.id})
            rows = await res.fetchall()
            all_races = [{k: item[k] for k in item.keys()} for item in rows]

    #build stats
    output['total_races_all'] = 0
    output['total_wins_all'] = 0
    output['total_races_sync'] = 0
    output['total_wins_sync'] = 0
    output['total_races_async'] = 0
    output['total_wins_async'] = 0

    for x in all_races:
        output['total_races_all'] += 1
        if x['type'] == 'sync':
            output['total_races_sync'] += 1
            if x['finish_pos'] == 1:
                output['total_wins_sync'] += 1
                output['total_wins_all'] += 1
        if x['type'] == 'async':
            output['total_races_async'] += 1
            if x['finish_pos'] == 1:
                output['total_wins_all'] += 1
                output['total_wins_async'] += 1
    

    return output

