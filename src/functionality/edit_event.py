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
    # Open and read user's calendar file
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id))
    
    # Initialize variables
    channel = await ctx.author.create_dm()
    event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}
    events = []
    eventFlag = False
    
    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
            event['name'] = row[1]
            start = row[2].split()
            event['startDate'] = start[0]
            event['startTime'] = convert_to_12(start[1][:-3])  # Convert to 12 hour format
            end = row[3].split()
            event['endDate'] = end[0]
            event['endTime'] = convert_to_12(end[1][:-3])  # Convert to 12 hour format
            event['type'] = row[4]
            event['desc'] = row[5]
            #dates = [event['startDate'], event['endDate']]

            events.append(event)

            # reset event
            event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}
    

