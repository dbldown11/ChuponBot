import discord
import discord.ui
from discord import app_commands

from commands.setseed import setseed
from commands.joinrace import joinrace
from commands.entrants import entrants
from commands.raceinfo import raceinfo
from commands.getstreams import getstreams
import functions.update_raceroom_pin
import functions.update_spoiler_room_pin

from classes.Race import Race
from classes.Modals import FlagstringModal, URLModal, LeagueBasicModal, LeagueScheduleModal

# Simple View that gives a Join Button and Restream Options for a given race
class ListingButtonsWithJoin(discord.ui.View):
    def __init__(self, guild: discord.Guild, interaction: discord.Interaction, room: str, races:dict):
        super().__init__(timeout=None)
        self.value = None
        self.guild = guild
        self.interaction = interaction
        self.room = room
        self.races = races

    @discord.ui.button(label='Join this race', style=discord.ButtonStyle.primary, custom_id='JoinButton')
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message('Joining race!', ephemeral=True)
        #await interaction.response.defer()
        await joinrace(self.guild,interaction,self.room,self.races)
        await functions.update_raceroom_pin.update_raceroom_pin(self.room, self.races)
        await functions.update_spoiler_room_pin.update_spoiler_room_pin(self.room, self.races)
        #self.stop()

    @discord.ui.button(label='Get stream links', style=discord.ButtonStyle.primary, custom_id='WatchStream')
    async def watchstream(self,interaction: discord.Interaction, button: discord.ui.Button):
        await getstreams(interaction,self.races,self.room)
        #self.stop()

# Simple View that without a Join Button and Restream Options for a given race
class ListingButtonsNoJoin(discord.ui.View):
    def __init__(self, guild: discord.Guild, interaction: discord.Interaction, room: str, races:dict):
        super().__init__(timeout=None)
        self.value = None
        self.guild = guild
        self.interaction = interaction
        self.room = room
        self.races = races

    @discord.ui.button(label='Get stream links', style=discord.ButtonStyle.primary, custom_id='WatchStream')
    async def watchstream(self,interaction: discord.Interaction, button: discord.ui.Button):
        await getstreams(interaction,self.races,self.room)
        #self.stop()

# View with the control panel for the top of race rooms
class RaceroomControlPanel(discord.ui.View):
    def __init__(self, races: dict):
        super().__init__(timeout=None)
        self.races = races
        # self.value = None
        '''
        self.interaction = interaction
        self.races = races
        '''

    @discord.ui.button(label='Show Race Info', style=discord.ButtonStyle.primary, row = 0, custom_id="raceroom_raceinfo")
    async def raceinfo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message('Joining race!', ephemeral=True)
        #await interaction.response.defer()
        await raceinfo(interaction,self.races)

    @discord.ui.button(label='Show Entrants', style=discord.ButtonStyle.primary, row = 0, custom_id="raceroom_showentrants")
    async def entrants_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.send_message('Joining race!', ephemeral=True)
        #await interaction.response.defer()
        await entrants(interaction,self.races)

    @discord.ui.button(label='Show Race Streams', style=discord.ButtonStyle.primary, row = 0, custom_id="raceroom_showstreams")
    async def showstreams_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await getstreams(interaction,self.races, room=None)

    @discord.ui.button(label='Set Seed Using Flagstring', style=discord.ButtonStyle.green, row=1, custom_id="raceroom_setseed_flagstring")
    async def setseed_flagstring_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Joining race!', ephemeral=True)
        # await interaction.response.defer()
        modal = FlagstringModal('Race flagstring')
        await interaction.response.send_modal(modal)
        await modal.wait()
        await setseed(interaction=interaction, races=self.races, flagstring=modal.name.value)

    @discord.ui.button(label='Set Seed Using URL', style=discord.ButtonStyle.green, row=1, custom_id="raceroom_setseed_url")
    async def setseed_url_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Joining race!', ephemeral=True)
        # await interaction.response.defer()
        modal = URLModal('Enter URL')
        await interaction.response.send_modal(modal)
        await modal.wait()
        await setseed(interaction=interaction, races=self.races, url=modal.name.value)

    @discord.ui.button(label='Set Seed by Uploading ROM', style=discord.ButtonStyle.green, row=1, custom_id="raceroom_setseed_file")
    async def setseed_file_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Joining race!', ephemeral=True)
        # await interaction.response.defer()
        await interaction.response.send_message(
            'To upload a file, please use the `/setseed upload` command in this race room.',
        ephemeral=True
        )

    @discord.ui.button(label='Set Seed Using Preset', style=discord.ButtonStyle.green, row=1, custom_id="raceroom_setseed_preset")
    async def setseed_flagstring_preset(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Joining race!', ephemeral=True)
        # await interaction.response.defer()
        await interaction.response.send_message(
            'To select a Seedbot preset, please use the `/setseed preset` command in this race room.',
        ephemeral=True
        )

    #TODO This also isn't implemented yet
    '''
    @discord.ui.button(label='Upload Custom Seed', style=discord.ButtonStyle.green, row=1)
    async def setseed_flagstring_custom(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('Joining race!', ephemeral=True)
        # await interaction.response.defer()
        await joinrace(self.guild, interaction, self.room, self.races)
    '''

class LeagueBuilderView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.value = None
        self.interaction = interaction
        self.guild = interaction.guild
        self.name = ''
        self.weeks = 0
        self.start_date = 0
        self.start_hour = 2
        self.finish_hour = 11

    @discord.ui.button(label='Set up basic league info', style=discord.ButtonStyle.primary)
    async def basicleagueinfobutton(self,interaction: discord.Interaction, button: discord.ui.Button):
        modal = LeagueBasicModal('Basic League Info')
        await interaction.response.send_modal(modal)
        self.name = modal.name
        self.weeks = modal.weeks

    @discord.ui.button(label='Set up league race scheduling', style=discord.ButtonStyle.primary)
    async def leagueschedulebutton(self,interaction: discord.Interaction, button:discord.ui.Button):
        modal = LeagueScheduleModal('League Scheduling Info',default_start_date = self.start_date,
                                    default_start_hour = self.start_hour, default_finish_hour = self.finish_hour)
        '''
        modal.default_start_date = self.start_date
        modal.default_start_hour = self.start_hour
        modal.default_finish_hour = -self.finish_hour
        '''
        await interaction.response.send_modal(modal)
        print(modal.start_hour.value)
        self.start_date = modal.start_date.value
        self.start_hour = modal.start_hour.value
        self.finish_hour = modal.finish_hour.value

    @discord.ui.button(label='View input data', style=discord.ButtonStyle.primary)
    async def viewbutton(self,interaction: discord.Interaction, button: discord.ui.Button):
        msg = ''
        msg += f'league name is {self.name}\n'
        msg += f'league length is {self.weeks} weeks\n'
        msg += f'league start date is {self.start_date}\n'
        msg += f'league start hour is {self.start_hour}:00\n'
        msg += f'league finish hour is {self.finish_hour}:00\n'
        await interaction.response.send_message(msg)

class ConfirmButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()