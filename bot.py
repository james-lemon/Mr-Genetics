#!/usr/bin/python

# --
# Mr. Genetics - The discord bot to blame when you have bad genes

# Written by 48productions, 2020
# --

import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get

import config_man
import utils
from rolelist import RoleList
from duckboard import DuckBoard
from colorlist import ColorList
import playing_messages


print('Initalizing Mr. Genetics, using discordpy version ' + discord.__version__)

intents = discord.Intents(guilds=True, members=True, emojis=True, messages=True, message_content=True, guild_reactions=True)  # Set our intents - Subscribes to certain types of events from discord

bot = commands.Bot(command_prefix=commands.when_mentioned, case_insensitive=True, intents=intents)

bot.remove_command('help')  # Remove the default help command, imma make my own lel

rolelist = RoleList(bot)
duckboard = DuckBoard(bot)
colorlist = ColorList(bot)

@bot.event
async def on_ready():
    await bot.add_cog(rolelist)
    #await bot.add_cog(duckboard)
    await bot.add_cog(colorlist)
    print('Bot logged on as user: ', bot.user)
    bot.loop.create_task(change_status())  # Also start the "change status every so often" task, too
    #print(bot.tree.get_commands())
    #lol = await bot.tree.sync(guild=discord.Object(id=)) # Debug: Sync slash commands to a specific guild (MUCH faster)
    #print('Slash command sync okay')


# Sets the admin role in the config
@bot.command()
async def setadminrole(ctx, role: discord.Role):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        if role is not None:
            embed = discord.Embed(title="Will set the admin role", colour=0xFF7D00)  # Create an embed, set it's title and color
            embed.description = "**Role:** " + role.name + "\n\nUsers without this role can't edit or send the role list, and can only react to it for roles.\n\n**Ensure you have this role and react with 🔒 to confirm!**"
            msg = await ctx.send(embed=embed)
            rolelist.setadmin_message[0] = msg.channel.id
            rolelist.setadmin_message[1] = msg.id
            rolelist.setadmin_role = str(role.id)
            await msg.add_reaction('🔒')
            print("Sent setadminrole message: ", msg.id)
        else:
            await ctx.send(embed=utils.format_embed("Invalid role given!", True))  # This might not even get reached, on_command_error() might intercept things first


# Sends an introduction message, da-don!
@bot.command()
async def introduction(ctx):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        await ctx.send("*Musical quack*, da-don 🦆")


# Sync slash commands to the current guild
@bot.command()
async def synccommands(ctx, syncglobal=False):
    if not isinstance(ctx.channel, discord.DMChannel) and isinstance(ctx.author, discord.Member) and utils.authorize_admin(ctx.guild, ctx.author):  # First: Authorize an admin is running this command
        # Slash commands must be synced in order to appear in autocomplete/etc. Maybe to even be used at all? W/e, needs to happen as a one-time setup thing
        # They can either be synced globally (takes up to an hour, ratelimited in some instances) or to a specific guild
        # This bot is intended for use in only ONE server, so we'll take the latter route here
        try:
            if syncglobal:
                commandlist = await bot.tree.sync()
                await ctx.send(embed=utils.format_embed('Successfully synced ' + str(len(commandlist)) + ' slash commands globally', False))

            else:
                bot.tree.copy_global_to(guild=discord.Object(id=ctx.guild.id))
                commandlist = await bot.tree.sync(guild=discord.Object(id=ctx.guild.id))
                await ctx.send(embed=utils.format_embed('Successfully synced ' + str(len(commandlist)) + ' slash commands to this guild', False))

        except discord.HTTPException:
            await ctx.send(embed=utils.format_embed('Slash command sync has FAILED!', True))
            return
        except discord.Forbidden:
            await ctx.send(embed=utils.format_embed('Slash command sync failed - check that slash commands are allowed', True))
            return


# A help command that DMs the sender with command info
@bot.tree.command(description='Receive a list of available commands')
async def help(interaction: discord.Interaction):
    if not isinstance(interaction.channel, discord.DMChannel) and isinstance(interaction.user, discord.Member):  # First: Make sure we're running this as a member in a guild
        embed = discord.Embed(title="Command Help", colour=0xFF7D00)  # Create an embed, set it's title and color
        if utils.authorize_admin(interaction.guild, interaction.user):
            embed.description = "\n`/help:` Get sent this list\n\n" \
                            "`synccommands (global):` Syncs this bot's slash commands to the current guild (or globally if \"True\" is specified). Required one-time setup.\n\n" \
                            "`addrole \"Category\" \"Role\" Description:`  Adds an assignable role to the role list\n\n" \
                            "`adddisprole \"Category\" \"Role\" Description:`  Adds a non-assignable role to the role list\n\n" \
                            "`editrole \"Category\" \"Role\" Description:`  Removes and re-adds a role to the role list\n\n" \
                            "`removerole \"Category\" \"Role\":`  Removes a role from the role list\n\n" \
                            "`rolelist:`  Updates all active rolelist messages. Sends new list messages to the current channel if needed.\n\n" \
                            "`newrolelist:`  Deletes the old role list and sends a new one to the current channel\n\n" \
                            "`setadminrole \"Role\":`  Sets a role as this bot's \"admin\" role\n\n" \
                            "`sortcategory \"Category\":`  Sorts the roles in a category (alphabetical order)\n\n" \
                            "`setcategorydescription \"Category\" Description:` Sets a category's description (optional)\n\n\n" \
                            "`duckboard:` Sets this channel as the channel to repost starboard messages in\n\n" \
                            "`duckboardcount Count:` Sets the number of reactions a message needs to be reposted\n\n" \
                            "Note:  If an admin role is set, you'll need that role to run most commands!"
        else:
            embed.description = "\nThe Duck is 48productions' role management and (soon to be) duckboard bot.\n\n" \
                            "`/help:` Get sent this list\n\n" \
                            "`/color:` Choose a name color\n\n\n\n\n" \
                            "...that's it, that's all the help you get :)"
                            # "With enough reactions, any message will be reposted in the duckboard channel for your viewing pleasure!\n\n\n\n\n" \

        await interaction.user.send(embed=embed)
        await interaction.response.send_message(embed=utils.format_embed("DM'd ya fam 😉", False))





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
        await asyncio.sleep(60 * 60 * 2)  # 60 seconds * 60 minutes * 2 hours

# Now to actually run the bot:
secret = open("secret-token.txt", "r").read(59)  # Load our spooper secret token from file
if len(secret) == 59:  # Basic length check for invalid secrets (are secrets always 59 characters lnog???? I DUNNO BRUH!!!1!
    #bot.tree.copy_global_to(guild=discord.Object(id=)) # Debug: Copy slash commands in the global scope to a specific guild so it syncs faster
    bot.run(secret)
else:
    print("Invalid secret? Place this bot's access token in secret-token.txt to run!")
