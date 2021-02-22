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
        "You've shown us your ultimate dance!",
        "Ganbare!",
        "***Do it!!!***",
    )
    def __init__(self, bot):
        self.bot = bot
        self.sc_config = scoreboard_config_man.ScoreboardConfig()

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
            elif loaded == 1:
                await ctx.send(embed=utils.format_embed("Created new scoreboard " + name, False))
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
            await ctx.send(embed=utils.format_embed("Set scoreboard display name to " + name, False))



    # Sets the scoreboard's description
    @commands.command()
    async def scdescription(self, ctx, *, desc):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            self.sc_config.set_desc(desc)
            await ctx.send(embed=utils.format_embed("Set scoreboard description to " + desc, False))



    #  Submits a score for entry
    @commands.command()
    async def submit(self, ctx, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member):  # Prevent this from running outside of a guild:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded!", True))
                return
            print(Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))])
            embedd = discord.Embed(title="Score submitted for verification - " + Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))], description="Song1 - " + str(score), colour=0x16E200)
            await ctx.send(embed=embedd)


    #  Verifies a user's score entry (optionally accepting an argument for a score correction
    @commands.command()
    async def verify(self, ctx, member: discord.Member, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return
            embedd = discord.Embed(title="Verified user " + member.display_name + "'s score", description="Song1 - " + str(score), colour=0x16E200)
            await ctx.send(embed=embedd)


    # Sends a new leaderboard message
    @commands.command()
    async def scoreboard(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            if not self.sc_config.is_scoreboard_loaded():
                await ctx.send(embed=utils.format_embed("Error: No scoreboard is currently loaded! Load one with !scload", True))
                return

            embed = discord.Embed(title="👑   Event Leaderboard  👑",  # Title: Leaderboard
                                  description=self.sc_config.get_desc() + "\n.",  # Description
                                  color=0xFF7D00)
            embed.set_author(name=self.sc_config.get_disp_name(), url="https://www.youtube.com/watch?v=2ocykBzWDiM")  # Author field: Event name, link
            embed.set_footer(text="Type !score to submit a score!")  # Footer: Brief instructions
            embed.add_field(name="Song 1", value="1) Gene - *573*\n2) etics - *-5*\n ")  # Fields: Individual field/score combos
            embed.add_field(name="Song 2", value="1) The Duck - *574*\n2) 4848 - *100*\n ")
            embed.add_field(name="The third field",
                            value="1) Player 1 - *574*\n2) Player 2 - *100*\n3) Player 3 - *12*\n...and 4 other players\n ")
            await ctx.send(embed=embed)
