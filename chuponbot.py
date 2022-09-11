import discord.app_commands

VERSION = "v.0.3 2022-08-09 (TEST)"

# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
from discord import ui, app_commands, Interaction, TextStyle
from discord.ui import Modal, TextInput
from discord.utils import maybe_coroutine
from typing import Literal, Callable, Coroutine, Optional, Union, Any
from typing_extensions import Self
from datetime import datetime
from discord.app_commands import Choice, command
from discord.ext import commands

# IMPORT ASYNCIO, DO I NEED THIS, WHO EVEN KNOWS
import asyncio

# IMPORT THE OS MODULE.
import os

# IMPORT EMOJI TO CONVERT/INTERPRET EMOJI FROM UNICODE
# import emoji

# IMPORT LOAD_DOTENV FUNCTION FROM DOTENV MODULE.
from dotenv import load_dotenv

import functions.constants
from functions.constants import TESTGUILD
from functions.constants import LOG_CRITICAL, LOG_REGULAR
from functions.string_functions import parse_command
from functions.listraces import listraces
from commands.openrace import openrace
from commands.joinrace import joinrace
from commands.getseed import getseed
from commands.setseed import setseed
from commands.getraces import getraces
from commands.quitrace import quitrace
from commands.finishrace import finishrace
from commands.startrace import startrace
from commands.ready import ready
from commands.unready import unready
from commands.killrace import killrace
from commands.entrants import entrants
from commands.raceinfo import raceinfo
from commands.done import done
from commands.forfeit import forfeit

from functions.create_race_channels import create_race_channels
from functions.loadraces import loadraces

from classes.Log import Log

# DEBUG LOG INIT?
logger = Log()

# INITIALIZES A DICTIONARY OF RACES
races = {}

# LOADS THE .ENV FILE THAT RESIDES ON THE SAME LEVEL AS THE SCRIPT.
load_dotenv()

# GRAB THE API TOKEN FROM THE .ENV FILE.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# INTENTS STUFF
intents = discord.Intents.all()
intents.members = True

# Subclass Client
class Aclient(discord.Client):
    def __init__(self):
        #intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix = "!", intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild = discord.Object(id = TESTGUILD))
            self.synced = True
        print(f"We have logged in as {self.user}.")

        # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
        guild_count = 0

        # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
        for guild in client.guilds:
            # PRINT THE SERVER'S ID AND NAME.
            print(f"- {guild.id} (name: {guild.name})")

            # INCREMENTS THE GUILD COUNTER.
            guild_count = guild_count + 1

        global races

        # PRINTS STARTUP INFO, INCLUDING HOW MANY SERVERS THE BOT IS IN.
        gmessage = f"Fungah! I'm ChuponBot {VERSION}, currently logged in as {client.user}\n"
        gmessage += "ChuponBot is currently active on " + str(guild_count) + " Discord servers.\n"
        logger.show(gmessage, LOG_CRITICAL)

        # The bot has just restarted, so read in the races we know about
        races = loadraces(functions.constants.RACE_PATH, client)

        gmessage = f"Found {len(races.keys())} open races\n"
        for r in races.keys():
            gmessage += f"    {races[r].guild} - {r}\n"
        logger.show(gmessage, LOG_CRITICAL)
        for key in races.keys():
            guild = races[key].guild
            creator = races[key].creator
            name = races[key].channel_name
            if not name:
                name = key
            await create_race_channels(guild, creator, name, logger)
            if not races[key].channel:
                races[key].channel = discord.utils.get(client.get_all_channels(), name=races[key].channel_name)

            for i in races[key].members.keys():
                if not races[key].members[i].channel:
                    races[key].members[i].channel = races[key].channel
'''
class FlagstringModal(ui.Modal):

    def __init__(
            self,
            title="Flagstring",
            *,
            check: Optional[Callable[[Self, Interaction], Union[Coroutine[Any, Any, bool], bool]]] = None,
            timeout: int = 30,
            input_label: str = "Paste your flagstring here:",
            input_max_length: int = 4000,
            input_min_length: int = 1,
            input_style: TextStyle = TextStyle.long,
            input_placeholder: Optional[str] = None,
            input_default: Optional[str] = None,
    ):

        super().__init__(title=title, timeout=timeout, custom_id="flagstring_modal")
        self._check: Optional[Callable[[Self, Interaction], Union[Coroutine[Any, Any, bool], bool]]] = check
        self.value: Optional[str] = None
        self.interaction: Optional[Interaction] = None

        self.answer = TextInput(
            label=input_label,
            placeholder=input_placeholder,
            max_length=input_max_length,
            min_length=input_min_length,
            style=input_style,
            default=input_default,
            custom_id=self.custom_id + "_input_field",
        )
        self.add_item(self.answer)

        async def interaction_check(self, interaction: Interaction) -> bool:
            if self._check:
                allow = await maybe_coroutine(self._check, self, interaction)
                return allow

            return True

        async def on_submit(self, interaction: Interaction) -> None:
            self.value = self.answer.value
            self.interaction = interaction
            self.stop()
'''

