import datetime
import json

import discord
from Event import Event
from functionality.shared_functions import read_event_file, create_event_tree, update_event_from_file


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
    channel = await ctx.author.create_dm()

    # check to verify author and channel of the message
    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    # Open and read user's calendar file
    create_event_tree(str(ctx.author.id))
    rows = read_event_file(str(ctx.author.id))

    # Initialize variables
    channel = await ctx.author.create_dm()
    event = {'name': '', 'startDateTime': '', 'endDateTime': '', 'priority': '', 'type': '', 'notes': ''}
    events = []
    eventFlag = False

    # If there are events in the file
    if len(rows) > 1:
        # For every row in calendar file
        for row in rows[1:]:
            # Get event details
            event['name'] = row[1]
            event['startDateTime'] = row[2]
            event['endDateTime'] = row[3]
            event['priority'] = row[4]
            event['type'] = row[5]
            event['notes'] = row[6]

            events.append(event)

            # send event information to user
            embed = discord.Embed(colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at,
                                  title="Event from your schedule:")
            embed.set_footer(text=f"Requested by {ctx.author}")
            if event['name']:
                embed.add_field(name="Event Name:", value=event['name'], inline=False)
            if event['startDateTime']:
                embed.add_field(name="Start Date & Time:", value=event['startDateTime'], inline=True)
            if event['endDateTime']:
                embed.add_field(name="End Date & Time:", value=event['endDateTime'], inline=True)
            if event['priority']:
                embed.add_field(name="Priority:", value=event['priority'], inline=False)
            if event['type']:
                embed.add_field(name="Event Type:", value=event['type'], inline=True)
            if event['notes']:
                embed.add_field(name="Description:", value=event['notes'], inline=False)
            await ctx.send(embed=embed)

            # reset event dict
            event = {'name': '', 'startDateTime': '', 'endDateTime': '', 'priority': '', 'type': '', 'notes': ''}

    else:
        # sending error message for empty schedule
        eventFlag = True
        embed = discord.Embed(
            description="Looks like your schedule is empty. You can add events using the `!schedule` command!",
            colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)

    if not eventFlag:
        embed = discord.Embed(
            description="Please enter the name of the event you want to edit or exit update using `exitupdate`",
            colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=embed)
        selected_event = None

        # loop while user enters a valid event name for update or while user exits update
        while selected_event == None:
            event_msg = await client.wait_for("message", check=check)  # Waits for user input
            event_msg = event_msg.content  # Strips message to just the text the user entered

            if event_msg.lower() == 'exitupdate':  # user exited update
                embed = discord.Embed(description="`!editevent` command exited successfully!",
                                      colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)
                break

            selected_event = next((item for item in events if item["name"] == event_msg),
                                  None)  # finds event with given name or returns None if not present

            if selected_event == None:
                # ask user to re-enter valid event name or exit command
                embed = discord.Embed(
                    description="Looks like you entered event name that does not exists in your schedule. Please enter a valid event name or exit by entering `exitupdate`",
                    colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)

        # get updated information for the event        
        if selected_event:
            valid_update = False
            embed = discord.Embed(
                description="Please enter the updated event information in following format:\n\n`" + json.dumps(
                    selected_event) + "`\n\nor enter `exitupdate` to exit update", colour=discord.Colour.dark_red(),
                timestamp=ctx.message.created_at)
            embed.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=embed)
            while not valid_update:
                try:
                    updated_event = await client.wait_for("message", check=check)  # Waits for user input
                    updated_event = updated_event.content  # Strips message to just the text the user entered
                    if updated_event == 'exitupdate':
                        break
                    updated_event = json.loads(updated_event)  # load updated event info in dict
                    events.remove(selected_event)
                    events.append(updated_event)
                    valid_update = True
                except ValueError:
                    embed = discord.Embed(
                        description="Please enter valid updated event information in following format:\n\n`" + json.dumps(
                            selected_event) + "`\n\nor enter `exitupdate` to exit update",
                        colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
                    embed.set_footer(text=f"Requested by {ctx.author}")
                    await ctx.send(embed=embed)

            # update user file with the updated event information        
            if valid_update:
                updated_event_name = updated_event['name']
                updated_event = Event(updated_event['name'],
                                      datetime.datetime.strptime(updated_event['startDateTime'], '%Y-%m-%d %H:%M:%S'),
                                      datetime.datetime.strptime(updated_event['endDateTime'], '%Y-%m-%d %H:%M:%S'),
                                      updated_event['priority'], updated_event['type'], updated_event['notes'])
                update_event_from_file(str(ctx.author.id), selected_event, updated_event)
                embed = discord.Embed(description="Event `" + updated_event_name + "` updated successfully!",
                                      colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)

            # exit update command    
            else:
                embed = discord.Embed(description="`!editevent` command exited successfully!",
                                      colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at)
                embed.set_footer(text=f"Requested by {ctx.author}")
                await ctx.send(embed=embed)
