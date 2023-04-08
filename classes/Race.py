import discord
import datetime
import json
import os
import shutil
import dateutil.parser
import asqlite
import sqlite3

from functions.constants import TZ
from classes.Log import Log
from functions.lograce import create_race_file
from functions.generate_z_score import generate_z_score
import functions.constants

class Race:
    """An object to store races"""
    from classes import RaceRunner
    def __init__(self, in_interaction, in_channel, initialize=True)->None:
        self._channel = None
        self._guild = None
        self._creator = None
        self._description = None
        self._stream_url = None #NOTE: this is not being written to json rn!
        self._preset = None
        self._url = None
        self._hash = None
        self._version = None
        self._flags = None
        self._filename = None
        self._admins = set(functions.constants.ADMINS)
        self._type = None
        self._members = {}
        self._opened_date = None
        self._closed_date = None
        self._scheduled_close = None
        self._race_start_date = None
        self._isHidden = False
        self._comments = ""
        self._results = ""
        self._closed = False
        self._path_open = None
        self._path_closed = None
        self._loaded_race = False
        self._channel_name = None
        self._entrants_msg_id = None
        self._entrants_spoiler_msg_id = None
        self._race_listing_msg_id = None #NOTE: this is not being written to json rn!
        self._event_name = None #NOTE: this is not being written to json rn!
        self._gp_pool = None
        self._restrict_role_id = None

        if initialize:
            if not isinstance(in_interaction, discord.Interaction):
                emessage = f"message must be a discord.Interaction. Found type {type(input)}"
                raise Exception(emessage)
            if not isinstance(in_channel, discord.channel.TextChannel):
                emessage = f"channel must be a discord.channel.TextChannel. Found type {type(input)}"
                raise Exception(emessage)

            self.creator = in_interaction.user
            self.admins.add(self.creator.id)
            self.opened_date = datetime.datetime.now()
            self.guild = in_interaction.guild
            self.channel = in_channel
            self.path_open = functions.constants.RACE_PATH
            self.gp_pool = 0
            self.log()
            #TODO: INSERT INTO THE DB HERE
            '''
            path = os.path.join(functions.constants.DATA_PATH, 'testdata.db')
            data = (self.channel.name, self.guild.id, self.creator.id, self.opened_date)
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO races (race_name, guild, creator_id, date_opened) 
                        VALUES (?, ?, ?, ?)""", data)
            conn.commit()
            conn.close()
            '''
        else:
            self._loaded_race = True


    @property
    def channel(self) -> discord.channel.TextChannel:
        return self._channel

    @channel.setter
    def channel(self, input:discord.channel.TextChannel) -> None:
        if not isinstance(input, discord.channel.TextChannel):
            emessage = f"input should be a discord.channel.TextChannel. Found type {type(input)}"
            raise Exception(emessage)
        self._channel = input
        self._channel_name = input.name

    @property
    def guild(self) -> discord.guild.Guild:
        return self._guild

    @guild.setter
    def guild(self, input:discord.guild.Guild) -> None:
        if not isinstance(input, discord.guild.Guild):
            emessage = f"input must be a discord.guild.Guild. Found type {type(input)}"
            raise Exception(emessage)
        self._guild = input


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
        if input is None:
            self._description = 'No details available - join the race room or contact the race creator to learn more!'
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._description = input

    @property
    def stream_url(self) -> str:
        return self._stream_url

    @stream_url.setter
    def stream_url(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._stream_url = input
    @property
    def preset(self) -> str:
        return self._preset

    @preset.setter
    def preset(self, input:str) -> None:
        if not isinstance(input, str) and input != None:
            emessage = f"preset input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._preset = input
 #       self.log(functions.constants.LOG_TRIVIAL)

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, input:str) -> None:
        if input is None:
            return
        if not isinstance(input, str) and input != None:
            emessage = f"url input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        if not input.upper().startswith("HTTP") or "/seed/" not in input:
            emessage = f"input doesn't appear to be a valid seed link. Found {input}"
            raise Exception(emessage)
        self._url = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def hash(self) -> str:
        return self._hash

    @hash.setter
    def hash(self, input:str) -> None:
        if not isinstance(input, str) and input != None:
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        elif ',' not in input or len(input.split(',')) != 4:
            emessage = f"input doesn't appear to be a valid hash - {input}"
            raise Exception(emessage)
        self._hash = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._version = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def flags(self) -> str:
        return self._flags

    @flags.setter
    def flags(self, input:str) -> None:
        if input is None:
            return
        if not isinstance(input, str):
            emessage = f"input should be a str. Found type {type(input)}"
            raise Exception(emessage)
        self._flags = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, input:str) -> None:
        self._filename = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def admins(self) -> set:
        #Set of discord IDs
        return self._admins

    @admins.setter
    def admins(self, input:int) -> None:
        if not isinstance(input, (list, tuple, int)):
            emessage = f"input should be an int or set/list/tuple of ints representing a discord ID. Found type {type(input)}"
            raise Exception(emessage)
        if isinstance(input, int):
            self._admins = set()
            self._admins.add(input)
            return
        for item in input:
            if not isinstance(item, int):
                emessage = f"input should be an int or set/list/tuple of ints representing a discord ID. Found type {type(item)}"
                raise Exception(emessage)
        self._admins = set(input)

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be type str. Found type {type(input)}"
            raise Exception(emessage)
        if not input.strip().lower() in functions.constants.RACETYPES:
            emessage = f"input must be one of: {functions.constants.RACETYPES}"
            raise Exception(emessage)
        self._type = input
        #self.log(functions.constants.LOG_TRIVIAL)

    @property
    def members(self) -> dict:
        return self._members

    @members.setter
    def members(self, input) -> None:
        if not self._loaded_race:
            emessage = "Race.members cannot be set directly. Use the addRacer and removeRacer methods."
            raise Exception(emessage)
        self._members = input

    @property
    def opened_date(self) -> datetime.datetime:
        return self._opened_date

    @opened_date.setter
    def opened_date(self, input: datetime.datetime) -> None:
        if not isinstance(input, datetime.datetime):
            emessage = f"input should be datetime.datetime. Found type {type(input)}"
            raise Exception(emessage)
        self._opened_date = input

    @property
    def closed_date(self) -> datetime.datetime:
        return self._closed_date

    @closed_date.setter
    def closed_date(self, input) -> None:
            emessage = f"closed_date is set automatically when the race is closed"
            raise Exception(emessage)

    @property
    def race_start_date(self) -> datetime.datetime:
        return self._race_start_date

    @race_start_date.setter
    def race_start_date(self, input:datetime.datetime) -> None:
        if not isinstance(input, datetime.datetime):
            emessage = f"input should be datetime.datetime. Found type {type(input)}"
            raise Exception(emessage)
        self._race_start_date = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def scheduled_close(self) -> datetime.datetime:
        return self._scheduled_close

    @scheduled_close.setter
    def scheduled_close(self, input:datetime.datetime) -> None:
        if not isinstance(input, datetime.datetime):
            emessage = f"input should be datetime.datetime. Found type {type(input)}"
            raise Exception(emessage)
        self._scheduled_close = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def isHidden(self) -> bool:
        return self._isHidden

    @isHidden.setter
    def isHidden(self, input:bool) -> None:
        if not isinstance(input, bool):
            emessage = f"input should be bool, found type {type(input)}"
            raise Exception(emessage)
        self._isHidden = input

    @property
    def comments(self) -> str:
        return self._comments

    @comments.setter
    def comments(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be str. Found type {type(input)}"
            raise Exception(emessage)
        self._comments = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def results(self) -> str:
        return self._results

    @results.setter
    def results(self, input:bool) -> None:
        emessage = "results is automatically set when the race is closed"
        raise Exception(emessage)

    @property
    def path_open(self) -> str:
        return self._path_open

    @path_open.setter
    def path_open(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be type str. Found type {type(input)}"
            raise Exception(emessage)

        if not self._loaded_race:
            self._path_open = create_race_file(input, self)
            self._path_closed = self.path_open.replace(os.sep + "open" + os.sep, os.sep + "closed" + os.sep)
        else:
            self._path_open = input
            self._path_closed = self.path_open.replace(os.sep + "open" + os.sep, os.sep + "closed" + os.sep)

    @property
    def path_closed(self) -> str:
        return self._path_closed

    @path_closed.setter
    def path_closed(self, input:str) -> None:
        if not isinstance(input, str):
            emessage = f"input should be type str. Found type {type(input)}"
            raise Exception(emessage)
        self._path_closed = input

    @property
    def closed(self) -> bool:
        return self._closed

    @closed.setter
    def closed(self, input) -> None:
        emessage = "The closed property is automatically set when the race is closed"
        raise Exception(emessage)

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @channel_name.setter
    def channel_name(self, input) -> None:
        """Need this because if we lose the main channel in a crash, we need somewhere to store the
           name of the channel on load so we can re-create it in an async environment"""
        if not isinstance(input, str):
            emessage = f"input should be type str. Found type {type(input)}"
            raise Exception(emessage)
        self._channel_name = input

    @property
    def entrants_msg_id(self) -> str:
        return self._entrants_msg_id

    @entrants_msg_id.setter
    def entrants_msg_id(self, input) -> None:
        if not isinstance(input, int) and input != None:
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._entrants_msg_id = input
#        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def entrants_spoiler_msg_id(self) -> str:
        return self._entrants_spoiler_msg_id

    @entrants_spoiler_msg_id.setter
    def entrants_spoiler_msg_id(self, input) -> None:
        if not isinstance(input, int) and input != None:
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._entrants_spoiler_msg_id = input
#        self.log(functions.constants.LOG_TRIVIAL)
    
    @property
    def race_listing_msg_id(self) -> str:
        return self._race_listing_msg_id

    @race_listing_msg_id.setter
    def race_listing_msg_id(self, input) -> None:
        if not isinstance(input, int):
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._race_listing_msg_id = input
        self.log(functions.constants.LOG_TRIVIAL)
        
    @property
    def event_name(self) -> str:
        return self._event_name

    @event_name.setter
    def event_name(self, input) -> None:
        if not isinstance(input, int):
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._event_name = input
        self.log(functions.constants.LOG_TRIVIAL)

    @property
    def loaded_race(self) -> bool:
        return self._loaded_race

    @loaded_race.setter
    def loaded_race(self, input: bool):
        if not isinstance(input, bool):
            emessage = f"input should be bool, found type {type(input)}"
            raise Exception(emessage)
        self._loaded_race = input

    @property
    def gp_pool(self) -> int:
        return self._gp_pool

    @gp_pool.setter
    def gp_pool(self, input) -> None:
        if not isinstance(input, int) and input != None:
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._gp_pool = input

    ### DT, 4/6/23
    @property
    def restrict_role_id(self) -> int:
        return self._restrict_role_id

    @restrict_role_id.setter
    def restrict_role_id(self, input) -> None:
        if not isinstance(input, int) and input != None:
            emessage = f"input should be int. Found type {type(input)}"
            raise Exception(emessage)
        self._restrict_role_id = input
    ###

    def close(self) -> None:
        """Closes the race"""
        self._closed_date = datetime.datetime.now()
        times = {}
        results = []
        for member in self.members.keys():
            times[self.members[member].time_taken] = member
        counter = 1
        for time in sorted(times.keys()):
            runner = times[time]
            results.append((counter,runner,time))
        self._results = results
        self._closed = True

        msg= ''
        # delete any associated files uploaded for this race
        path = os.path.join(functions.constants.UPLOADS_PATH,self.channel.name)
        if self.closed and os.path.exists(path):
            try:
                shutil.rmtree(path)
                msg += f"\nDeleted {path} and all contents from local storage"
                print(msg)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        #self.log()

    def addRacer(self, input:RaceRunner) -> None:
        """Adds a RaceRunner to this Race.
        """
        from classes import RaceRunner
        if not isinstance(input, RaceRunner.RaceRunner):
            emessage = f"input should be an FF6WC-raceroombot-RaceRunner. Found type {type(input)}"
            raise Exception(emessage)
        self._members[input.member.name] = input
        #self.log(functions.constants.LOG_TRIVIAL)

    def removeRacer(self, input:RaceRunner) -> None:
        """Removes a RaceRunner from this Race.
        """
        from classes import RaceRunner
        if not isinstance(input, RaceRunner.RaceRunner):
            emessage = f"input should be an FF6WC-raceroombot-RaceRunner. Found type {type(input)}"
            raise Exception(emessage)
        if input.member.name in self._members:
            del self._members[input.member.name]
        self.log(functions.constants.LOG_TRIVIAL)


    def toJSON(self) -> str:
        output = '{\n'
        output += f'\t"guild":"{self.guild.id}",\n'
        output += f'\t"channel":"{self.channel_name}",\n'
        output += f'\t"entrants_msg_id":"{self.entrants_msg_id}",\n'
        output += f'\t"entrants_spoiler_msg_id":"{self.entrants_spoiler_msg_id}",\n'
        output += f'\t"creator":"{self.creator.id}",\n'
        output += f'\t"description":"{self.description}",\n'
        output += f'\t"creator_name":"{self.creator.name}",\n'
        output += f'\t"filename":"{self.filename}",\n'
        output += f'\t"preset":"{self.preset}",\n'
        output += f'\t"url":"{self.url}",\n'
        output += f'\t"hidden":"{self.isHidden}",\n'
        output += f'\t"hash":"{self.hash}",\n'
        output += f'\t"version":"{self.version}",\n'
        output += f'\t"flags":"{self.flags}",\n'
        output += f'\t"type":"{self.type}",\n'
        output += f'\t"admins":[' + (',').join([str(admin) for admin in self.admins]) + '],\n'
        output += f'\t"members":[\n'
        for member_key in self.members.keys():
            output += f'\t' + self.members[member_key].toJSON().replace('\n', '\n\t\t').replace('\t}', '},')
        if output.strip().endswith(','):
            output = output.strip()[:-1]
        output += f'\t],\n'

        output += f'\t"date_opened":"{self.opened_date}",\n'
        output += f'\t"date_started":"{self.race_start_date}",\n'
        output += f'\t"date_closed":"{self.closed_date}",\n'
        output += f'\t"scheduled_close":"{self.scheduled_close}",\n'
        output += f'\t"comments":"' + self.comments.replace("\"", "\'") + '",\n'
        output += f'\t"results":["'
        result_txt = []
        for result in self.results:
            result_txt.append(f"\t\t({result[0], result[1], result[2]})\n")
        output += (",").join(result_txt) + "\"]\n"
        output += "}\n"
        output = output.replace("None", "null")
        output = output.replace("\"null\"", "null")
        return output

    def getResults(self) -> str:
        output = "`"
        times = {}
        for member in self.members.keys():
            taken = None
            if not self.members[member].time_taken:
                taken = dateutil.parser.parse('2099-12-31 23:59:59.999') - datetime.datetime.now()
            else:
                taken = self.members[member].time_taken
            times[taken] = member

        # Show those with times
        counter = 1
        for time in sorted(times.keys()):
            #displaytime = str(time).split(".")[0]
            if time < datetime.timedelta(days=180):
                output += f'{counter} - {times[time]} -- {time}\n'
            else:
                output += f'{counter} - {times[time]} -- Forfeited\n'
            counter += 1
        # Now show the forfeits
        output += "`\n"
        return output

    def log(self, priority = 0) -> None:
        """Logs a race to the appropriate location"""
        logger = Log()
        path = self.path_open
        try:
            with open(path, 'w') as f:
                js = self.toJSON()
                f.write(js)
        except Exception as e:
            emessage = f"Unable to write to {path}"

        msg = f"{self.guild} -- Logged this race at {path}\n"
        msg += str(self)
        if self.closed:
            msg += self.getResults()

        if self.closed:
            try:
                if os.path.exists(self.path_open):
                    shutil.move(self.path_open, self.path_closed)
                    msg += f"Moved race {self.path_open} to {self.path_closed}"
            except Exception as e:
                emessage = f"Unable to move {self.path_open} to {self.path_closed}"
                raise Exception(emessage)

        # Deletes any associated uploaded seeds
        path = os.path.join(functions.constants.UPLOADS_PATH,self.channel.name)
        if self.closed and os.path.exists(path):
            try:
                shutil.rmtree(path)
                msg += f"\nDeleted {path} and all contents from local storage"
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

        logger.show(msg + "\n", priority)
        return

    def __str__(self) -> str:
        output = ""
        output += f"Guild:        {self.guild}\n"
        output += f"Channel:      {self.channel_name}\n"
        output += f"Creator:      {self.creator}\n"
        output += f"Description:  {self.description}\n"
        if self.isHidden and not self.closed_date:
            output += f"Seed URL:     Hidden\n"
            output += f"Flags:        Hidden\n"
            output += f"Filename:     Hidden\n"
        else:
            output += f"Seed URL:     {self.url}\n"
            output += f"Flags:        {self.flags}\n"
            output += f"Filename:     {self.filename}\n"
        output += f"Admins:     \n"
        for admin in self.admins:
            output += f"    {str(self.guild.get_member(admin))}\n"
        output += f"Type:         {self.type}\n"
        output += f"Members:     \n"
        if not self.members or len(self.members) == 0:
            output += "    No one has joined this race\n"
        else:
            for member in self.members.keys():
                output += f"    {self.members[member].member.name}\n"
        output += f"Date Opened:  {self.opened_date} ET\n"
        output += f"Date Started: "
        if self.race_start_date:
            output += f"{self.race_start_date} ET\n"
        else:
            output += "Not yet started\n"

        output += f"Scheduled Close: "
        if self.scheduled_close:
            output += f"{self.scheduled_close} ET\n"
        else:
            output += "n/a\n"

        output += f"Date Closed:  "
        if self.closed_date:
            output += f"{self.closed_date} ET\n"
        else:
            output += "Not yet closed\n"

        output += f"Comments:     {self.comments}\n"
        output += "\n"
        return output