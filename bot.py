#!/usr/bin/python

import asyncio
import discord
from discord.ext import commands
from discord.utils import get

import config_man
import playing_messages

# client = discord.Client()
bot = commands.Bot(command_prefix='!', case_insensitive=True)

bot.remove_command('help')  # Remove the default help command, imma make my own lel

rolelist_messages = {}  # A list of rolelist messages to track, stored as {(channel id, message id), category}
for category, ids in config_man.categories.items():  # Let's initialize that list with the values stored in each category in the config
    id_list = ids.split(';')
    if id_list[0] != '-1':  # Only add valid category messages to the rolelist messages list: -1 means a category doesn't have a rolelist message
        rolelist_messages[(int(id_list[0]), int(id_list[1]))] = category

# Temporary tracking variables for the addrole command - Helps persist some data between the command being run and the emoji reaction to confirm it
addrole_message = [0, 0]
addrole_role = ""
addrole_dispname = ""
addrole_description = ""
addrole_category = ""

# Also track stuff for the removerole command
removerole_message = [0, 0]
removerole_category = ""
removerole_role = ""

# ...and the "setadminrole" command...
setadmin_message = [0, 0]
setadmin_role = ""

debug_emoji = None

@bot.event
async def on_ready():
    global admin_role
    print('Logged on as ', bot.user)
    bot.loop.create_task(change_status())  # Also start the "change status every so often" task, too


# Argument test commands
#@bot.command()
#async def hoi(ctx, arg): # Interprets first "arg" (up to first space)
#    await ctx.send('Bruh, ' + arg)


#@bot.command()
#async def boi(ctx, *, arg): # Interprets all remaining arguments as one ("keyword-only")
#    await ctx.send('Bruv, ' + arg)


# Adds a role to the config
# Usage: addrole <category in quotes> <role name in quotes> Role description (no quotes)
@bot.command()
async def addrole(ctx, category, role: discord.Role, *, desc=""): # argument: discord.XYZ converts this argument to this data type (i.e. turn a string into a role)
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
        roles = config_man.get_roles(category)  # First, let's do some sanity checks:
        if roles is not False:  # A valid dict of roles was returned, run some checks only if this is the case
            if len(roles) >= 20:  # Discord limits reactions to 20 per message (afaik), so prevent adding a 21st role to a category
                await ctx.send("Error: A category can't have more than 20 roles!\nThis is a discord reaction limitation, sorry :(")
                return

            if str(role.id) in roles.keys():  # Prevent having the same role pop up multiple times in the category (probably doesn't break anything tbh, it just sounds dumb)
                await ctx.send("Error: This role is already in this category!")
                return

        if role.id == config_man.get_admin_role():  # Prevent adding the admin role to a category (giving random users your admin role doesn't seem smart)
            await ctx.send("Error: " + role.name + " is this bot's config admin role - You cannot add it to the role list!")
            return

        permissions = role.permissions
        if permissions.administrator:  # Prevent adding any admin roles for the guild
            await ctx.send("Error: " + role.name + " is an admin role in this guild - You cannot add it to the role list!")
            return

        global addrole_message, addrole_role, addrole_description, addrole_category, addrole_dispname
        msg_text = 'Will attempt to add a role entry:'
        msg_text += '\nRole: ' + role.name + " (id " + str(role.id) + ")"
        msg_text += '\nCategory: ' + category
        msg_text += '\nDesc: ' + desc
        msg_text += '\n\nTo confirm add: React to this message with the emote to listen for!'
        addrole_role = str(role.id)
        addrole_dispname = role.name
        addrole_category = category
        addrole_description = desc

        # Finally, warn against adding roles with potentially "dangerous" permissions at the bottom of the message
        if permissions.kick_members or permissions.ban_members or permissions.manage_channels or permissions.manage_guild or permissions.manage_messages or permissions.mute_members or permissions.deafen_members:
            msg_text += "\n\n⚠ **Warning: Role " + role.name + " has potentially dangerous permissions.**\nRoles and permissions added to the role list can be obtained by *ANY* user."

        msg = await ctx.send(msg_text)
        addrole_message[0] = msg.channel.id
        addrole_message[1] = msg.id
        print("Sent addrole message: ", msg.id)
        return


# Removes a role from the config
# Usage: removerole <role category in quotes> <role name in quotes>
@bot.command()
async def removerole(ctx, category, role: discord.Role):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
        global removerole_message, removerole_category, removerole_role
        msg_text = 'Will attempt to remove a role entry:'
        msg_text += '\nCategory: ' + category
        msg_text += '\nRole: ' + role.name
        msg_text += '\n\nTo confirm removal: React with ❌'
        removerole_category = category
        removerole_role = str(role.id)

        msg = await ctx.send(msg_text)
        removerole_message[0] = msg.channel.id
        removerole_message[1] = msg.id
        await msg.add_reaction('❌')
        print("Sent removerole message: ", msg.id)
        return