class FlagstringModal(Modal):
    name = discord.ui.TextInput(
        label="Enter the flagstring for this seed:",
        style=TextStyle.paragraph,
        placeholder='Paste flagstring here',
        max_length=4000,
    )

    def __init__(self, title: str) -> None:
        super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()

class NewSotwModal(Modal):
    sotwname = discord.ui.TextInput(
        label="Enter the name for this seed:",
        style=TextStyle.short,
        placeholder='Seed name',
        max_length=100,
    )

    sotwsubmitter = discord.ui.TextInput(
        label="Enter the flagset creator's name:",
        style=TextStyle.short,
        placeholder='Submitter''s name',
        max_length=100,
    )

    sotwflags = discord.ui.TextInput(
        label="Enter the flagstring for the sotw:",
        style=TextStyle.paragraph,
        placeholder='Paste flagstring here',
        max_length=4000,
    )

    def __init__(self, title: str) -> None:
        super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT. WILL ALSO RUN ON READY STUFF FROM SUBCLASS
client = Aclient()
tree = app_commands.CommandTree(client)

help ="""
```ansi
\u001b[0;0m\u001b[1;35mChuponBot - %s
```
The bot currently supports the following commands:
    `!help`
        Prints this help text
    `!openrace`
        Opens a race. If no options are provided, the race will be synchronous (players must race at the same time) and a random name will be generated. 
        A raceroom and spoiler room will be generated. 
        The following options exist:
            `-name <racename>`: Open a race with the name <racename>. Must be between 1 and 29 characters
            `-async`: Opens an async race. Races are sync by default
            `-hidden` : Opens a race with a hidden seed which will only be rolled and DMed to the players right before start
            You may combine -async and -hidden to make a hidden async race.
    `!finishrace`
        Removes a raceroom and its spoiler room after a brief delay
    `!join <racename>`
        Joins a race called <racename>, if it exists
    `!startrace`
        Starts a race
    `!ready / !unready`
        Ready or unready yourself for a race
    `!quit`
        Quits a race
    `!forfeit / !ff`
        Forfeits from a race
    `!entrants`
        Lists the entrants of a race
    `!raceinfo`
        Lists information about a race
    `!done` / `!done 11:22:33`
        When used in a race room, marks a race as completed in the given time (in this case 11 hours, 22 minutes, and 33 seconds)
        For hidden seeds or asyncs, just use !done
    `!getseed`
        Asks for a specfic seed for a given race, specified by the room the command is run in. 
        This seed will be DMed to the user and a timer will start once it has been DMed. 
        When the racer types !done, the total time between the DM and done command will be the runner's time.
    `!setseed`
        Sets the seed URL for a race. Can only be called by channel or race admins
""" % (VERSION)

adminhelp = """\n
Admin-only commands:
    `/getraces`
        A command for administrators which shows the current races
    `!gethistory`
        Get the history of races, stored in db/races.txt
    `!killrace`
        Immediately closes a race room and its spoiler room. 
        This does not check to see if all racers are finished.
"""

@tree.command(name = "help", description = "A list of ChuponBot's commands", guild = discord.Object(id = TESTGUILD))
# @app_commands.checks.cooldown(1,5,key = lambda i: (i.user.id)) ### COOLDOWN ONLY NEEDED IF COMMAND DOES API CALL
async def self(interaction: discord.Interaction):
    await interaction.response.send_message(help, ephemeral = True)
    role = discord.utils.get(interaction.user.roles, name=functions.constants.ADMIN_ROLE)
    if role is not None and role.name == functions.constants.ADMIN_ROLE:
        await interaction.followup.send(adminhelp, ephemeral = True)

