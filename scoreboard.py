#!/usr/bin/python

# --
# scoreboard.py: Logic/variables related to the scoreboard feature
# --

import config_man
import scoreboard_config_man
import asyncio
from random import randrange
import discord
from discord.utils import get
from discord.ext import commands
import utils


class Scoreboard(commands.Cog):
    score_messages = (  # Random messages to display on score submission
        "Good luck on the win!",
        "Go for the gold!",
        "Ganbare!",
        "***Do it!!!***",
        "Yo! Tear it up!",
        "Your scores are on FIRE!",
        "Can I call you a dancin' MASTER?",
        "Wow, your steps are AMAZIN'!",
    )

    def __init__(self, bot):
        self.bot = bot
        self.sc_config = scoreboard_config_man.ScoreboardConfig()

        self.scfield_emote = None

        default_scoreboard = config_man.get_default_scoreboard()
        if default_scoreboard is not None:
            print("Default scoreboard " + default_scoreboard + " is saved, attempting load...")
            self.sc_config.load_sc_config(default_scoreboard, False)

    # Tries loading a scoreboard config file
    @commands.command()
    async def scload(self, ctx, name):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            self.sc_config.save_sc_config() #Don't nuke ur data kids, triple-check that you've saved to disk before loading a new config
            loaded = self.sc_config.load_sc_config(name, False)
            if loaded == 0:
                await ctx.send(embed=utils.format_embed("Loaded scoreboard " + name, False))
                config_man.set_default_scoreboard(name)
            else:
                await ctx.send(embed=utils.format_embed("Error: Scoreboard config not found: " + name, True))



    # Tries making a new scoreboard config file
    @commands.command()
    async def scnew(self, ctx, name, *, description=""):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            self.sc_config.save_sc_config()  # Don't nuke ur data kids, triple-check that you've saved to disk before loading a new config
            #sc_config.sc_config_exists(name) # Not yet
            loaded = self.sc_config.load_sc_config(name, True, description)
            if loaded == 0:
                await ctx.send(embed=utils.format_embed("Loaded scoreboard " + name + " - this really shouldn't happen :sweat_smile:", False))
                config_man.set_default_scoreboard(name)
            elif loaded == 1:
                await ctx.send(embed=utils.format_embed("Created new scoreboard " + name, False))
                config_man.set_default_scoreboard(name)
            else:
                await ctx.send(embed=utils.format_embed("Error: Scoreboard config not found: " + name, True))



    # Sets the scoreboard's display name
    @commands.command()
    async def scdisplayname(self, ctx, *, name):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            self.sc_config.set_disp_name(name)
            await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard, BOI
            await ctx.send(embed=utils.format_embed("Set scoreboard display name to " + name, False))



    # Sets the scoreboard's description
    @commands.command()
    async def scdescription(self, ctx, *, desc):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            self.sc_config.set_desc(desc)
            await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard, BOI
            await ctx.send(embed=utils.format_embed("Set scoreboard description to " + desc, False))



    # Creates or updates a scoreboard field
    @commands.command()
    async def scfield(self, ctx, name, type):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            type = 0  # Todo: We only support one field type for now, so enforce it here
            ftype = self.sc_config.parse_field_type(type)
            if ftype is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid field type \"" + type + "\"!", True))
                return

            fields = self.sc_config.get_fields()
            if name in fields.keys():
                print("Field " + name + " exists")
                embed = discord.Embed(title="Editing existing scoreboard field:", color=0x4EDB23)
            else:
                print("Field " + name + " doesn't exist")
                embed = discord.Embed(title="Creating new scoreboard field:", color=0x4EDB23)


            msg_text = '\n**Name:** ' + name
            msg_text += '\n**Type:** ' + str(type)
            msg_text += '\n\nTo confirm: React with an emote to associate with this field!'

            embed.description = msg_text
            msg = await ctx.send(embed=embed)

            def reaction_check(reaction, user):  # Checks if the emoji reaction to sc_field is valid or not
                if user != ctx.author:  # First: Only accept reactions from the command sender
                    return False

                if str(reaction.emoji) in self.sc_config.get_fields_emoji().values():  # Make sure the emoji isn't in use in another field
                    print("Reaction check failed: Duplicate emoji")
                    return False

                if reaction.custom_emoji:  # Finally: If this is a custom emote, make sure the bot can actually use it
                    emoji = get(ctx.guild.emojis, id=reaction.emoji.id)
                    if emoji is None or emoji.available is False:
                        return False

                self.scfield_emote = str(reaction.emoji)
                return True

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=reaction_check)
            except asyncio.TimeoutError:
                msg_text += '\n**Waiting for an emote timed out - run this command again**'
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)
            else:
                print(self.scfield_emote)
                self.sc_config.update_field(name, str(type), self.scfield_emote)
                await msg.add_reaction("👍")
                #await msg.channel.send(embed=utils.format_embed("Updated field " + name + "!", False))
                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard, BOI


    # Creates or updates a scoreboard field
    @commands.command()
    async def scremovefield(self, ctx, name):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            fields = self.sc_config.get_fields()
            if name in fields.keys():
                embed = discord.Embed(title="Removing scoreboard field:", color=0x4EDB23)
            else:
                ctx.send(embed=utils.format_embed("Error: Field " + name + " doesn't exist!", True))
                return


            msg_text = '\n**Name:** ' + name
            msg_text += '\n**Warning: This will permanently delete this field and its scores!**'
            msg_text += '\n\nTo confirm deletion: React with "❌"'

            embed.description = msg_text
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("❌")

            def reaction_check(reaction, user):  # Checks if the emoji reaction to scremovefield is valid or not
                return user == ctx.author and str(reaction.emoji) == '❌'  # Only accept 'X' reactions from the command sender

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=reaction_check)
            except asyncio.TimeoutError:
                msg_text += '\n**Waiting for a reaction timed out - run this command again**'
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)
            else:
                self.sc_config.remove_field(name)
                #await msg.channel.send(embed=utils.format_embed("Deleted field " + name, False))
                await msg.add_reaction("👍")
                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard, BOI



    #  Submits a score for entry
    @commands.command()
    async def submit(self, ctx, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member):  # Prevent this from running outside of a guild:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded!", True))
                return

            field = "Song 1"  # Debug: Submit scores only to the default field

            self.sc_config.update_entry(field, ctx.author.id, score, False)

            if randrange(0, 100) == 0:
                scmsg = "You showed us... your ULTIMATE dance... Thank you very much... I can't stop CRYING, BUCKETS of ***TEARS.....***"
            else:
                scmsg = Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))]

            await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
            embedd = discord.Embed(title="Score submitted for verification - " + scmsg, description=field + ": " + str(score), colour=0x16E200)
            await ctx.send(embed=embedd)



    #  Sets a user's verified score entry (to a specified score if specified, else to their unverified score if they have one)
    @commands.command()
    async def verify(self, ctx, member: discord.Member, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            field = "Song 1"  # Debug: Submit scores only to the default field

            #try:
            if int(score) == -1:  # Score = -1 means score wasn't specified as an argument, so verify the user's unverified score
                existing_scores = self.sc_config.get_entry(field, member.id)
                print("Attempting verify of user " + member.display_name + "'s unverified score")
                print(existing_scores)
                if existing_scores is False or existing_scores[0] == -1:  # Plot twist: The user doesn't have an unverified score to verify
                    await ctx.send(embed=utils.format_embed("Error: This user doesn't have an unverified score! Specify their score after their username!", True))
                    return

                else:  # They have an unverified score, set their new verified score to it
                    score = existing_scores[0]

            #except TypeError as e:
#                print("TypeError in score verification: " + str(e) + "\nWas the specified score an int?")
#                await ctx.send(embed=utils.format_embed("Error: Specified score \"" + str(score) + "\" is not an int!", True))
#                return

            self.sc_config.update_entry(field, member.id, score, True)

            await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
            embedd = discord.Embed(title="Set user " + member.display_name + "'s verified score", description=field + ": " + str(score), colour=0x16E200)
            await ctx.send(embed=embedd)


    # Removes a score entry from the scoreboard
    @commands.command()
    async def scremoveentry(self, ctx, member: discord.Member):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            field = "Song 1"  # Debug: Submit scores only to the default field
            result = self.sc_config.remove_entry(field, member.id)
            if result:
                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
                await ctx.send(embed=utils.format_embed("Removed " + member.display_name + "'s entry from " + field, False))
            else:
                await ctx.send(embed=utils.format_embed("Unable to remove " + member.display_name + "'s entry from " + field, True))


    # Sends a new leaderboard message
    @commands.command()
    async def scoreboard(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            await self.generate_scoreboard_message(ctx, True)


    # Generates a scoreboard message, either updating the existing one or sending a new one
    async def generate_scoreboard_message(self, ctx, generate_new):
        # Make sure a scoreboard config is loaded first
        if not self.sc_config.is_scoreboard_loaded():
            print("Error: Attempted to generate a scoreboard message while no scoreboard config was loaded")
            return

        # First, if we're sending a new message we should delete the old one (if it exists)
        old_msg_id = self.sc_config.get_scoreboard_msg()
        if old_msg_id is None:  # Don't even have an old message id, we gotta make a new one
            generate_new = True

        if generate_new:
            if old_msg_id is not None:
                try:
                    old_msg = await self.bot.get_channel(old_msg_id[0]).fetch_message(old_msg_id[1])
                    await old_msg.delete()
                except discord.errors.NotFound:
                    print("Received 404 trying to delete scoreboard message with ID " + str(old_msg_id[1]) + ", was it already deleted?")

        # Next, generate the message embed
        embed = discord.Embed(title="👑   Event Leaderboard  👑",  # Title: Leaderboard
                              description=self.sc_config.get_desc() + "\n.",  # Description
                              color=0xFF7D00)
        embed.set_author(name=self.sc_config.get_disp_name(),
                         url="https://www.youtube.com/watch?v=2ocykBzWDiM")  # Author field: Event name, link
        embed.set_footer(text="Type !score to submit a score  -  ⚠ scores are unverified")  # Footer: Brief instructions

        for field, emoji in self.sc_config.get_fields_emoji().items():  # First get a list of fields to display...
            fieldtext = ""
            entries = self.sc_config.get_entries(field, ctx.guild)  # ...then a list of entries for that field
            entry_members = sorted(entries.items(), key=lambda i: i[1][0], reverse=True)  # Get a list of users, sorted by their entry's highest score
            # print(entry_members)
            for i, entry in enumerate(entry_members):  # And place em on the leaderboard!
                # print(entry[0] + str(entry[1][0]) + str(entry[1][1]))
                fieldtext += str(i + 1) + ") " + entry[0] + " *" + str(entry[1][0]) + "*"
                if entry[1][1] is False:  # This entry is unverified, mark it as such
                    fieldtext += "  ⚠"
                else:
                    fieldtext += "  ✔"
                fieldtext += "\n"

            if fieldtext == "":
                fieldtext = "No scores yet!"
            embed.add_field(name=emoji + "  " + field, value=fieldtext)

        # Updating an old message
        if not generate_new:
            try:
                msg = await self.bot.get_channel(old_msg_id[0]).fetch_message(old_msg_id[1])
                await msg.edit(embed=embed)
                print("Updated scoreboard message")

            except (TypeError, discord.errors.NotFound) as e:  # 404 i dunno where the old message went
                print("Error updating scoreboard message: Message with ID " + str(old_msg_id[1]) + " not found, generating new message instead")
                generate_new = True

        # Generating a new message (or updating the old one failed above)
        if generate_new:
            msg = await ctx.send(embed=embed)
            self.sc_config.set_scoreboard_msg(msg.channel.id, msg.id)
            print("New scoreboard message sent (ID=" + str(msg.id) + ")")

