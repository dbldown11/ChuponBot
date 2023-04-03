import discord
import ast
from functions.botconfig import config, env

def isAdmin(user: discord.Member) -> bool:
    guild = user.guild
    admin_roles = ast.literal_eval(config.get(env,"admin_roles"))
    for role in admin_roles:
        admin_role = discord.utils.get(guild.roles, name=role)
        if admin_role in user.roles:
            return True
    return False