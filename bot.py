#!/usr/bin/python

# --
# Mr. Genetics - The discord bot to blame when you have bad genes

# Written by 48productions, 2020
# --

import asyncio
import discord
from discord.ext import commands
from discord.utils import get

import config_man
import utils
from rolelist import RoleList
from scoreboard import Scoreboard
import playing_messages


print('Initalizing Mr. Genetics, using discordpy version ' + discord.__version__)

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, guild_reactions=True)  # Set our intents - Subscribes to certain types of events from discord

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)

bot.remove_command('help')  # Remove the default help command, imma make my own lel

bot.add_cog(RoleList(bot))
bot.add_cog(Scoreboard(bot))

@bot.event
async def on_ready():
    #global admin_role
    print('Bot logged on as user: ', bot.user)
    bot.loop.create_task(change_status())  # Also start the "change status every so often" task, too


# Sets the admin role in the config
@bot.command()
async def setadminrole(ctx, role: discord.Role):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        global setadmin_message, setadminrole
        if role is not None:
            embed = discord.Embed(title="Will set the admin role", colour=0xFF7D00)  # Create an embed, set it's title and color
            embed.description = "**Role:** " + role.name + "\n\nUsers without this role can't edit or send the role list, and can only react to it for roles.\n\n**Ensure you have this role and react with 🔒 to confirm!**"
            msg = await ctx.send(embed=embed)
            setadmin_message[0] = msg.channel.id
            setadmin_message[1] = msg.id
            setadmin_role = str(role.id)
            await msg.add_reaction('🔒')
            print("Sent setadminrole message: ", msg.id)
        else:
            await ctx.send(embed=utils.format_embed("Invalid role given!", True))  # This might not even get reached, on_command_error() might intercept things first

# Sends an introduction message, da-don!
@bot.command()
async def introduction(ctx):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        await ctx.send("*Musical quack*, da-don 🦆")


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id and bot.user in message.mentions:  # On pings, react with duck
        duck_emote = str(get(message.guild.emojis, name="discoduck"))
        if duck_emote == "None":
            duck_emote = "🦆"
        print(duck_emote)
        await message.add_reaction(duck_emote)
    else:
        await bot.process_commands(message)


# A help command that DMs the sender with command info
@bot.command()
async def help(ctx):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member):  # First: Authorize an admin is running this command
        embed = discord.Embed(title="Command Help", colour=0xFF7D00)  # Create an embed, set it's title and color
        if utils.authorize_admin(ctx.guild, ctx.author):
            embed.description = "\n`help:` Get sent this list\n\n" \
                            "`addrole \"Category\" \"Role\" Description:`  Adds an assignable role to the role list\n\n" \
                            "`adddisprole \"Category\" \"Role\" Description:`  Adds a non-assignable role to the role list\n\n" \
                            "`editrole \"Category\" \"Role\" Description:`  Removes and re-adds a role to the role list\n\n" \
                            "`removerole \"Category\" \"Role\":`  Removes a role from the role list\n\n" \
                            "`rolelist:`  Sends/updates the role list messages to the current channel\n\n" \
                            "`newrolelist:`  Deletes the old role list and sends a new one to the current channel\n\n" \
                            "`setadminrole \"Role\":`  Sets a role as this bot's \"admin\" role\n\n" \
                            "`sortcategory \"Category\":`  Sorts the roles in a category (alphabetical order)\n\n" \
                            "`setcategorydescription \"Category\" Description:` Sets a category's description (optional)\n\n\n" \
                            "`scnew \"Fileame\" Description:` Creates a new scoreboard\n\n" \
                            "`scload \"Filename\":` Loads a saved scoreboard from file\n\n" \
                            "`scoreboard:` Sends a new scoreboard message\n\n" \
                            "`scdisplayname Name:` Sets a scoreboard's display name\n\n" \
                            "`scdescription Desc:` Sets a scoreboard's description\n\n" \
                            "`scfield \"name\" type:` Adds/updates a scoreboard field\n\n"\
                            "`scremovefield \"name\":` Removes a scoreboard field\n\n" \
                            "`submit score:` Submits a score to the scoreboard (adding a score is optional)\n\n" \
                            "`verify user score:` Verifies user's score on the scoreboard (score is optional if the user provided a score)\n\n" \
                            "Note:  If an admin role is set, you'll need that role to run most commands!"
        else:
            embed.description = "\n`!help:` Get sent this list\n\n" \
                            "`!submit <score>:` Submits a score to the leaderboard (specifying score is optional, must be verified by an admin)\n\n\n" \
                            "...yeah there's not much else non-admins can do :/\n\n" \
                            "I guess you can ping me if you get super bored lol"

        await ctx.author.send(embed=embed)
        await ctx.send(embed=utils.format_embed("DM'd ya fam 😉", False))





@bot.event
async def on_command_error(ctx, error):
    if isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # Invalid commands run by non-admins can still display error messages - Prevent that here
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=utils.format_embed('Missing arguments!', True))
            return
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=utils.format_embed('Bad argument given!', True))
            return
        raise error



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