# Sends the "role list" messages - Users can react to these messages for roles assignments
# Usage: rolelist
@bot.command()
async def rolelist(ctx):  # Sends the "role list" messages, which can be reacted to for role assignments
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            global debug_emoji, rolelist_messages

            # First, delete all the old rolelist messages we're tracking (if any) and clear the list of messages to track
            for message in rolelist_messages.keys():
                print(message)
                try:
                    msg = await bot.get_channel(message[0]).fetch_message(message[1])
                    await msg.delete()
                except discord.errors.NotFound:
                    print("Received 404 trying to delete message with ID " + str(message[1]) + ", was it already deleted?")
            rolelist_messages.clear()

            for category, ids in config_man.categories.items():  # Send a rolelist message for each category
                msg_text = "> **" + category + "**\nReact with the following emotes to get roles!\n"
                emojis = config_man.get_roles_emoji(category)
                for role_id, desc in config_man.get_roles(category).items():  # Grab the roles from this category, and add their name/descriptions to the message to send
                    role = get(ctx.guild.roles, id=int(role_id))
                    msg_text += "\n "
                    if emojis[role_id][1] == 'True':  # Custom emoji - Find emoji in guild and then insert it
                        msg_text += str(get(ctx.guild.emojis, name=emojis[role_id][0]))
                    else:  # Unicode emoji - Print emoji normally (since it's just stored as a unicode string)
                        msg_text += emojis[role_id][0]
                    msg_text += "  **" + role.name + "** - " + desc

                msg = await ctx.send(msg_text)
                print("Sent role list message: ", msg.id)
                rolelist_messages[(msg.channel.id, msg.id)] = category  # Store this message's channel/message IDs for later - We'll use them to track these messages for reactions
                config_man.set_category_message(category, str(msg.channel.id), str(msg.id))  # Also save these values to the config as well
                for emoji in emojis.values():
                    await asyncio.sleep(0.5)  # Wait a bit to appease rate limits (discordpy apparently does some stuff internally too, this prolly can't hurt tho
                    if emoji[1] == 'True':  # This is a custom emoji, grab an emoji instance before use
                        await msg.add_reaction(get(ctx.guild.emojis, name=emoji[0]))
                    else:  # No fancy emoji conversion needed otherwise, unicode emojis can be passed into add_reaction as-is
                        await msg.add_reaction(emoji[0])

                await asyncio.sleep(1)  # *bows down to discord api*

            config_man.save_config()  # We've updated some entries in the config for message IDs to listen for reactions on, don't forget to save these!
            return


# Sets the admin role in the config
@bot.command()
async def setadminrole(ctx, role: discord.Role):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        global setadmin_message, setadmin_role
        if role is not None:
            msg = await ctx.send("Will set the admin role as: " + role.name + "\nUsers without this role can't edit or send the role list, and can only react to it for roles.\n\n**Ensure you have this role and react with 🔒 to confirm this!**")
            setadmin_message[0] = msg.channel.id
            setadmin_message[1] = msg.id
            setadmin_role = str(role.id)
            await msg.add_reaction('🔒')
            print("Sent setadminrole message: ", msg.id)
        else:
            await ctx.send("Invalid role given!")


# Sorts the roles in a category by alphabetical order
@bot.command()
async def sortcategory(ctx, category):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        msg = config_man.sort_category(category)
        await ctx.send(msg)


# A help command that DMs the sender with command info
@bot.command()
async def help(ctx):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        await ctx.author.send("> **Command Help**\n" +
                              "```help: Get sent this list\n" +
                              "addrole \"Category\" \"Role\" Description:  Adds a role to the role list\n" +
                              "removerole \"Category\" \"Role\":  Removes a role from the role list\n" +
                              "rolelist:  Prints the role list to the current channel\n" +
                              "setadminrole \"Role\":  Sets a role as this bot's \"admin\" role\n" +
                              "sortcategory \"Category\":  Sorts the roles in a category (alphabetical order)\n\n"
                              "Note:  If an admin role is set, you'll need that role to run ANY commands!```")
        await ctx.send("DM'd ya fam 😉")


@bot.event
async def on_raw_reaction_add(payload):
    await handle_reaction(payload)


@bot.event
async def on_raw_reaction_remove(payload):
    await handle_reaction(payload)


