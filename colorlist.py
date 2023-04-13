#!/usr/bin/python

# --
# colorlist.py - Colorlist commands
# --
import discord
from discord import SelectOption, app_commands
from discord.ext import commands
from discord.ui import Select

import config_man
import utils

# The color dropdown selection and logic
class ColorSelect(discord.ui.Select):
    def __init__(self):
        global colorRoles
        options = []
        for color in colorRoles.items():
            options = SelectOption(label=color[1], value=color[0])
        super().__init__(placeholder="Select a name color", options=options)

    # Someone picked a  c o l o r
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Incorrect color: " + self.values[0], ephemeral=True)



# The view of the selection presented to the user
class ColorSelectView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(ColorSelect())

class ColorList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # Sets a user's name color
    @app_commands.command(description='Change your name color in chat')
    async def color(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.DMChannel) and isinstance(interaction.user, discord.Member):  # First: Check the user is running this command in a server
            await interaction.response.send_message(view=ColorSelectView(), ephemeral=True)
