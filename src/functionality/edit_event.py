import re
import datetime
import discord
from discord import Client
from discord.ext import commands
from src.functionality.shared_functions import read_event_file, create_event_tree, delete_event_from_file
from src.functionality.highlights import convert_to_12

async def edit_event(ctx, bot):
    """
    Function:
        edit_event
    Description:
        A existing event is edited from the user's schedule file
    Input:
        ctx: the current context
        client: the instance of the bot
    Output:
        - A reply saying whether the event was updated or not
    """

    channel = await ctx.author.create_dm()
    

