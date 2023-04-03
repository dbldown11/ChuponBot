import discord
from discord import Interaction, TextStyle
from discord.ui import Modal


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


class NewEventModal(Modal):
    event_name = discord.ui.TextInput(
        label="Enter the name for this event:",
        style=TextStyle.short,
        placeholder='Event name',
        max_length=50,
    )
    event_prefix = discord.ui.TextInput(
        label="Enter the prefix for this event's race rooms:",
        style=TextStyle.short,
        placeholder='Prefix',
        max_length=6,
    )
    event_desc = discord.ui.TextInput(
        label="Enter a brief description for this event:",
        style=TextStyle.paragraph,
        placeholder='Event description',
        max_length=150,
    )

    def __init__(self, title: str) -> None:
        super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class URLModal(Modal):
    name = discord.ui.TextInput(
        label="Enter the URL for this seed:",
        style=TextStyle.short,
        placeholder='Paste URL here',
        max_length=1000,
    )

    def __init__(self, title: str) -> None:
        super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class LeagueBasicModal(discord.ui.Modal, title='League setup'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    name = discord.ui.TextInput(
        label='League Name',
        placeholder='Input the name of the league (no season numbers)',
    )

    tiers = discord.ui.TextInput(
        label='Number of tiers',
        placeholder='Input the number of tiers (not divisions!)',
    )

    weeks = discord.ui.TextInput(
        label='Number of weeks',
        placeholder='Input the length of the league in weeks - this is how many races will run',
    )

    flags = discord.ui.TextInput(
        label='Flagset',
        style=discord.TextStyle.paragraph,
        placeholder='Input the flagset for the league races.',
    )

    def __init__(self, title: str) -> None:
        super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()


class LeagueScheduleModal(discord.ui.Modal, title='League scheduling'):
    def __init__(self, title: str, default_start_date : str, default_start_hour : str, default_finish_hour : str) -> None:
        super().__init__(title=title, timeout=None)
        self.start_date = discord.ui.TextInput(
        label='Date of season start (YYYY-MM-DD)',
        placeholder='Input the date that the league will begin.',
        default=default_start_date
        )
        self.start_hour = discord.ui.TextInput(
        label='Hour of race start',
        placeholder='Input the hour of the day in local time that weekly races will open (24 hours, e.g. 13 = 1:00 PM).',
        default=default_start_hour
        )
        self.finish_hour = discord.ui.TextInput(
        label='Hour of race end',
        placeholder='Input the hour of the day in local time that weekly races will close (24 hours, e.g. 13 = 1:00 PM).',
        default=str(default_finish_hour)
        )

        self.add_item(self.start_date)
        self.add_item(self.start_hour)
        self.add_item(self.finish_hour)

    '''
    start_date = discord.ui.TextInput(
        label='Date of season start (YYYY-MM-DD)',
        placeholder='Input the date that the league will begin.',
        default=str(default_start_date)
    )

    start_hour = discord.ui.TextInput(
        label='Hour of race start',
        placeholder='Input the hour of the day in local time that weekly races will open (24 hours, e.g. 13 = 1:00 PM).',
        default=str(default_start_hour)
    )

    end_hour = discord.ui.TextInput(
        label='Hour of race end',
        placeholder='Input the hour of the day in local time that weekly races will close (24 hours, e.g. 13 = 1:00 PM).',
        default=str(default_finish_hour)
    )
    '''
    # def __init__(self, title: str) -> None:
    #    super().__init__(title=title, timeout=None)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()
