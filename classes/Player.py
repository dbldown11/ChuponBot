import discord
import datetime


class Player:
    '''An object to hold players'''

    def __init__(self, initialize=True) -> None:
        self._user = None
        self._guild = None
        self._created_date = None
        self._stream_url = None
        self._gp = None
        self._badges = {}
        self._races_completed = {}  # completed races include final time, final place, total competitors, displayname
        self._total_all = None
        self._total_sync = None
        self._win_all = None
        self._win_sync = None
        self._rating_all = None
        self._rating_sync = None
        self._rating_async = None

    @property
    def user(self) -> discord.User:
        return self._user

    @user.setter
    def user(self, input: discord.User):
        if not isinstance(input, discord.User):
            emessage = f"user_id input should be an discord.User. Found type {type(input)}"
            raise Exception(emessage)
        self._user = input

    @property
    def guild(self) -> discord.guild.Guild:
        return self._guild

    @guild.setter
    def guild(self, input: discord.guild.Guild) -> None:
        if not isinstance(input, discord.guild.Guild):
            emessage = f"guild input must be a discord.guild.Guild. Found type {type(input)}"
            raise Exception(emessage)
        self._guild = input

    @property
    def created_date(self) -> datetime.datetime:
        return self._created_date

    @created_date.setter
    def created_date(self, input: datetime.datetime) -> None:
        if not isinstance(input, datetime.datetime):
            emessage = f"created_date input should be datetime.datetime. Found type {type(input)}"
            raise Exception(emessage)
        self._created_date = input

    @property
    def stream_url(self) -> str:
        return self._stream_url

    @stream_url.setter
    def stream_url(self, input: str) -> None:
        if not isinstance(input, str):
            emessage = f"stream URL input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._stream_url = input

    @property
    def gp(self) -> int:
        return self._gp

    @gp.setter
    def gp(self, input: int):
        if not isinstance(input, int):
            emessage = f"gp input should be an int. Found type {type(input)}"
            raise Exception(emessage)
        # Ensures racer's GP total never goes below 0
        self._gp = max(input, 0)

    @property
    def badges(self) -> dict:
        return self._badges

    @badges.setter
    def badges(self, input) -> None:
        # Need something here - these should only be added by a class method TBD
        self._badges = input

    @property
    def races_completed(self) -> dict:
        return self._races_completed

    @races_completed.setter
    def races_completed(self, input) -> None:
        # Need something here - these should only be added by a class method TBD
        self._races_completed = input

    @property
    def total_all(self) -> int:
        return self._total_all

    @total_all.setter
    def total_all(self, input: int):
        if not isinstance(input, int):
            emessage = f"total_all input should be an int. Found type {type(input)}"
            raise Exception(emessage)
        self._total_all = input

    @property
    def total_sync(self) -> int:
        return self._total_all

    @total_sync.setter
    def total_sync(self, input: int):
        if not isinstance(input, int):
            emessage = f"total_sync input should be an int. Found type {type(input)}"
            raise Exception(emessage)
        self._total_sync = input

    @property
    def win_all(self) -> int:
        return self._win_all

    @win_all.setter
    def win_all(self, input: int):
        if not isinstance(input, int):
            emessage = f"win_all input should be an int. Found type {type(input)}"
            raise Exception(emessage)
        self._win_all = input

    @property
    def win_sync(self) -> int:
        return self._win_all

    @win_sync.setter
    def win_sync(self, input: int):
        if not isinstance(input, int):
            emessage = f"win_sync input should be an int. Found type {type(input)}"
            raise Exception(emessage)
        self._win_sync = input

    @property
    def rating_all(self) -> float:
        return self._rating_all

    @rating_all.setter
    def rating_all(self, input: float):
        if not isinstance(input, float):
            emessage = f"rating_all input should be a float. Found type {type(input)}"
            raise Exception(emessage)
        self._rating_all = input

    @property
    def rating_sync(self) -> float:
        return self._rating_all

    @rating_sync.setter
    def rating_sync(self, input: float):
        if not isinstance(input, float):
            emessage = f"rating_sync input should be a float. Found type {type(input)}"
            raise Exception(emessage)
        self._rating_sync = input

    @property
    def rating_all(self) -> float:
        return self._rating_all

    @rating_all.setter
    def rating_all(self, input: float):
        if not isinstance(input, float):
            emessage = f"rating_all input should be a float. Found type {type(input)}"
            raise Exception(emessage)
        self._rating_all = input
