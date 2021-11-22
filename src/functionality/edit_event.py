import re
import datetime
import discord
from discord import Client
from discord.ext import commands
from src.functionality.shared_functions import read_event_file, create_event_tree, delete_event_from_file
from src.functionality.highlights import convert_to_12
import json

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
    event = {'name': '', 'startDateTime': '', 'endDateTime': '', 'type': '', 'desc': ''}
    events = []
    eventFlag = False
    
    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
            event['name'] = row[1]
            # start = row[2].split()
            event['startDateTime'] = datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
            # event['startTime'] = convert_to_12(start[1][:-3])  # Convert to 12 hour format
            # end = row[3].split()
            event['endDateTime'] = datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
            # event['endTime'] = convert_to_12(end[1][:-3])  # Convert to 12 hour format
            event['type'] = row[4]
            event['desc'] = row[5]
            events.append(event)
            
            # send event information to user
            embed = discord.Embed(colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at,
                                      title="Your Schedule:")
            embed.set_footer(text=f"Requested by {ctx.author}")
            embed.add_field(name="Event Name:", value=event['name'], inline=False)
            embed.add_field(name="Start Date & Time:", value=event['startDateTime'], inline=True)
            embed.add_field(name="End Date & Time:", value=event['endDateTime'], inline=True)
            embed.add_field(name="Event Type:", value=event['type'], inline=False)
            embed.add_field(name="Description:", value=event['desc'], inline=False)
            await ctx.send(embed=embed)    
            
            # reset event dict
            event = {'name': '', 'startDateTime': '', 'endDateTime': '', 'type': '', 'desc': ''}
            
    else:
        eventFlag = True
        await channel.send("Looks like your schedule is empty. You can add events using the '!schedule' command!")
    
    #delete the event and event type
    if not eventFlag:
        await channel.send("Please enter the name of the event you want to edit")
        selected_event = None
        while selected_event == None:
            event_msg = await client.wait_for("message", check=check)  # Waits for user input
            event_msg = event_msg.content  # Strips message to just the text the user entered
            if event_msg == 'exitupdate':
                break
            selected_event = next((item for item in events if item["name"] == event_msg), None)
            if selected_event == None:
                await channel.send("Looks like you entered event name that does not exists in our record. Please enter a valid event name or exit by entering 'exitupdate'")
        if selected_event:
            valid_update = False
            await channel.send("Please enter the updated event information in following format:\n" + json.dumps(selected_event) + "\nor enter exit update to exit")
            while not valid_update:
                try:
                    updated_event = await client.wait_for("message", check=check)  # Waits for user input
                    updated_event = updated_event.content  # Strips message to just the text the user entered
                    if updated_event == 'exitupdate':
                        break
                    updated_event = json.loads(updated_event)
                    print(events)
                    events.remove(selected_event)
                    events.append(updated_event)
                    print(events)
                    valid_update = True
                except ValueError:
                    await channel.send("Please enter valid updated event information in following format:\n" + json.dumps(selected_event) + "\nor enter 'exitupdate' to exit")
            
            
            
            
            
            
            
            
            
            
            
            
            
# attribute_selection_message = "Please enter any of the following number:\n1 to update name\n2 to update start date & time\n3 to update end date & time\n4 to update description\n5 to update type"
# await channel.send(attribute_selection_message)
# attribute_to_update = await client.wait_for("message", check=check)  # Waits for user input
# attribute_to_update = attribute_to_update.content
# invalid_attribute = False
# while not attribute_to_update.isnumeric() or int(attribute_to_update)<1 or int(attribute_to_update)>5:
#     await channel.send("Looks like you entered invalid attribute number. Please enter a valid attribute number for update or exit by entering 'exitupdate'\n" + attribute_selection_message)
#     attribute_to_update = await client.wait_for("message", check=check)  # Waits for user input
#     attribute_to_update = attribute_to_update.content  # Strips message to just the text the user entered
#     if attribute_to_update == 'exitupdate':
#         break

# if attribute_to_update == '1':
#     await channel.send("Please enter new name for the selected event")
#     new_name = await client.wait_for("message", check=check)
#     new_name = attribute_to_update.content
        