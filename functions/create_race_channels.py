import discord
from discord.utils import get
from functions.constants import LOG_CRITICAL

async def create_race_channels(guild, creator, name, logger):
    race_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        creator: discord.PermissionOverwrite(read_messages=True)
    }

    spoiler_room_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }

    cat = get(guild.categories, name="Racing")

    if not name in [r.name for r in guild.channels]:
        channel = await guild.create_text_channel(name, category=cat, overwrites=race_room_overwrites)
        gmessage = f"{guild} -- Had to recreate channel {name}"
        logger.show(gmessage, LOG_CRITICAL)

        r_create_msg = f"You can use the following commands:`\n"
        r_create_msg += f"    !raceinfo  - See information about this race\n"
        r_create_msg += f"    !entrants  - Shows the entrants for this race\n"
        r_create_msg += f"    !ready     - Mark yourself ready\n"
        r_create_msg += f"    !unready   - Mark yourself unready\n"
        r_create_msg += f"    !getseed   - DMs you a link to download the seed for this race\n"
        r_create_msg += f"    !setseed   - If you're a race admin, use this to set the URL for the race seed\n"
        r_create_msg += f"    !startrace - Start the race\n"
        r_create_msg += f"    !done      - Mark that you are done\n"
        r_create_msg += f"    !finishrace - Close this raceroom after a brief delay\n"
        r_create_msg += f"`\n"
        infopost = await channel.send(r_create_msg)
        await infopost.pin()

    if not name + "-spoilers" in [r.name for r in guild.channels]:
        await guild.create_text_channel(name + "-spoilers", category=cat, overwrites=spoiler_room_overwrites)
        gmessage = f"{guild} -- Had to recreate channel {name}-spoilers"
        logger.show(gmessage, LOG_CRITICAL)