# Handles the add and remove reaction events for ALL messages on servers the bot is in
async def handle_reaction(payload):
    if payload.user_id == bot.user.id or payload.guild_id is None:  # Don't process reactions we've added ourselves or aren't in a guild (probably in DMs?)
        return
    global debug_emoji, addrole_message, addrole_role, addrole_description, addrole_category, addrole_dispname, removerole_message, removerole_category, removerole_role, setadmin_message, setadmin_role

    guild = bot.get_guild(payload.guild_id)  # Grab the guild we're in and the member that reacted for later
    member = guild.get_member(payload.user_id)

    # Reaction processing 1: ROLELIST MESSAGES (available to all server users)
    for tracked_message in rolelist_messages:
        if payload.channel_id == tracked_message[0] and payload.message_id == tracked_message[1]:  # Only process messages that we are listening for reactions on. Here, we'll process reactions on the role list messages
            # print("\nRolelist reaction!\nUser: ", payload.user_id, "\nChannel: ", payload.channel_id, "\nMessage: ", payload.message_id, "\nEmoji: ", payload.emoji.name, "\nEvent: ", payload.event_type)

            for category, category_message in config_man.categories.items():  # Next, let's find the category of the message we just reacted to:
                category_ids = category_message.split(';')
                if payload.channel_id == int(category_ids[0]) and payload.message_id == int(category_ids[1]):  # Did we find the category?
                    roles = config_man.get_roles_emoji(category)  # Grab the roles in the category message the member reacted on

                    for role_id, role_emoji in roles.items():  # Now find the role to add - Go through each role until we find the one with the emoji the member reacted with
                        # print(payload.emoji.name, ", ", role_emoji)
                        if payload.emoji.name == role_emoji[0]:  # Once we find it, toggle this role on the user!
                            role = get(guild.roles, id=int(role_id))

                            if role in member.roles:  # Member already has this role, take it away!
                                print("Removing role " + role.name + " from member " + member.display_name)
                                await member.remove_roles(role, reason="Self-removed via bot (by reaction)")
                            else:  # Member doesn't have the role, add it!
                                print("Adding role " + role.name + " to member " + member.display_name)
                                await member.add_roles(role, reason="Self-assigned via bot (by reaction)")
                            return  # Done adding this role, don't process anything else

    # Reaction processing 2: Add/remove role reactions - Only available to admins!
    if authorize_admin(guild, member):
        if payload.channel_id == addrole_message[0] and payload.message_id == addrole_message[1]:  # Check for reactions on the latest "addrole" message
            debug_emoji = payload.emoji
            print("\nAddrole reaction!\nID: ", payload.message_id, "Emoji: ", payload.emoji.name)

            if payload.emoji.is_custom_emoji():  # Using a custom emoji? Make sure the bot can actually use it, too
                emoji = get(guild.emojis, id=payload.emoji.id)
                print(emoji)
                if emoji is None or emoji.available is False:
                    await bot.get_channel(payload.channel_id).send("Error: I can't use that custom emoji, try reacting with a different emote!")
                    return

            add_result = config_man.add_role(addrole_category, addrole_role, addrole_dispname, payload.emoji.name, addrole_description, payload.emoji.is_custom_emoji())
            if add_result is True:
                msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await msg.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await bot.get_channel(payload.channel_id).send(add_result)
            addrole_message = [0, 0]  # Don't forget to blank out the addrole message so we stop listening for reactions on the message we just reacted on!

        if payload.channel_id == removerole_message[0] and payload.message_id == removerole_message[1] and payload.emoji.name == '❌':  # Check for reactions on the latest "removerole" message
            remove_result = config_man.remove_role(removerole_category, removerole_role)
            if remove_result is True:
                msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await msg.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await bot.get_channel(payload.channel_id).send(remove_result)
            removerole_message = [0, 0]  # Don't forget to blank out the removerole message so we stop listening for reactions on the message we just reacted on!

        if payload.channel_id == setadmin_message[0] and payload.message_id == setadmin_message[1] and payload.emoji.name == '🔒':  # Check for reactions on the latest "setadminrole" message
            set_result = config_man.set_admin_role(setadmin_role)
            if set_result is True:
                msg = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                await msg.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await bot.get_channel(payload.channel_id).send(set_result)
            setadmin_message = [0, 0]  # Don't forget to blank out the addrole message so we stop listening for reactions on the message we just reacted on!


    # Endif: Admin auth


@bot.event
async def on_command_error(ctx, error):
    if isinstance(ctx.author, discord.Member) and authorize_admin(ctx.guild, ctx.author):  # Invalid commands run by non-admins can still display error messages - Prevent that here
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing arguments!')
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send('Bad argument given!')
            return
        raise error


# Checks if member has the admin role specified in the config. If no admin role is in the config, note that this ALWAYS returns true
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


# Change the "playing" message every 6 hours (4 changes a day)
async def change_status():
    while True:
        await bot.change_presence(activity=discord.Game(playing_messages.get_status()))
        await asyncio.sleep(21600)  # 60 seconds * 60 minutes * 6 hours

# Now to actually run the bot:
secret = open("secret-token.txt", "r").read(59)  # Load our spooper secret token from file
if len(secret) == 59:  # Basic length check for invalid secrets (are secrets always 59 characters lnog???? I DUNNO BRUH!!!1!
    bot.run(secret)
else:
    print("Invalid secret? Place this bot's access token in secret-token.txt to run!")