# OPENS A RACE ROOM USING THE SETTINGS ENTERED
# racetype and hidden are required, all other options are optional
@tree.command(name = "openrace", description = "Creates a new FF6WC race", guild = discord.Object(id = TESTGUILD))
@app_commands.describe(racetype='If "Sync", racers compete in real-time. If "Async", racers can complete the seed whenever convenient.')
@app_commands.describe(hidden='If "Yes", seed will be DM''d to racers. If "No", seed will be immediately available.')
@app_commands.describe(name='(Optional) Give the channel a unique name. If not named, race will get an auto-generated string.')
@app_commands.describe(desc='(Optional) Give the race a description to be displayed in the race directory.')
async def self(interaction: discord.Interaction,racetype: Literal['sync', 'async'],hidden: Literal['yes','no'], name: str = None, desc: str = None):
    args = {}
    args['racetype'] = racetype
    args['hidden'] = hidden
    args['name'] = name
    args['desc'] = desc
    new_race = await openrace(interaction, args)

    # If raceroom creation failed, don't add it to the list of rooms, but print a message
    if not new_race:
        emessage = f"{interaction.guild} -- Failed to create raceroom in {interaction.channel}\n\t{interaction.user} - {interaction.command}"
        logger.show(emessage, LOG_CRITICAL)
        return
    races[new_race.channel.name] = new_race

@tree.command(name = "join", description = "Joins an open FF6WC race", guild = discord.Object(id = TESTGUILD))
@app_commands.describe(room='The full name of an open race room.')
async def join(interaction: discord.Interaction,room: str):
    await joinrace(interaction.guild, interaction, room, races)

@join.autocomplete('room')
async def join_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    rooms = [r for r in races.keys()]
    return [
        app_commands.Choice(name=room,value=room)
        for room in rooms if current.lower() in room.lower()
    ]

@tree.command(name = "getraces",description = "Displays a list of all open WC races on the server", guild = discord.Object(id = TESTGUILD))
async def self(interaction: discord.Interaction):
    await getraces(interaction, races)

# Start a race
@tree.command(name="startrace",description="Starts a race", guild = discord.Object(id = TESTGUILD))
async def startrace_command(interaction: discord.Interaction):
    await startrace(interaction, races)

# Setseed group of commands
setseed_group = app_commands.Group(name='setseed', description= '(Race Admin Only) Set the URL or flags for the race seed')

@setseed_group.command(name='flagstring', description= '(Race Admin Only) Opens a popup to set the race seed using an FF6WC flagstring')
async def setseed_flagstring(interaction: Interaction):
    modal = FlagstringModal('Race flagstring')
    await interaction.response.send_modal(modal)
    await modal.wait()
    await setseed(interaction=interaction,races=races,flagstring=modal.name.value)
    #await interaction.followup.send(f"I'll be spewing out a seed with these flags: {modal.name.value}")

@setseed_group.command(name='url', description = '(Race Admin Only) Sets the race seed using a FF6WC url (e.g. https://ff6wc.com/seed/E6n93pxzhYEs)')
async def setseed_url(interaction: Interaction, url: str):
    await interaction.response.defer(ephemeral=True)
    await setseed(interaction=interaction,races=races,url=url)

@setseed_group.command(name='upload', description = '(Race Admin Only, NOT YET IMPLEMENTED) Sets the race seed by uploading an existing ROM')
async def setseed_upload(interaction: Interaction):
    # One day an embed will grab an attached file here. one day. For now, GNDN.
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("This feature is not yet implemented!")
    return

# Adds the setseed commands to the command tree
tree.add_command(setseed_group, guild = discord.Object(id = TESTGUILD))

# Set yourself as ready for a race
@tree.command(name = "ready",description = "Set yourself as ready to begin the race", guild = discord.Object(id = TESTGUILD))
async def ready_command(interaction: Interaction):
    await ready(interaction, races)

# Set yourself as unready for a race
@tree.command(name = "unready",description = "Set yourself as ready to begin the race", guild = discord.Object(id = TESTGUILD))
async def unready_command(interaction: Interaction):
    await unready(interaction, races)

# Get a list of race entrants
@tree.command(name = "entrants",description = "Lists the entrants of a race", guild = discord.Object(id = TESTGUILD))
async def entrants_command(interaction: Interaction):
    await entrants(interaction, races)

# Gets information about the race in this room
@tree.command(name = "raceinfo",description="Lists information about a race", guild = discord.Object(id = TESTGUILD))
async def raceinfo_command(interaction: Interaction):
    await raceinfo(interaction, races)

# Finishes a user's race and adds them to the race room's spoiler channel
@tree.command(name = "done", description="Mark that you have finished a race", guild = discord.Object(id = TESTGUILD))
@app_commands.describe(time='(Async only) Your total elapsed time to finish the seed (hh:mm:ss), e.g. /done time 1:23:45')
async def done_command(interaction: Interaction, time: str = None):
    await done(interaction=interaction,races=races,time = time)

