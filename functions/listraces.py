import os
import discord

from classes.Race import Race
from classes.RaceRunner import RaceRunner
from classes.Log import Log
# from functions.create_race_channels import create_race_channels
import functions.constants

def listraces(races: dict) -> list:
    """
    Read in the currently active races from the filesystem given by path

    Parameters
    ----------
    races : dict
        A dictionary containing racerooms

    Returns
    -------
    racelist
        A list of current race channel names
    """
    racelist = []
    for r in races.keys():
        racelist.append(r)
    return racelist
