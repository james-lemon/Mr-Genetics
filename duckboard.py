#!/usr/bin/python

# --
# duckboard.py: Logic/variables related to the duckboard
# --

import config_man
import asyncio
import discord
from discord.utils import get
from discord.ext import commands
import utils

class DuckBoard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_rolelist_messages()

    # Lazy copy and paste of the rolelist.py rolelist message parsing lol
    def update_rolelist_messages(self):
        self.rolelist_messages = {}  # A list of rolelist messages to track, stored as {(channel id, message id), category}
        for category, ids in config_man.categories.items():  # Let's initialize that list with the values stored in each category in the config
            id_list = ids.split(';')
            if id_list[0] != '-1':  # Only add valid category messages to the rolelist messages list: -1 means a category doesn't have a rolelist message
                self.rolelist_messages[(int(id_list[0]), int(id_list[1]))] = category

        for category, ids in config_man.categoriesAlt.items():  # Do the same for the alt rolelist messages
            id_list = ids.split(';')
            if id_list[0] != '-1':
                self.rolelist_messages[(int(id_list[0]), int(id_list[1]))] = category

    # Sets the duckboard channel
    @commands.command()
    async def duckboard(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
            res = config_man.set_duckboard_channel(ctx.channel.id)
            if res:
                await ctx.send(embed=utils.format_embed("This channel is now the duckboard channel!", False))
            else:
                await ctx.send(embed=utils.format_embed("Failed to set the duckboard channel!", True))



    # Sets the number of reactions a message needs to get duckboarded
    @commands.command()
    async def duckboardcount(self, ctx, count: int):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
            res = config_man.set_duckboard_count(count)
            if res:
                await ctx.send(embed=utils.format_embed("Duckboard reaction count set to " + str(count) + "!", False))
            else:
                await ctx.send(embed=utils.format_embed("Failed to set the duckboard reaction count!", True))



    # Called when a reaction is added to a message
    ''' Duckboard is not ready yet, disable it for now
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # First, go through a BUNCH of checks to see if this message is duckboard-eligible
        duckboard_channel = config_man.get_duckboard_channel()
        duckboard_count = int(config_man.get_duckboard_count())
        reacted_channel = reaction.message.channel.id

        print("react")
        if duckboard_channel is None or duckboard_count is None: # Duckboard must be configured
            return

        print("1")
        if reaction.me or not isinstance(reaction.message.channel, discord.TextChannel) or reacted_channel == duckboard_channel: # Bot reactions, duckboard channel reactions, and reactions outside of a guild are not eligible
            return

        print("2")
        for tracked_message in self.rolelist_messages: # Rolelist messages are not eligible
            if reacted_channel == tracked_message[0]:
                return

        # Todo: Don't duckboard messages that've already been posted

        print("3")
        # At this point, we good!
        if reaction.count >= duckboard_count:
            print("4:" + reaction.message.content)

            # Last check: Is this a private channel that's been reacted in?
            channel_overwrites = reaction.message.channel.overwrites_for(reaction.message.guild.default_role)
            embed = discord.Embed(color=0xFF7D00)
            if channel_overwrites.read_messages: # Not a private channel, repost away!
                embed.description = reaction.message.content
                embed.set_author(name=reaction.message.author.display_name, url=reaction.message.jump_url, icon_url=reaction.message.author.display_avatar.url)

            else: # Private channel - don't show message content or author here
                embed.description = "Ah ah ah, you didn't say the magic word~!\n*(message is from a private channel - click the username to view)*"
                embed.set_author(name="The Duck (definitely)", url=reaction.message.jump_url, icon_url=self.bot.user.display_avatar.url)

            embed.set_footer(text="Messages with X reactions are added to the duckboard")
            await self.bot.get_channel(int(duckboard_channel)).send(embed=embed)
    '''