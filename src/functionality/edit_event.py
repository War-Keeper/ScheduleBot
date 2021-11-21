import re
import datetime
import discord
from discord import Client
from discord.ext import commands
from src.functionality.shared_functions import read_event_file, create_event_tree, delete_event_from_file
from src.functionality.highlights import convert_to_12

async def edit_event(ctx, client):
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
    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author
    
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

            events.append(event)
            
            
            
            # reset event
            event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}
            
    else:
        eventFlag = True
        await channel.send("Looks like your schedule is empty. You can add events using the '!schedule' command!")
    
    #delete the event and event type
    if not eventFlag:
        await channel.send("Please enter the name of the event you want to edit")
        event_msg = await client.wait_for("message", check=check)  # Waits for user input
        event_msg = event_msg.content  # Strips message to just the text the user entered
        next((item for item in events if item["name"] == event_msg), None)


async def send_event_info(ctx, event):
    embed = discord.Embed(colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at,
                                      title="Your Schedule:")
    embed.set_footer(text=f"Requested by {ctx.author}")
    embed.add_field(name="Event Name:", value=event['name'], inline=False)
    embed.add_field(name="Start Time:", value=event['startTime'], inline=True)
    embed.add_field(name="End Time:", value=event['endTime'], inline=True)
    embed.add_field(name="Event Type:", value=event['type'], inline=False)
    embed.add_field(name="Description:", value=event['desc'], inline=False)
    await ctx.send(embed=embed)          