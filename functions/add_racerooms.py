import discord
from discord.utils import get
import datetime
import random
import string
import os

def add_racerooms(user, room_id, room_type, spoiler_room, ts):
    filename = "./db/races.txt"

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "a") as f:
        writemsg = str([user, room_id, room_type, spoiler_room, ts])+"\n"
        f.write(writemsg)
        f.close()
    return