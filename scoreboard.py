#!/usr/bin/python

# --
# scoreboard.py: Logic/variables related to the scoreboard feature
# --

import config_man
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
        "!",
    )
    def __init__(self, bot):
        self.bot = bot



    #  Submits a score for entry
    @commands.command()
    async def submit(self, ctx, score=-1):
        print(Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))])
        embedd = discord.Embed(title="Score submitted for verification - " + Scoreboard.score_messages[randrange(len(Scoreboard.score_messages))], description="Song1 - " + str(score), colour=0x16E200)
        await ctx.send(embed=embedd)



    #  Verifies a user's score entry (optionally accepting an argument for a score correction
    @commands.command()
    async def verify(self, ctx, member: discord.Member, score=-1):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            embedd = discord.Embed(title="Verified user " + member.display_name + "'s score", description="Song1 - " + str(score), colour=0x16E200)
            await ctx.send(embed=embedd)


    # Sends a new leaderboard message
    @commands.command()
    async def leaderboard(self, ctx):
        if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Prevent this from running outside of a guild or by non-admins:
            embed = discord.Embed(title="👑   Event Leaderboard  👑",
                                  description="*get it the name's an arcade pun kek - details in #announcements*\n.",
                                  color=0xFF7D00)
            embed.set_author(name="Jeremy's Downtown Pajamma Party", url="https://www.youtube.com/watch?v=2ocykBzWDiM")
            embed.set_footer(text="Type !score to submit a score!")
            embed.add_field(name="Song 1", value="1) Gene - *573*\n2) etics - *-5*\n ")
            embed.add_field(name="Song 2", value="1) The Duck - *574*\n2) 4848 - *100*\n ")
            embed.add_field(name="The third field",
                            value="1) Player 1 - *574*\n2) Player 2 - *100*\n3) Player 3 - *12*\n...and 4 other players\n ")
            await ctx.send(embed=embed)
