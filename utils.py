#!/usr/bin/python

# --
# utils.py: A few common utility functions for the bot
# --

import config_man
import discord
from discord.utils import get

#  Checks if member has the admin role specified in the config. If no admin role is in the config, note that this ALWAYS returns true
def authorize_admin(guild, member):
    role_id = config_man.get_admin_role()  # Try grabbing the admin role from the config, check if it's None
    if role_id is not None:
        role = get(guild.roles, id=int(role_id))

        if role is not None:  # Now try checking if we can grab a role based on this id
            if role in member.roles:  # If the role exists, now see if the member we're checking has this role
                return True  # At this point the user is confirmed to be an admin! Return true!

        else:  # Couldn't turn the role id into the role
            print("\nWarning: Unable to grab the guild's admin role from the role id in the config!\nAdmin commands won't be authorized until you remove the 'admin_role' entry from the config\n")
            return False

    else:  # role_id is none - it probably isn't in the config?
        print("\nWarning: Admin command authorized for a potentially non-admin user - No admin role id is specified in the config!\nRun 'setAdminRole' to set this!\n")
        return True


# Returns a discord.Embed for use in sending status messages
def format_embed(text, is_error):
    return discord.Embed(title=text, colour=0xDB2323 if is_error else 0xFF7D00)
