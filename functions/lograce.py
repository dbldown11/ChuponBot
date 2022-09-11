import os
import shutil
import traceback
import sys

from classes.Log import Log
from functions.constants import RACE_PATH


def create_race_file(path: str, race) -> str:
    from classes.Race import Race
    """
    Creates a race file for a given Race in a given path
    Parameters
    ----------
    path : str
        The root directory in which to create the race file. Usually the constant RACE_PATH.
    race : Race
        An FF6WC Raceroom bot Race object
    Returns
    -------
    str
        The path to the JSON file containing the race information
    """
    if not isinstance(path, str):
        emessage = f"input path must be a str. Found type {type(path)}"
        raise Exception(emessage)

    if not isinstance(race, Race):
        emessage = f"input must be an FF6WC-raceroombot-Race. Found type {type(race)}"
        raise Exception(emessage)

    if not race.guild or not race.guild.id:
        emessage = f"Race does not have proper guild information.\n {race}\n"
        raise Exception(emessage)

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception as e:
            emessage = f"Unable to create directory {path}"
            raise Exception(emessage)

    open_path = path + os.sep + "open"
    if not os.path.exists(open_path):
        try:
            os.makedirs(open_path)
        except Exception as e:
            emessage = f"Unable to create directory {open_path}"
            raise Exception(emessage)

    closed_path = path + os.sep + "closed"
    if not os.path.exists(closed_path):
        try:
            os.makedirs(closed_path)
        except Exception as e:
            emessage = f"Unable to create directory {closed_path}"
            raise Exception(emessage)

    if not path.endswith(os.sep):
        path += os.sep

    guild_path = path + os.sep + "open" + os.sep + str(race.guild.id)
    guild_path = os.path.abspath(guild_path)

    if not os.path.exists(guild_path):
        try:
            os.makedirs(guild_path)
        except Exception as e:
            emessage = f"Unable to create directory {guild_path}"
            raise Exception(emessage)

    closed_guild_path = path + os.sep + "closed" + os.sep + str(race.guild.id)
    closed_guild_path = os.path.abspath(closed_guild_path)

    if not os.path.exists(closed_guild_path):
        try:
            os.makedirs(closed_guild_path)
        except Exception as e:
            emessage = f"Unable to create directory {closed_guild_path}"
            raise Exception(emessage)

    filename = race.channel_name + "-" + race.opened_date.strftime("%Y-%m-%d") + ".json"
    filepath = guild_path + os.sep + filename
    if os.path.exists(filepath):
        counter = 0
        bkp_path = filepath + f".bkp_{str(counter).zfill(4)}"
        while os.path.exists(bkp_path):
            if counter > 9999:
                emessage = f"Tried to create 10,000 races with the same name and date in {guild_path}"
                raise Exception(emessage)
            counter += 1
            bkp_path = filepath + f".bkp_{str(counter).zfill(4)}"
        shutil.copyfile(filepath, bkp_path)

    # We should now have clean access to write to the output file
    with open(filepath, 'w') as f:
        js = race.toJSON()
        f.write(js)
    return filepath