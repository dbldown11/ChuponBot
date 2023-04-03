import ast
import copy
import os
import discord
from datetime import datetime
from discord.utils import get
import json
import ast
import regex as re
import asqlite
import sqlite3
from dateutil.parser import parse

from classes.Race import Race
from classes.RaceRunner import RaceRunner
from classes.Log import Log
# from functions.create_race_channels import create_race_channels
import functions.constants
from functions.constants import DATA_PATH


def loadraces(path: str, client: discord.client.Client) -> dict:
    """
    Read in the currently active races from the filesystem given by path

    Parameters
    ----------
    path : str
        The root directory of where we store the race information

    client : discord.client.Client
        The bot client

    Returns
    -------
    dict
        A dictionary of the races. Each key is a server id with a value of another dictionary whose keys are raceroom names
        Those values are the races themselves
    """
    if not isinstance(path, str):
        emessage = f"input path must be a str. Found type {type(path)}"
        raise Exception(emessage)

    if not isinstance(client, discord.client.Client):
        emessage = f"client must be a discord.client.Client. Found type {type(path)}"
        raise Exception(emessage)
    '''
    path = path + os.sep + "open"
    servers = []
    directories = [w[0] for w in os.walk(path)]
    if path in directories:
        directories.remove(path)
    for directory in directories:
        directory = directory.strip()
        guild = directory.split(os.sep)[-1]
        if client.get_guild(int(guild)):
            open_server = path + os.sep + guild + os.sep
            servers.append(open_server)

    # We now know which servers have open races. Get a list of races
    race_files = []
    for server_dir in servers:
        for root, dirs, files in os.walk(server_dir):
            for file in files:
                race_files.append(server_dir + file)

    # Cycle through the json files and read them in
    races = {}
    for race_json_file in race_files:
        with open(race_json_file, 'r') as f:
            j = f.read()
            r = json_to_race(client, j)
            r.loaded_race = True
            r.path_open = race_json_file
            races[r.channel_name] = r
    # return races
    '''

    # Run through the race DB and compile all races not closed
    races = {}
    path = os.path.join(DATA_PATH, 'testdata.db')
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    curs = conn.cursor()
    curs.execute("""SELECT * FROM races WHERE date_closed IS NULL""")
    rows = curs.fetchall()
    curs.close()
    for row in rows:
        r = Race(None, None, False)
        r.guild = client.get_guild(row['guild'])

        channel = discord.utils.get(client.get_all_channels(), name=row["race_name"])
        if not channel:
            r.channel_name = row["race_name"]
        else:
            r.channel = channel
            r.channel_name = channel.name

        r.creator = r.guild.get_member(row["creator_id"])

        if row["type"] is not None:
            if row["type"] in functions.constants.RACETYPES:
                r.type = row["type"]
            else:
                emessage = f'Invalid race type found: {row["type"]}'
                raise Exception(emessage)

        cur = conn.cursor()
        cur.execute("""SELECT user_id FROM race_admins WHERE race_name = ?""", (row["race_name"],))
        r.admins = [r[0] for r in cur]
        cur.close()

        if row["date_opened"]:
            r.opened_date = parse(row["date_opened"])

        if row["date_started"]:
            r.race_start_date = parse(row["date_started"])

        if row["scheduled_close"]:
            r.scheduled_close = parse(row["scheduled_close"])

        if row["entrants_msg_id"]:
            r.entrants_msg_id = int(row["entrants_msg_id"])

        if row["entrants_spoiler_msg_id"]:
            r.entrants_spoiler_msg_id = int(row["entrants_spoiler_msg_id"])

        if row["filename"]:
            r.filename = row["filename"]

        if row["description"]:
            r.description = row["description"]
        else:
            r.description = 'No details available - join the race room or contact the race creator to learn more!'

        # TODO: make another search to get all race runners
        # Need to write out racerunners as a dict
        path = os.path.join(DATA_PATH, 'testdata.db')
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        curs = conn.cursor()
        curs.execute("""SELECT * FROM race_members WHERE race_name=?""",(r.channel_name,))
        racer_rows = curs.fetchall()
        curs.close()
        for racer_row in racer_rows:
            rr = RaceRunner()
            rr.guild = client.get_guild(racer_row["guild"])
            if channel:
                rr.channel = channel
            rr.member = rr.guild.get_member(racer_row["user_id"])

            rr.join_date = parse(racer_row["join_date"])

            if racer_row["start_date"]:
                rr.start_date = parse(racer_row["start_date"])
                print(type(rr.start_date))

            if racer_row["finish_date"]:
                rr.finish_date = parse(racer_row["finish_date"])

            if racer_row["isforfeit"] == 1:
                rr.forfeit = True

            if racer_row["isready"] == 1:
                rr.ready = True

            rr.hasSeed = False
            if racer_row["hasseed"] == 1:
                rr.hasSeed = True

            rr.start_rating_thistype = racer_row["start_rating_thistype"]
            rr.start_rating_all = racer_row["start_rating_all"]

            r.addRacer(rr)

        if row["preset"]:
            r.preset = row["preset"]

        if row["url"]:
            r.url = row["url"]

        if row["flags"]:
            r.flags = row["flags"]

        if row["hash"]:
            r.hash = row["hash"]

        if row["version"]:
            r.version = row["version"]

        if row["comments"]:
            r.comments = row["comments"]

        r.isHidden = False
        if row["ishidden"] == 1:
            r.isHidden = True

        races[r.channel_name] = r
    '''
    async with asqlite.connect(path) as db:
        db.row_factory = asqlite.Row
        async with db.execute("""SELECT * FROM races WHERE date_closed IS NOT NULL""") as cursor:
            async for row in cursor:
                races[row['race_name']] = row['race_name']
    '''
    return races


