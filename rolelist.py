#!/usr/bin/python

# --
# rolelist.py: Logic/variables related to rolelist assignment
# --

import config_man
import asyncio
import discord
from discord.utils import get
from discord.ext import commands
import utils

class RoleList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rolelist_messages = {}  # A list of rolelist messages to track, stored as {(channel id, message id), category}
        for category, ids in config_man.categories.items():  # Let's initialize that list with the values stored in each category in the config
            id_list = ids.split(';')
            if id_list[0] != '-1':  # Only add valid category messages to the rolelist messages list: -1 means a category doesn't have a rolelist message
                self.rolelist_messages[(int(id_list[0]), int(id_list[1]))] = category

        for category, ids in config_man.categoriesAlt.items():  # Do the same for the alt rolelist messages
            id_list = ids.split(';')
            if id_list[0] != '-1':
                self.rolelist_messages[(int(id_list[0]), int(id_list[1]))] = category
    
        # Temporary tracking variables for the addrole command - Helps persist some data between the command being run and the emoji reaction to confirm it
        self.addrole_message = [0, 0]
        self.addrole_role = ""
        self.addrole_dispname = ""
        self.addrole_description = ""
        self.addrole_category = ""
        self.addrole_editing = False
        self.addrole_assignable = False
    
        # Also track stuff for the removerole command
        self.removerole_message = [0, 0]
        self.removerole_category = ""
        self.removerole_role = ""
    
        # ...and the "setadminrole" command...
        self.setadmin_message = [0, 0]
        self.setadmin_role = ""


    # Adds a role to the config
    # Usage: addrole <category in quotes> <role name in quotes> Role description (no quotes)
    @commands.command()
    async def addrole(self, ctx, category, role: discord.Role, *, desc=""):  # argument: discord.XYZ converts this argument to this data type (i.e. turn a string into a role)
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            roles = config_man.get_roles(category)  # First, let's do some sanity checks:
            if roles is not False:  # A valid dict of roles was returned, run some checks only if this is the case
                if len(roles) >= 20:  # Discord limits reactions to 20 per message (afaik), so prevent adding a 21st role to a category
                    await ctx.send(embed=utils.format_embed("Error: A category can't have more than 20 roles!\nThis is a discord reaction limitation, sorry :(", True))
                    return

                if str(role.id) in roles.keys():  # Prevent having the same role pop up multiple times in the category (probably doesn't break anything tbh, it just sounds dumb)
                    await ctx.send(embed=utils.format_embed("Error: This role is already in this category!", True))
                    return

            if role.id == config_man.get_admin_role():  # Prevent adding the admin role to a category (giving random users your admin role doesn't seem smart)
                await ctx.send(embed=utils.format_embed("Error: " + role.name + " is this bot's config admin role - You cannot add it to the role list!", True))
                return

            permissions = role.permissions
            if permissions.administrator:  # Prevent adding any admin roles for the guild
                await ctx.send(embed=utils.format_embed("Error: " + role.name + " is an admin role in this server - You cannot add it to the role list!", True))
                return

            #global self.addrole_message, self.addrole_role, self.addrole_description, self.addrole_category, self.addrole_dispname, self.addrole_editing, self.addrole_assignable
            embed = discord.Embed(title="Will attempt to add a role", colour=0x4EDB23)
            msg_text = '\n**Role: **' + role.name
            msg_text += '\n**Category: **' + category
            msg_text += '\n**Description: **' + desc
            msg_text += '\n**Assignable: True** - Any user can obtain this role!'
            msg_text += '\n\nTo confirm add: React to this message with the emote to listen for!'
            self.addrole_role = str(role.id)
            self.addrole_dispname = role.name
            self.addrole_category = category
            self.addrole_description = desc
            self.addrole_editing = False
            self.addrole_assignable = True

            # Finally, warn against adding roles with potentially "dangerous" permissions at the bottom of the message
            if permissions.kick_members or permissions.ban_members or permissions.manage_channels or permissions.manage_guild or permissions.manage_messages or permissions.mute_members or permissions.deafen_members:
                msg_text += "\n\n⚠ **Warning: Role " + role.name + " has potentially dangerous permissions.**\nRoles and permissions added to the role list can be obtained by *ANY* user."

            embed.description = msg_text
            msg = await ctx.send(embed=embed)
            self.addrole_message[0] = msg.channel.id
            self.addrole_message[1] = msg.id
            print("Sent addrole message: ", msg.id)
            return


    # Adds a role to the config
    # Usage: addrole <category in quotes> <role name in quotes> Role description (no quotes)
    @commands.command()
    async def adddisprole(self, ctx, category, role: discord.Role, *, desc=""):  # argument: discord.XYZ converts this argument to this data type (i.e. turn a string into a role)
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            roles = config_man.get_roles(category)  # First, let's do some sanity checks:
            if roles is not False:  # A valid dict of roles was returned, run some checks only if this is the case
                if len(roles) >= 20:  # Discord limits reactions to 20 per message (afaik), so prevent adding a 21st role to a category
                    await ctx.send(embed=utils.format_embed("Error: A category can't have more than 20 roles!\nThis is a discord reaction limitation, sorry :(", True))
                    return

                if str(role.id) in roles.keys():  # Prevent having the same role pop up multiple times in the category (probably doesn't break anything tbh, it just sounds dumb)
                    await ctx.send(embed=utils.format_embed("Error: This role is already in this category!", True))
                    return

            #global self.addrole_message, self.addrole_role, self.addrole_description, self.addrole_category, self.addrole_dispname, self.addrole_editing, self.addrole_assignable
            embed = discord.Embed(title="Will attempt to add a display role", colour=0x4EDB23)
            msg_text = '\n**Role: **' + role.name
            msg_text += '\n**Category: **' + category
            msg_text += '\n**Description: **' + desc
            msg_text += '\n**Assignable: False**'
            msg_text += '\n\nTo confirm add: React with 🛡 to confirm!'
            self.addrole_role = str(role.id)
            self.addrole_dispname = role.name
            self.addrole_category = category
            self.addrole_description = desc
            self.addrole_editing = False
            self.addrole_assignable = False

            embed.description = msg_text
            msg = await ctx.send(embed=embed)
            self.addrole_message[0] = msg.channel.id
            self.addrole_message[1] = msg.id
            await msg.add_reaction('🛡')
            print("Sent adddisprole message: ", msg.id)
            return


    # Edits a role in the config
    @commands.command()
    async def editrole(self, ctx, category, role: discord.Role, *, desc=""):  # argument: discord.XYZ converts this argument to this data type (i.e. turn a string into a role)
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            roles = config_man.get_roles(category)  # First, let's do some sanity checks:
            if roles is False:  # Confirm that our role list is valid (if it's false, the category is invalid)
                await ctx.send(embed=utils.format_embed("Error getting roles for category \"" + category + "\" - does this category exist?", True))
                return

            if str(role.id) not in roles.keys():  # If our role list is correct, make sure the role we want to edit is valid, too
                await ctx.send(embed=utils.format_embed("Error: Role \"" + role.name + "\" not found in category \"" + category + "\"!", True))
                return

            #global self.addrole_message, self.addrole_role, self.addrole_description, self.addrole_category, self.addrole_dispname, self.addrole_editing, self.addrole_assignable
            self.addrole_assignable = config_man.is_role_assignable(category, role.id)
            embed = discord.Embed(title="Will attempt to edit a role", colour=0x4EDB23)
            msg_text = '\n**Role: **' + role.name
            msg_text += '\n**Category: **' + category
            msg_text += '\n**Description: **' + desc
            msg_text += '\n**Assignable: **' + str(self.addrole_assignable)
            msg_text += '\n\nRole will be removed and re-added with these values.'
            msg_text += '\nTo confirm: React to this message with ' + ('the emote to listen for!' if self.addrole_assignable else '🛡!')
            self.addrole_role = str(role.id)
            self.addrole_dispname = role.name
            self.addrole_category = category
            self.addrole_description = desc
            self.addrole_editing = True

            embed.description = msg_text
            msg = await ctx.send(embed=embed)
            self.addrole_message[0] = msg.channel.id
            self.addrole_message[1] = msg.id
            if not self.addrole_assignable:
                await msg.add_reaction('🛡')
            print("Sent editrole message: ", msg.id)
            return


    # Removes a role from the config
    # Usage: removerole <role category in quotes> <role name in quotes>
    @commands.command()
    async def removerole(self, ctx, category, role: discord.Role):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            #global self.removerole_message, self.removerole_category, self.removerole_role
            role_list = config_man.get_roles(category)
            if role_list is False:  # Sanity check we're being given a valid category
                await ctx.send(embed=utils.format_embed("Error: Category " + category + " not found!", True))
                return

            embed = discord.Embed(title="Will attempt to remove a role", colour=0xDB2323)
            msg_text = '\n**Category:** ' + category
            msg_text += '\n**Role: **' + role.name
            if len(role_list) <= 1:  # If this is the only role in the category, the category will be removed as well
                msg_text += '\n**This category will be empty (and thus removed) if this role is removed. It\'s rolelist message will be deleted if it exists, too.**'
            msg_text += '\n\nTo confirm removal: React with ❌'
            self.removerole_category = category
            self.removerole_role = str(role.id)

            embed.description = msg_text
            msg = await ctx.send(embed=embed)
            self.removerole_message[0] = msg.channel.id
            self.removerole_message[1] = msg.id
            await msg.add_reaction('❌')
            print("Sent removerole message: ", msg.id)
            return


    # Generates a role list, either deleting the old messages and sending new ones or updating the existing messages
    async def generateRoleList(self, ctx, sendNew):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Confirm that it's a member (of a guild) we're being given, and then authorize them as an admin
            if not config_man.categories:  # Are no categories loaded?
                await ctx.send(embed=utils.format_embed("No role categories to display found! Add some roles to the rolelist with !addrole or !adddisprole.", True))
                return

            #global self.rolelist_messages

            if sendNew:  # Generating a new role list? Delete the old messages we're tracking first
                # First, delete all the old rolelist messages we're tracking (if any) and clear the list of messages to track
                for message in self.rolelist_messages.keys():
                    # print(message)
                    try:
                        msg = await self.bot.get_channel(message[0]).fetch_message(message[1])
                        await msg.delete()
                    except discord.errors.NotFound:
                        print("Received 404 trying to delete message with ID " + str(
                            message[1]) + ", was it already deleted?")
                self.rolelist_messages.clear()

            categorydescriptions = config_man.get_category_descriptions()
            for category, ids in config_man.categories.items():  # Send a rolelist message for each category
                embed = discord.Embed(title=category, colour=0xFF7D00)  # Create an embed, set it's title and color
                msg_text = categorydescriptions[category] if categorydescriptions[category] is not None else "React with these emotes to get roles!"  # Grab this category's description from the config (if there is one), otherwise use some placeholder text
                msg_text += "\n"
                emojis = config_man.get_roles_emoji(category)
                for role_id, desc in config_man.get_roles(category).items():  # Grab the roles from this category, and add their name/descriptions to the message to send
                    role = get(ctx.guild.roles, id=int(role_id))
                    msg_text += "\n "

                    if config_man.is_role_assignable(category, role_id):  # Is this role assignable? If so, add its emote!
                        if emojis[role_id][1] == 'True':  # Custom emoji - Find emoji in guild and then insert it
                            msg_text += str(get(ctx.guild.emojis, name=emojis[role_id][0]))
                        else:  # Unicode emoji - Print emoji normally (since it's just stored as a unicode string)
                            msg_text += emojis[role_id][0]

                    if desc == '':
                        msg_text += "  **" + role.name + "**"
                    else:
                        msg_text += "  **" + role.name + "** - " + desc

                embed.description = msg_text  # Set the embed's description to our role list text

                msg = None
                updated_msg = False
                if not sendNew:  # Hol up, if we want to update the existing lists, check if this category already has a message
                    id_list = ids.split(';')
                    if id_list[0] != '-1' and id_list[1] != '-1':  # There's *probably* a valid message to update?
                        msg = await self.bot.get_channel(int(id_list[0])).fetch_message(int(id_list[1]))
                        await msg.edit(embed=embed)
                        print("Edited existing role list message for \"" + category + "\": ", msg.id)
                        updated_msg = True

                if not updated_msg:  # Wasn't able to edit an existing category message? That's cool just send a new one
                    msg = await ctx.send(embed=embed)
                    print("Sent role new list message for \"" + category + "\": ", msg.id)

                self.rolelist_messages[(msg.channel.id, msg.id)] = category  # Store this message's channel/message IDs for later - We'll use them to track these messages for reactions
                config_man.set_category_message(category, str(msg.channel.id), str(msg.id))  # Also save these values to the config as well

                cur_emoji_list = []
                if updated_msg:  # If we're updated an existing message, check if we should remove any (of our) reactions for roles that no longer exist:
                    new_emoji_list = []

                    for item in emojis.values():  # First, grab a list of all the emojis associated with roles in this category
                        new_emoji_list.append(item[0])

                    for reaction in msg.reactions:  # Now go through all of this message's reactions
                        if isinstance(reaction.emoji, discord.Emoji) or isinstance(reaction.emoji, discord.PartialEmoji):
                            emote = reaction.emoji.name
                        else:  # We're probably being given a unicode string as an emoji???
                            emote = reaction.emoji

                        if reaction.me:
                            if emote not in new_emoji_list:  # If we've used this reaction and that reaction no longer belongs to a role, remove our reaction to it!
                                await reaction.remove(self.bot.user)
                                await asyncio.sleep(0.5)
                            else:  # We've used this reaction and it does belong to a role, add it to the list of reactions we currently have
                                cur_emoji_list.append(emote)

                for role, emoji in emojis.items():  # React with the emotes for all assignable roles in this category

                    # Add this emote as a reaction if this role is assignable AND EITHER:
                    #    - We're sending a new role list OR
                    #    - We're updating a role list and we haven't reacted with this emote yet (it isn't in cur_emoji)list)
                    if config_man.is_role_assignable(category, role) and (not updated_msg or (updated_msg and emoji[0] not in cur_emoji_list)):
                        await asyncio.sleep(0.5)  # Wait a bit to appease rate limits (discordpy apparently does some stuff internally too, this prolly can't hurt tho
                        if emoji[1] == 'True':  # This is a custom emoji, grab an emoji instance before use
                            await msg.add_reaction(get(ctx.guild.emojis, name=emoji[0]))
                        else:  # No fancy emoji conversion needed otherwise, unicode emojis can be passed into add_reaction as-is
                            await msg.add_reaction(emoji[0])

                await asyncio.sleep(1)  # *bows down to discord api*

            config_man.save_config()  # We've updated some entries in the config for message IDs to listen for reactions on, don't forget to save these!
            return


    # Updates the "role list" messages if they exist - Users can react to these messages for roles assignments
    # Usage: rolelist
    @commands.command()
    async def rolelist(self, ctx):
        await RoleList.generateRoleList(self, ctx, False)


    # Sends new "role list" messages, deleting old ones in the process
    @commands.command()
    async def newrolelist(self, ctx):
        await RoleList.generateRoleList(self, ctx, True)


    # Sorts the roles in a category by alphabetical order
    @commands.command()
    async def sortcategory(self, ctx, category):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
            msg = config_man.sort_category(category)
            await ctx.send(embed=utils.format_embed(msg, False))


    # Sets the description of a category
    @commands.command()
    async def setcategorydescription(self, ctx, category, *, description=""):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
            msg = config_man.set_category_description(category, description)
            await ctx.send(embed=utils.format_embed(msg, False))

    # Sets the alt rolelist message for a role
    @commands.command()
    async def altrolemsg(self, ctx, category, role: discord.Role, msgid):
            if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command

                # Check to make sure the specified message exists
                msg = str(msgid).split("-")
                if len(msg) != 2:
                    await ctx.send(embed=utils.format_embed("Invalid Message ID specified!\nMake sure you use `Shift + Hover Message -> Copy ID` to get the ID.", True))
                    return
                print("Specified channel: " + msg[0] + ", message: " + msg[1])
                try:
                    message = await self.bot.get_channel(int(msg[0])).fetch_message(int(msg[1]))
                    assert message is not None
                except discord.errors.NotFound:
                    print("Received 404 trying to find message with ID " + str(msgid))
                    await ctx.send(embed=utils.format_embed("Error getting the specified message ID!\nMake sure you use `Shift + Hover Message -> Copy ID` to get the ID.", True))
                    return

                # The message should exist at this point, add a reaction to it and set it as the category's alt message
                duck_emote = str(get(ctx.guild.emojis, name="discoduck"))
                if duck_emote == "None":
                    duck_emote = "🦆"
                await message.add_reaction(duck_emote)

                ret = config_man.set_category_alt_message(category, msg[0], msg[1], role)
                await ctx.send(embed=utils.format_embed(ret, False))


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await RoleList.handle_reaction(self, payload, True)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await RoleList.handle_reaction(self, payload, False)


    # If any of the rolelist messages are reacted to, this routine checks if the reacted emote is a role emote, and updates user roles if needed
    async def process_rolelist_reaction(self, payload, guild, category, roles, reaction_added, member):
        for role_id, role_emoji in roles.items():  # Now find the role to add - Go through each role until we find the one with the emoji the member reacted with
            # print(payload.emoji.name, ", ", role_emoji)
            if payload.emoji.name == role_emoji[0]:  # Once we find it, toggle this role on the user!
                role = get(guild.roles, id=int(role_id))

                if config_man.is_role_assignable(category, str(role.id)):  # Check to make sure we are allowed to assign this role to regular users!
                    if not reaction_added:  # Member removed this reaction, take the role away!
                        print("Removing role " + role.name + " from member " + member.display_name)
                        await member.remove_roles(role, reason="Self-removed via bot (by reaction)")
                        # print("Removed role")
                    else:  # Member added the reaction, add the role!
                        print("Adding role " + role.name + " to member " + member.display_name)
                        await member.add_roles(role, reason="Self-assigned via bot (by reaction)")
                        # print("Added role ")
                    return True  # Done adding this role, don't process anything else
        return False


    # Handles the add and remove reaction events for ALL messages on servers the bot is in
    async def handle_reaction(self, payload, reaction_added):
        if payload.user_id == self.bot.user.id or payload.guild_id is None:  # Don't process reactions we've added ourselves or aren't in a guild (probably in DMs?)
            return
        #global self.addrole_message, self.addrole_role, self.addrole_description, self.addrole_category, self.addrole_dispname, self.addrole_editing, self.addrole_assignable, self.removerole_message, self.removerole_category, self.removerole_role, self.setadmin_message, self.setadmin_role

        guild = self.bot.get_guild(payload.guild_id)  # Grab the guild we're in and the member that reacted for later
        member = guild.get_member(payload.user_id)

        # Reaction processing 1: ROLELIST MESSAGES (available to all server users)
        for tracked_message in self.rolelist_messages:
            if payload.channel_id == tracked_message[0] and payload.message_id == tracked_message[1]:  # Only process messages that we are listening for reactions on. Here, we'll process reactions on the role list messages
                # print("\nRolelist reaction!\nUser: ", payload.user_id, "\nChannel: ", payload.channel_id, "\nMessage: ", payload.message_id, "\nEmoji: ", payload.emoji.name, "\nEvent: ", payload.event_type)

                for category, category_message in config_man.categories.items():  # Next, let's find the category of the message we just reacted to:
                    category_ids = category_message.split(';')
                    if payload.channel_id == int(category_ids[0]) and payload.message_id == int(category_ids[1]):  # Did we find the category?
                        roles = config_man.get_roles_emoji(category)  # Grab the roles in the category message the member reacted on
                        if await RoleList.process_rolelist_reaction(self, payload, guild, category, roles, reaction_added, member):  # Try checking if the reacted emote belongs to a role, if it does update the user and return
                            return

                print("lol")
                for category, category_message in config_man.categoriesAlt.items():  # Finally, see if the message we reacted to was in our list of ALT category messages
                    print(category + ", " + category_message)
                    category_ids = category_message.split(';')
                    if payload.channel_id == int(category_ids[0]) and payload.message_id == int(category_ids[1]):  # Did we find the category?
                        print("Found alt message")
                        roles = config_man.get_alt_role_emoji(category)  # Grab the roles in the category message the member reacted on
                        print(roles)
                        if await RoleList.process_rolelist_reaction(self, payload, guild, category, roles, reaction_added, member):  # Try checking if the reacted emote belongs to a role, if it does update the user and return
                            return


        # Reaction processing 2: Add/remove role reactions - Only available to admins!
        if utils.authorize_admin(guild, member):
            if payload.channel_id == self.addrole_message[0] and payload.message_id == self.addrole_message[1]:  # Check for reactions on the latest "addrole" message
                print("\nAdd/edit role reaction!\nID: ", payload.message_id, "Emoji: ", payload.emoji.name)

                if self.addrole_assignable:  # Run some sanity checks depending on whether we're adding an assignable role or not
                    if payload.emoji.is_custom_emoji():  # Using a custom emoji? Make sure the bot can actually use it, too
                        emoji = get(guild.emojis, id=payload.emoji.id)
                        if emoji is None or emoji.available is False:
                            await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed("Error: I can't use that custom emoji, try reacting with a different emote.", True))
                            return

                else:  # Not an assignable role, only process if the added reaction is the confirmation shield
                    if payload.emoji.name != '🛡' and payload.emoji.name != '🛡️':  # wth why are there two shields???
                        return

                if self.addrole_editing:  # If we're editing a role, we want to remove the existing role before we add a new one with the new parameters
                    remove_result = config_man.remove_role(self.addrole_category, self.addrole_role)
                    if remove_result is False:
                        await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed("Role edit macro failed!\n" + remove_result, True))
                        self.addrole_message = [0, 0]
                        return

                add_result = config_man.add_role(self.addrole_category, self.addrole_role, self.addrole_dispname, payload.emoji.name, self.addrole_description, payload.emoji.is_custom_emoji(), self.addrole_assignable)
                if add_result is True:
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.add_reaction('\N{THUMBS UP SIGN}')
                else:
                    await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed(add_result, True))
                self.addrole_message = [0, 0]  # Don't forget to blank out the addrole message so we stop listening for reactions on the message we just reacted on!

            if payload.channel_id == self.removerole_message[0] and payload.message_id == self.removerole_message[1] and payload.emoji.name == '❌':  # Check for reactions on the latest "removerole" message
                remove_result = config_man.remove_role(self.removerole_category, self.removerole_role)
                if remove_result is True or isinstance(remove_result, list):
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.add_reaction('\N{THUMBS UP SIGN}')

                    if isinstance(remove_result, list) and remove_result[0] != -1:  # If we got returned a list, it means this category is now empty. If list[0] isn't -1, it means we should delete the old rolelist message for that category, too
                        msg = await self.bot.get_channel(remove_result[0]).fetch_message(remove_result[1])
                        await msg.delete()
                        await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed("This category is now empty! Removed category and deleted its role list message", False))

                else:
                    await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed(remove_result, True))
                self.removerole_message = [0, 0]  # Don't forget to blank out the removerole message so we stop listening for reactions on the message we just reacted on!

            if payload.channel_id == self.setadmin_message[0] and payload.message_id == self.setadmin_message[1] and payload.emoji.name == '🔒':  # Check for reactions on the latest "setadminrole" message
                print("Reaction: setadmin message match")
                set_result = config_man.set_admin_role(self.setadmin_role)
                if set_result is True:
                    msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
                    await msg.add_reaction('\N{THUMBS UP SIGN}')
                else:
                    await self.bot.get_channel(payload.channel_id).send(embed=utils.format_embed(set_result, True))
                self.setadmin_message = [0, 0]  # Don't forget to blank out the addrole message so we stop listening for reactions on the message we just reacted on!


        # Endif: Admin auth
