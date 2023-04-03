import discord
from discord.utils import get
from classes.Race import Race
from classes.Buttons import ListingButtonsWithJoin, ListingButtonsNoJoin
from datetime import datetime
from functions.constants import LOG_CRITICAL, TZ, RACETYPE_ASYNC, RACETYPE_SYNC

async def update_race_listing(race_channel, races):
    """
    Updates an embed listing in the active-races channel

    Parameters
    ----------
    race_channel : str
        An FF6WC Raceroom bot Race's name

    races : dict
        A dictionary containing racerooms

    Returns
    -------
    dict:
        json data
    """
    race = races[race_channel]

    if not isinstance(race_channel, str):
        emessage = f"input must be a string. Found type {type(race_channel)}"
        raise Exception(emessage)

    if not race.guild or not race.guild.id:
        emessage = f"Race does not have proper guild information.\n {race}\n"
        raise Exception(emessage)



    listing = None
    guild = race.guild
    listings_channel = get(guild.channels, name="active-races")
    async for message in listings_channel.history(around = race.opened_date):
        if race.channel_name in message.content:
            listing = message
        elif len(message.embeds) > 0:
            for embed in message.embeds:
                if race.channel_name in embed.title or race.channel_name in message.content:
                    listing = message
        else:
            await message.delete()

    '''
    view = discord.ui.View()
    style = discord.ButtonStyle.primary
    item = discord.ui.Button(style=style, label="Join this race",url="https://www.ff6wc.com")
    view.add_item(item=item)
    '''
    embed = discord.Embed(
        title = f'Race: {race.channel_name}',
        description = race.description,
        colour = discord.Colour.blue()
    )

    seedmsg='This race does not have a seed yet (or is being run without a seed)'
    now = datetime.now()
    embed.set_thumbnail(url='https://i.imgur.com/CS1qB2z.jpg')
    embed.set_author(name=f'Race created by: {race.creator.name}', icon_url=race.creator.avatar)
    if race.url:
        seedmsg = ''
        if race.preset:
            seedmsg += f'Rolled from SeedBot preset: `{race.preset}`\n'
        seedmsg += f"View this seed's flags: {race.url}\n"
    if race.filename:
        seedmsg = 'Race being run using an uploaded seed - join the race to learn more!'

    if race.closed_date != None:
        status_msg = 'Race completed'
    elif race.type == RACETYPE_SYNC:
        if race.race_start_date != None:
            status_msg = f'Race in progress'
        else:
            status_msg = 'Not yet started'
    else:
        status_msg = 'Ongoing (accepting new entrants)'



    embed.add_field(name='Seed Info', value=seedmsg, inline=False)
    if race.type == RACETYPE_SYNC and race.race_start_date !=None:
        embed.add_field(name='Current Status', value=status_msg, inline=True)
        embed.add_field(name='Race Started', value=discord.utils.format_dt(race.race_start_date,style='R'), inline=True)
        embed.add_field(name=chr(173), value=chr(173), inline=True)
    else:
        embed.add_field(name='Current Status', value=status_msg, inline=False)
    embed.add_field(name='Race Opened', value=discord.utils.format_dt(race.opened_date, style = 'F'), inline=True)
    embed.add_field(name='Race Style', value=race.type, inline=True)
    embed.add_field(name='Entrants', value=len(race.members), inline=True)
    if race.scheduled_close is not None:
        embed.add_field(name=chr(173), value=chr(173), inline=False)
        embed.add_field(name='Scheduled finish', value=discord.utils.format_dt(race.scheduled_close, style = 'F'), inline=True)
        embed.add_field(name='Race will close', value=discord.utils.format_dt(race.scheduled_close,style='R'), inline=True)
    embed.set_footer(text=f'Last updated: {datetime.now(tz=TZ).strftime("%b %d %Y at %I:%M:%S%p %Z")}')

    if (race.type == RACETYPE_SYNC and race.race_start_date != None) or (race.closed_date != None):
        listing_view = ListingButtonsNoJoin(race.guild, None, race.channel_name, races)
    else:
        listing_view = ListingButtonsWithJoin(race.guild, None, race.channel_name, races)

    if listing is not None:
        await listing.edit(content=None, embed = embed, view=listing_view)
    else:
        await listings_channel.send(content=None, embed=embed,view= listing_view)

