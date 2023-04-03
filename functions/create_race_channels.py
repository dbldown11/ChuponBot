import discord
from discord.utils import get
from functions.constants import LOG_CRITICAL
from functions.botconfig import config, env
from functions.update_race_listing import update_race_listing

async def create_race_channels(guild, creator, name, logger, races):
    race_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        creator: discord.PermissionOverwrite(read_messages=True)
    }

    spoiler_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    cat = get(guild.categories, name=config.get(env,"race_category_general"))

    if not name in [r.name for r in guild.channels]:
        races[name].channel = await guild.create_text_channel(name, category=cat, overwrites=race_room_overwrites)
        gmessage = f"{guild} -- Had to recreate channel {name}"
        logger.show(gmessage, LOG_CRITICAL)


    if not name + "-spoilers" in [r.name for r in guild.channels]:
        await guild.create_text_channel(name + "-spoilers", category=cat, overwrites=spoiler_room_overwrites)
        gmessage = f"{guild} -- Had to recreate channel {name}-spoilers"
        logger.show(gmessage, LOG_CRITICAL)
