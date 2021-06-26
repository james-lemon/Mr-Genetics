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
        "Yeah, I KNEW you could do it!",
        "Wow, you're awesome!",
        "Way to step it up!",
        "Your skills are UN-be-lieveable!",
        "Perfection is your first, last, AND middle name!",
        "Total ability UP!",
        "Showers are sexy! Take one today!",
        "\*Does a little jig\*",
        "Hell yeah, pizza time.",
        "I'm screenshotting this, thank you very much",

    )

    def __init__(self, bot):
        self.bot = bot
        self.sc_config = scoreboard_config_man.ScoreboardConfig()

        self.scfield_emote = None
        self.scdiv_emote = None
        self.scdiv_division = {}
        self.scsubmit_field = {}
        self.scverify_field = {}
        self.scrm_field = {}

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



    # Tries unloading the current scoreboard config (so no config is active)
    @commands.command()
    async def scunload(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("No scoreboard is currently loaded, nothing to unload!", False))
                return
            self.sc_config.save_sc_config() #Don't nuke ur data kids, triple-check that you've saved to disk before loading a new config
            self.sc_config.unload_sc_config()
            config_man.set_default_scoreboard("")
            await ctx.send(embed=utils.format_embed("Unloaded scoreboard - no scoreboard is active now", False))



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


    # Creates a new scoreboard division
    @commands.command()
    async def scnewdiv(self, ctx, name, *, desc=""):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            embed = discord.Embed(title="Creating a new scoreboard division:", color=0x4EDB23)
            msg_text = '\n**Name:**' + name
            msg_text += '\n**Desc:**' + desc
            msg_text += '\n\nTo confirm: React with an emote to associate with this division!'
            embed.description = msg_text
            msg = await ctx.send(embed=embed)

            def reaction_check(reaction, user):  # Checks if the emoji reaction to sc_field is valid or not
                if user != ctx.author or reaction.message.id != msg.id:  # First: Only accept reactions from the command sender on the message we just sent
                    return False

                if str(reaction.emoji) in self.sc_config.get_division_emotes().keys():  # Make sure the emoji isn't in use in another division
                    print("Reaction check failed: Duplicate emoji")
                    return False

                if reaction.custom_emoji:  # Finally: If this is a custom emote, make sure the bot can actually use it
                    emoji = get(ctx.guild.emojis, id=reaction.emoji.id)
                    if emoji is None or emoji.available is False:
                        return False

                self.scdiv_emote = str(reaction.emoji)
                return True

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=reaction_check)
            except asyncio.TimeoutError:
                msg_text += '\n**Waiting for an emote timed out - run this command again**'
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)
            else:
                if self.sc_config.div_new(name, desc, self.scdiv_emote):
                    await msg.add_reaction('👍')
                    return
                else:
                    await ctx.send(embed=utils.format_embed("Error creating division \"" + name + "\".", True))
                    return


    # Sets a division's description
    @commands.command()
    async def scdivdescription(self, ctx, name, *, description):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            if self.sc_config.div_desc(name, description):
                await ctx.send(embed=utils.format_embed("Set division \"" + name + "\"'s description", False))
                return
            else:
                await ctx.send(embed=utils.format_embed("Error removing division - division \"" + name + "\" doesn't exist!", True))
                return


    # Removes a scoreboard division
    @commands.command()
    async def scremovediv(self, ctx, name):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            if self.sc_config.div_remove(name):
                await ctx.send(embed=utils.format_embed("Removed division \"" + name + "\".", False))
                return
            else:
                await ctx.send(embed=utils.format_embed("Error removing division - division \"" + name + "\" doesn't exist!", True))
                return


    # Creates or updates a scoreboard field
    @commands.command()
    async def scfield(self, ctx, division, name, type=0):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            div = self.sc_config.get_division(division)
            if div is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid divsion name \"" + division + "\"", False))
                return

            type = 0  # Todo: We only support one field type for now, so enforce it here
            ftype = self.sc_config.parse_field_type(type)
            if ftype is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid field type \"" + type + "\"!", True))
                return

            fields = self.sc_config.get_fields(div)
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
                if user != ctx.author or reaction.message.id != msg.id:  # First: Only accept reactions from the command sender on the message we just sent
                    return False

                if str(reaction.emoji) in self.sc_config.get_fields_emoji(div).keys():  # Make sure the emoji isn't in use in another field
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
                self.sc_config.update_field(div, name, str(type), self.scfield_emote)
                await msg.add_reaction("👍")
                #await msg.channel.send(embed=utils.format_embed("Updated field " + name + "!", False))
                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard, BOI


    # Creates or updates a scoreboard field
    @commands.command()
    async def scremovefield(self, ctx, division, name):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            div = self.sc_config.get_division(division)
            if div is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid divsion name \"" + division + "\""))
                return

            fields = self.sc_config.get_fields(div)
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
                return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) == '❌'  # Only accept 'X' reactions from the command sender on the message we sent

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=reaction_check)
            except asyncio.TimeoutError:
                msg_text += '\n**Waiting for a reaction timed out - run this command again**'
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)
            else:
                self.sc_config.remove_field(div, name)
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

            #division = "EZ"  # DEBUG: Hard-code a division name, here, until we can grab a player's real division
            division = self.sc_config.get_player_division(ctx.author.id)
            print("Player " + ctx.author.display_name + "(id: " + str(ctx.author.id) + ") submitting unverified score " + str(score))
            if division is None:  # Player hasn't joined a division yet, prompt them to join
                print("Division check returned None, prompting player for division")
                res = await self.division(ctx)
                if res is False:  # Didn't choose a division lol, bail here
                    return
                division = self.sc_config.get_player_division(ctx.author.id)
            else:
                print("Division check passed, player division \"" + division + "\"")

            div = self.sc_config.get_division(division)
            if div is None:
                print("Division invalid!")
                await ctx.send(embed=utils.format_embed("Error: The division you joined (\"" + division + "\") is invalid... somehow. Please contact an admin :("))
                return

            # Our logic here changes if there's only one field on the scoreboard
            # If there's one field, select it by default and just submit scores to that
            # For multiple fields, we need to prompt the user to select a field
            fields = self.sc_config.get_fields_emoji(div)
            if len(fields) == 1:
                sub_field = list(fields.values())[0]
            else:
                sub_field = None

            # Our reaction-based field prompt - Validate input if the submitting user reacted to it, and their reaction is a field emoji
            def sub_reaction_check(reaction, user):
                if user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in fields.keys():
                    self.scsubmit_field[user.id] = fields[str(reaction.emoji)]
                    return True
                return False

            try:
                if sub_field is None:  # If we haven't set a default field to submit to (above), send the reaction prompt and wait for a reaction
                    embed = discord.Embed(title="Submitting a score:", color=0x4EDB23)
                    msg_text = "\n" + ctx.author.display_name + ": " + str(score)
                    msg_text += "\n\n**React with the field to submit this score to!**\n"
                    for emote, field in fields.items():  # Display the emotes for all the fields we can submit to
                        msg_text += emote + " - " + field + "\n"
                    embed.description = msg_text
                    msg = await ctx.send(embed=embed)

                    for emote in fields.keys():  # And react to the message with all the fields we can submit to (two for loops yeehaw)
                        await msg.add_reaction(emote)

                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=sub_reaction_check)  # Now wait for the user to react
            except asyncio.TimeoutError:
                msg_text += "\n\n**Waiting for a reaction timed out - run this command again**"
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)

            else:  # On reaction (or if we have a field to submit to and never prompted for a reaction), submit the score!
                if sub_field is None:
                    sub_field = self.scsubmit_field[ctx.author.id]
                    print("Reaction-based field set: " + sub_field)
                print("Attempting submission to field " + sub_field)
                self.sc_config.update_entry(div, sub_field, ctx.author.id, score, False)

                if randrange(0, 100) == 0:
                    scmsg = "You showed us... your ULTIMATE dance... Thank you very much... I can't stop CRYING, BUCKETS of ***TEARS.....***"
                else:
                    scmsg = Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))]

                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
                embedd = discord.Embed(title="Score submitted for verification - " + scmsg, description=sub_field + ": " + str(score), colour=0x16E200)
                await ctx.send(embed=embedd)


    # Joins a player to a division, returns if the player is currently in a division or not
    @commands.command()
    async def division(self, ctx):
        divisions = self.sc_config.get_division_names()  # Get a list of divisions and divisions emotes/descriptions
        divisions_emotes = self.sc_config.get_division_emotes()

        cur_div = self.sc_config.get_player_division(ctx.author.id)
        if cur_div is not None:
            await ctx.send(embed=utils.format_embed("You're in division \"" + cur_div + "\"!\n\n (At this time, you cannot switch divisions)", False))
            return True

        # If there's only one divisions, we want to auto-join that one!
        if len(divisions) == 1:
            selected_div = list(divisions.keys())[0]
        else:
            selected_div = None

        # Helper function to validate reaction-based input for the below prompt
        def div_reaction_check(reaction, user):
            if user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in divisions_emotes.keys():
                self.scdiv_division[user.id] = divisions_emotes[str(reaction.emoji)]
                return True
            return False

        try:
            if selected_div is None:  # Didn't auto-pick a division? Prompt for one
                emb = discord.Embed(title="Pick a division to join:", color=0x4EDB23)
                desc = ""
                for div_emote, div_name in divisions_emotes.items():  # List the divisions to join, their emotes, and descriptions
                    desc += div_emote + " **" + div_name + ":** " + divisions[div_name] + "\n"

                emb.description = desc
                msg = await ctx.send(embed=emb)

                for emote in divisions_emotes.keys():  # React to the message with the division emotes we can join
                    await msg.add_reaction(emote)

                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=div_reaction_check)  # And wait for the user to react to pick a division

        except asyncio.TimeoutError:  # User didn't react in time
            desc += "\n\n**Waiting for a reaction timed out - run this command again**"
            emb.description = desc
            emb.color = 0xDB2323
            await msg.edit(embed=emb)
            return False

        else:  # On reaction (or auto-selected division), set the player's division
            if selected_div is None:  # Didn't auto-select
                selected_div = self.scdiv_division[ctx.author.id]
                print("Reaction-based division set: " + selected_div)
            print("Attempting to set user division: " + ctx.author.display_name + ", " + selected_div)
            res = self.sc_config.set_player_division(ctx.author.id, selected_div)
            if res:
                await ctx.send(embed=utils.format_embed("You've joined division " + selected_div + "!", False))
                return True
            else:
                await ctx.send(embed=utils.format_embed("Unable to join division " + selected_div + " - Please contact an admin", True))
                return False


    #  Sets a user's verified score entry (to a specified score if specified, else to their unverified score if they have one)
    @commands.command()
    async def verify(self, ctx, division, member: discord.Member, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            div = self.sc_config.get_division(division)
            if div is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid divsion name \"" + division + "\"", True))
                return

            fields = self.sc_config.get_fields_emoji(div)
            if len(fields) == 1:  # Only one field, just submit to that one by default
                ver_field = list(fields.values())[0]
            else:  # Multiple fields - figure out which later:tm:
                ver_field = None

            # Validation method when prompting the user to pick a field to verify scores from
            def ver_reaction_check(reaction, user):
                if user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in fields.keys():
                    self.scverify_field[user.id] = fields[str(reaction.emoji)]
                    return True
                return False

            try:
                if ver_field is None:  # Still need to prompt the user to choose a field to submit to, do it
                    embed = discord.Embed(title="Verifying score:", color=0x4EDB23)
                    msg_text = "\n" + ctx.author.display_name
                    if int(score) == -1:
                        msg_text += "'s unverified score"
                    else:
                        msg_text += ": " + str(score)
                    msg_text += "\n\n**React with the field to verify this score from!**"
                    embed.description = msg_text
                    msg = await ctx.send(embed=embed)

                    for emote in fields.keys():  # React to this message with the emotes for all the fields we can submit to
                        await msg.add_reaction(emote)

                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=ver_reaction_check)

            except asyncio.TimeoutError:
                msg_text += "\n\n**Waiting for a reaction timed out - run this command again**"
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)

            else:  # On valid reaction/we cheated and already know the field to verify:
                if ver_field is None:
                    ver_field = self.scverify_field[ctx.author.id]
                    print("Reaction-based field set: " + ver_field)
                print("Attempting verification of score from field " + ver_field)

                #try:
                if int(score) == -1:  # Score = -1 means score wasn't specified as an argument, so verify the user's unverified score
                    existing_scores = self.sc_config.get_entry(div, ver_field, member.id)
                    print("Attempting verify of user " + member.display_name + "'s unverified score")
                    print(existing_scores)
                    if existing_scores is False or existing_scores[0] == -1:  # Plot twist: The user doesn't have an unverified score to verify
                        await ctx.send(embed=utils.format_embed("Error: This user doesn't have an unverified score in field " + ver_field + "! Specify their score after their username!", True))
                        return

                    else:  # They have an unverified score, set their new verified score to it
                        score = existing_scores[0]

                #except TypeError as e:
    #                print("TypeError in score verification: " + str(e) + "\nWas the specified score an int?")
    #                await ctx.send(embed=utils.format_embed("Error: Specified score \"" + str(score) + "\" is not an int!", True))
    #                return
                self.sc_config.update_entry(div, ver_field, member.id, score, True)

                await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
                embedd = discord.Embed(title="Set user " + member.display_name + "'s verified score", description="Division: " + division + "\nField " + ver_field + ": " + str(score), colour=0x16E200)
                await ctx.send(embed=embedd)


    # Removes a score entry from the scoreboard
    @commands.command()
    async def scremoveentry(self, ctx, division, member: discord.Member):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            div = self.sc_config.get_division(division)
            if div is None:
                await ctx.send(embed=utils.format_embed("Error: Invalid divsion name \"" + division + "\""))
                return

            fields = self.sc_config.get_fields_emoji(div)
            if len(fields) == 1:
                rm_field = list(fields.values())[0]
            else:
                rm_field = None

            # Field prompt part 3rd
            def rm_reaction_check(reaction, user):
                if user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in fields.keys():
                    self.scrm_field[user.id] = fields[str(reaction.emoji)]
                    return True
                return False

            try:
                if rm_field is None:
                    embed = discord.Embed(title="Removing a score:", color=0x4EDB23)
                    msg_text = "\n" + ctx.author.display_name
                    msg_text += "\n\n**React with the field to remove this user's score from!**\n"
                    for emote, field in fields.items():
                        msg_text += emote + " - " + field + "\n"
                    embed.description = msg_text
                    msg = await ctx.send(embed=embed)

                    for emote in fields.keys():
                        await msg.add_reaction(emote)

                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=rm_reaction_check)

            except asyncio.TimeoutError:
                msg_text += "\n\n**Waiting for a reaction timed out - run this command again**"
                embed.description = msg_text
                embed.color = 0xDB2323
                await msg.edit(embed=embed)

            else:
                if rm_field is None:
                    rm_field = self.scrm_field[ctx.author.id]
                    print("Reaction-based field set: " + rm_field)
                print("Attempting entry removal from field " + rm_field)
                result = self.sc_config.remove_entry(div, rm_field, member.id)

                if result:
                    await self.generate_scoreboard_message(ctx, False)  # Update the scoreboard
                    await ctx.send(embed=utils.format_embed("Removed " + member.display_name + "'s entry from " + rm_field, False))
                else:
                    await ctx.send(embed=utils.format_embed("Unable to remove " + member.display_name + "'s entry from " + rm_field, True))


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
                              color=0xFF7D00)
        embed.set_author(name=self.sc_config.get_disp_name(),
                         url="https://www.youtube.com/watch?v=PGNiXGX2nLU")  # Author field: Event name, link
        embed.set_footer(text="Type !submit to submit a score  -  \"⚠\" scores are unverified")  # Footer: Brief instructions

        desc_text = self.sc_config.get_desc() + "\n\n"
        for div_emoji, div in self.sc_config.get_divisions().items():  # First get a list of divisions to display...
            desc_text += div_emoji + " - Division " + div.getAttribute("name") + "\n"
            # print("Div " + div_emoji)
            for emoji, field in self.sc_config.get_fields_emoji(div).items():  # First (but not first) get a list of fields to display...
                # print("Field" + emoji)
                fieldtext = ""
                entries = self.sc_config.get_entries(div, field, ctx.guild)  # ...then a list of entries for that field
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
                embed.add_field(name=div_emoji + ": " + emoji + "  " + field, value=fieldtext)

        desc_text += "\n."
        embed.description = desc_text
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