# Cowardly forfeits from a race
@tree.command(name = "forfeit", description="Forfeit from a race", guild = discord.Object(id = TESTGUILD))
async def forfeit_command(interaction: Interaction):
    await forfeit(interaction=interaction,races=races)

# Quit from a race
@tree.command(name = "quit", description = "Quit a race", guild = discord.Object(id = TESTGUILD))
async def quit(interaction: discord.Interaction):
    await quitrace(interaction, races)

# Close a race that has been finished
@tree.command(name = "finishrace", description = "Close out a race room and its spoiler room after a brief delay", guild = discord.Object(id = TESTGUILD))
@app_commands.describe(logmessage='(Optional) A message to be added to the race''s log')
async def finishrace_command(interaction: discord.Interaction, logmessage: str = None):
    await interaction.response.defer()
    await finishrace(interaction,races,logmessage)

# Immediately close a race and all associated rooms, finished or not!
@tree.command(name = "killrace", description = "(Racebot admin only) Immediately force closes a race room and its spoiler room", guild = discord.Object(id = TESTGUILD))
async def killrace_command(interaction: Interaction):
    await killrace(interaction,races)

sotw_group = app_commands.Group(name='sotw', description= '(POC) Do SOTW stuff')
@sotw_group.command(name="new", description = "(POC only) Roll a new SOTW")
async def sotw_new_command(interaction:Interaction):
    modal = NewSotwModal('Enter the new SotW')
    await interaction.response.send_modal(modal)
    await modal.wait()
    await interaction.followup.send(f"The new SOTW, {modal.sotwname}, from {modal.sotwsubmitter} has been set!\nHere are the flags:\n{modal.sotwflags}")

tree.add_command(sotw_group, guild=discord.Object(id=TESTGUILD))

'''
# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@client.event
async def on_message(message):
    # sets the guild to the current server and makes sure this isn't a DM
    if isinstance(message.channel, discord.channel.TextChannel):
        guild = message.channel.guild

    # Ignore messages from Chupon himself
    if message.author == client.user:
        return

    #ignore non-! things (these aren't Chupon commands)
    if not message.content.startswith("!"):
        return

    commands_values = parse_command(message.content)

    if message.content.startswith("!help"):
        await message.channel.send(help)
        #if message.author.id in functions.constants.ADMINS:
        role = discord.utils.get(message.author.roles, name=functions.constants.ADMIN_ROLE)
        if role is not None and role.name == functions.constants.ADMIN_ROLE:
            await message.channel.send(adminhelp)

    # Opens a race, creating a race channel and a spoiler channel for it
    if message.content.startswith("!openrace"):
        new_race = await openrace(guild, message, commands_values)

        # If raceroom creation failed, don't add it to the list of rooms, but print a message
        if not new_race:
            emessage = f"{message.guild} -- Failed to create raceroom in {message.channel}\n\t{message.author} - {message.content}"
            logger.show(emessage, LOG_CRITICAL)
            return
        races[new_race.channel.name] = new_race

    # This command gets the seed specified for the given room
    if message.content.startswith("!getseed"):
        await getseed(guild, message, commands_values, races)

    # Admin only: Get current race rooms
    if message.content.startswith("!getraces"):
        await getraces(message, races)

    # Admin only: Set room seed
    if message.content.startswith("!setseed"):
        await setseed(guild, message, commands_values, races)

    if message.content.startswith('!openroom'):
        from discord.utils import get
        cat = get(guild.categories, name="Racing")
        race_room_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            message.author: discord.PermissionOverwrite(read_messages=True)
        }
        channel = await guild.create_text_channel('test-channel', category=cat, overwrites=race_room_overwrites)
        await channel.send('Fungah! I made a room!')

    if message.content.startswith('!thumbsup'):
        channel = message.channel
        await channel.send('Send me that 👍 reaction, mate')

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '👍'

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('👎')
        else:
            await channel.send('👍')
'''
# EVENT LISTENER FOR WHEN A USER GETS A NEW ROLE
@client.event
async def on_member_update(before, after):
    if len(before.roles) < len(after.roles):
        # The user has gained a new role, so lets find out which one
        newRole = next(role for role in after.roles if role not in before.roles)

        channel = client.get_channel(1006396949173387334)
        await channel.send("{} has gained the role: {}".format(before,newRole))

        #if newRole.name == "Respected":


# Runs Chupon with Token (from .env)
client.run(DISCORD_TOKEN)
