import discord
import datetime
import json
import os
import shutil
import dateutil.parser

from functions.constants import TZ
from classes.Log import Log
from functions.lograce import create_race_file
from functions.generate_z_score import generate_z_score
import functions.constants

class Event:
    '''An object to hold events'''
    def __init__(self, in_interaction, initialize=True)->None:
        self._name = None
        self._guild = None
        self._type = None
        self._isInviteOnly = None
        self._creator = None
        self._description = None
        self._prefix = None
        self._thumburl = None
        self._admins = {}
        self._members = {}
        self._standard_flags = None
        self._standard_racetype = None
        self._standard_isHidden = None
        self._weekly_rollover = None
        self._startdate = None
        self._finishdate = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, input: str) -> None:
        if not isinstance(input, str):
            emessage = f"input must be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._name = input

    @property
    def guild(self) -> discord.guild.Guild:
        return self._guild

    @guild.setter
    def guild(self, input: discord.guild.Guild) -> None:
        if not isinstance(input, discord.guild.Guild):
            emessage = f"input must be a discord.guild.Guild. Found type {type(input)}"
            raise Exception(emessage)
        self._guild = input

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, input: str) -> None:
        if not isinstance(input, str):
            emessage = f"input must be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._type = input
        
    @property
    def isInviteOnly(self) -> bool:
        return self._isInviteOnly

    @isInviteOnly.setter
    def isInviteOnly(self, input: bool) -> None:
        if not isinstance(input, bool):
            emessage = f"input must be a bool. Found type {type(input)}"
            raise Exception(emessage)
        self.isInviteOnly = input
        
    @property
    def creator(self) -> discord.member.Member:
        return self._creator

    @creator.setter
    def creator(self, input:discord.member.Member) -> None:
        if not isinstance(input, discord.member.Member):
            emessage = f"input should be a discord.member.Member. Found type {type(input)}"
            raise Exception(emessage)
        self._creator = input
        
    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._description = input

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, input: str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._prefix = input

    @property
    def thumburl(self) -> str:
        return self._thumburl

    @thumburl.setter
    def thumburl(self, input: str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._thumburl = input