def json_to_race(client, input: str) -> Race:
    """
    Converts Race JSON into a Race object. Only used within loadraces

    Parameters
    ----------
    client : discord.client.Client
        The bot client

    input : str
        Race JSON

    Returns
    -------
    Race
    """
    if not isinstance(input, str):
        emessage = f"input should be str, found type {type(input)}"
        raise Exception(emessage)

    try:
        js = json.loads(input, strict=False)
    except Exception as e:
        emessage = f"Unable to load input json:\n{input}\n\n{str(e)}"
        raise Exception(emessage)

    r = Race(None, None, False)
    r.guild = client.get_guild(int(js["guild"]))

    channel = discord.utils.get(client.get_all_channels(), name=js["channel"])
    if not channel:
        r.channel_name = js["channel"]
    else:
        r.channel = channel
    r.creator = r.guild.get_member(int(js["creator"]))

    if js["type"] is not None:
        if js["type"] in functions.constants.RACETYPES:
            r.type = js["type"]
        else:
            emessage = f'Invalid race type found: {js["type"]}'
            raise Exception(emessage)
    r.admins = js["admins"]

    if js["date_opened"]:
        r.opened_date = parse(js["date_opened"])

    if js["date_started"]:
        r.race_start_date = parse(js["date_started"])

    if js["scheduled_close"]:
        r.scheduled_close = parse(js["scheduled_close"])

    if js["entrants_msg_id"]:
        r.entrants_msg_id = int(js["entrants_msg_id"])

    if js["entrants_spoiler_msg_id"]:
        r.entrants_spoiler_msg_id = int(js["entrants_spoiler_msg_id"])

    if js["filename"]:
        r.fileid = js["filename"]

    if js["description"]:
        r.description = js["description"]
    else:
        r.description = 'No details available - join the race room or contact the race creator to learn more!'

    # Need to write out racerunners as a dict
    for member in js["members"]:
        member_js = str(member)
        # member_js = member_js.replace("'", '"')
        # the above line failed on strings with apostrophes, replaced by this ugly regex thing that does same thing from stackoverflow
        # https://stackoverflow.com/questions/55600788/replace-single-quotes-with-double-quotes-but-leave-ones-within-double-quotes-unt/63862387#63862387
        rx = re.compile(r'"[^"]*"(*SKIP)(*FAIL)|\'')
        member_js = rx.sub('"', member_js)
        rr = json_to_racer(client, member_js)
        rr.race = r
        r.addRacer(rr)

    if js["preset"]:
        r.preset = js["preset"]

    if js["url"]:
        r.url = js["url"]

    if js["flags"]:
        r.flags = js["flags"]

    if js["hash"]:
        r.hash = js["hash"]

    if js["version"]:
        r.version = js["version"]

    if js["comments"]:
        r.comments = js["comments"]

    r.isHidden = False
    if js["hidden"] == "True":
        r.isHidden = True

    return r


def json_to_racer(client, input: dict) -> RaceRunner:
    """
    Converts RaceRunner JSON into a RaceRunner object. Only used within json_to_race

    Parameters
    ----------
    client : discord.client.Client
        The bot client

    input : str
        RaceRunner JSON

    Returns
    -------
    RaceRunner
    """

    # if not isinstance(input, str):
    # emessage = f"input should be str, found type {type(input)}"
    # raise Exception(emessage)

    # The JSON loader in json_to_race tries to be helpful by turning our "null" into "None",
    # which breaks json_to_racer, so we do this
    input = input.replace("None", "null")
    input = input.replace("\"null\"", "null")

    try:
        js = json.loads(input, strict=False)
    except Exception as e:
        emessage = f"Unable to load input json:\n{input}\n\n{str(e)}"
        raise Exception(emessage)

    rr = RaceRunner()
    rr.guild = client.get_guild(int(js["guild_id"]))
    channel = discord.utils.get(client.get_all_channels(), name=js["race"])
    if channel:
        rr.channel = channel
    rr.member = rr.guild.get_member(int(js["id"]))

    rr.join_date = parse(js["join"])
    if js["start"]:
        rr.start_date = parse(js["start"])
    if js["finish"]:
        rr.finish_date = parse(js["finish"])
    if js["forfeit"] == "True":
        rr.forfeit = True
    if js["ready"] == "True":
        rr.ready = True

    rr.hasSeed = False
    if js["hasSeed"] == "True":
        rr.hasSeed = True
    return rr
