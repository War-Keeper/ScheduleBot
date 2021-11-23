import math
import traceback
from calendar import monthrange
from datetime import datetime

from discord_components import Select, SelectOption

from src.Event import Event
from src.functionality.create_event_type_easier import create_event_type
from src.functionality.shared_functions import create_event_tree, create_type_tree, add_event_to_file, \
    turn_types_to_string

BOT = None


async def grab_date(ctx, client, event_array, hr_min_array):
    # Get the event month
    await ctx.send(
        'Select the Event Month',
        components=[
            Select(
                placeholder='Select a month',
                options=[SelectOption(label='January', value='1'), SelectOption(label='February', value='2'),
                         SelectOption(label='March', value='3'), SelectOption(label='April', value='4'),
                         SelectOption(label='May', value='5'), SelectOption(label='June', value='6'),
                         SelectOption(label='July', value='7'), SelectOption(label='August', value='8'),
                         SelectOption(label='September', value='9'), SelectOption(label='October', value='10'),
                         SelectOption(label='November', value='11'), SelectOption(label='December', value='12')
                         ]
            )
        ]
    )
    monthInteraction = await client.wait_for('select_option',
                                             check=lambda x: x.values[0] in (
                                                 '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'))
    # Prevents "Interaction failed" message
    if monthInteraction.channel == ctx.channel:
        await monthInteraction.respond(content=f"{monthInteraction.values[0]} selected")
    month = monthInteraction.values[0]
    month_num = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12').index(
        month) + 1
    # Get the event day, varies depending on the number of days in the month
    num_days = monthrange(datetime.now().year, month_num)[1]
    dayOptionArray = []
    dayStringArray = []
    for i in range(0, num_days):
        dayOptionArray.append(SelectOption(label=str(i), value=str(i)))
        dayStringArray.append(str(i))
    dayStringArray.append((str(num_days)))
    dayOptionArray.append((SelectOption(label=str(num_days), value=str(num_days))))
    dayArrayHalf1 = dayOptionArray[:len(dayOptionArray) // 2]
    dayArrayHalf2 = dayOptionArray[len(dayOptionArray) // 2:]
    await ctx.send(
        f'Select the Event Day: 1-{str(math.floor(num_days / 2))}',
        components=[
            Select(
                placeholder='Select a day',
                options=dayArrayHalf1
            )
        ]
    )
    await ctx.send(
        f'or {str(math.floor((num_days / 2)) + 1)} - {str(num_days)}',
        components=[
            Select(
                placeholder='Select a day',
                options=dayArrayHalf2
            )
        ]
    )
    dayInteraction = await client.wait_for('select_option', check=lambda x: x.values[0] in dayStringArray)
    # Prevents "Interaction failed" message
    if dayInteraction.channel == ctx.channel:
        await dayInteraction.respond(content=f"{dayInteraction.values[0]} selected")
    day = dayInteraction.values[0]
    # Get the start hour (24hr) time
    hrOptionArray = []
    hrStringArray = []
    for i in range(0, 24):
        hrOptionArray.append(SelectOption(label=str(i), value=str(i)))
        hrStringArray.append(str(i))
    await ctx.send(
        f'Select the Event hour in 24hr time',
        components=[
            Select(
                placeholder='Select the event hour',
                options=hrOptionArray
            )
        ]
    )
    # Prevents "Interaction failed" message
    hrInteraction = await client.wait_for('select_option', check=lambda x: x.values[0] in hrStringArray)
    if hrInteraction.channel == ctx.channel:
        await hrInteraction.respond(content=f"{hrInteraction.values[0]} selected")
    hr = hrInteraction.values[0]

    # Get the event minute
    minOptionArray = []
    minStringArray = []
    for i in range(0, 60, 5):
        minOptionArray.append(SelectOption(label=str(i), value=str(i)))
        minStringArray.append(str(i))
    await ctx.send(
        f'Select the Event minute corresponding to the hour',
        components=[
            Select(
                placeholder='Select the event minute',
                options=minOptionArray
            )
        ]
    )
    # Prevents "Interaction failed" message
    minInteraction = await client.wait_for('select_option', check=lambda x: x.values[0] in minStringArray)
    if minInteraction.channel == ctx.channel:
        await minInteraction.respond(content=f"{minInteraction.values[0]} selected")
    minute = minInteraction.values[0]
    if int(month) < 10:
        month = "0" + month
    if int(day) < 10:
        day = "0" + day
    date = str(datetime.now().year) + "-" + month + "-" + day + " " + hr + ":" + minute + ":00"
    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    event_array.append(date)
    # append the hr and minute time to the hrMinArray for use later by create_event_easier
    hr_min_array.append(hr + ":" + minute + ":00")


async def add_event(ctx, client):
    """
    Function:
        add_event
    Description:
        Walks a user through the event creation process
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []
    # Track the hr:min start and end time of the Event, for use by create_event_type_easier
    hrMinArray = []
    await channel.send("Lets add an event!\n" + "First give me the name of your event:")  # Get the name of the event
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    event_array.append(event_msg)  # Append the name to the event array
    await ctx.send("First let's select the start date:")  # Query the start date of the Event
    await grab_date(ctx, client, event_array, hrMinArray)  # Get the start date of the Event

    await ctx.send(
        'Does this Event end on the same date, or later?',
        components=[
            Select(
                placeholder='Pick an end date',
                options=[SelectOption(label='Later', value='1'), SelectOption(label='Same date', value='2')]
            )
        ]
    )
    endDateInteraction = await client.wait_for('select_option',
                                               check=lambda x: x.values[0] in ('1', '2'))
    # Prevents "Interaction failed" message
    if endDateInteraction.channel == ctx.channel:
        await endDateInteraction.respond(content=f"{endDateInteraction.values[0]} selected")
    endDateChoice = endDateInteraction.values[0]
    if int(endDateChoice) == 1:
        await ctx.send("Please select the end date for the event")
        await grab_date(ctx, client, event_array, hrMinArray)
    else:

        event_array.append(event_array[len(event_array) - 1])
        hrMinArray.append(hrMinArray[len(hrMinArray) - 1])
    print(event_array)
    # Get the priority of the Event
    await ctx.send(
        'How important is this event? Pick a number between 1-5',
        components=[
            Select(
                placeholder='Pick a priority',
                options=[
                    SelectOption(label='5 - Highest priority.', value='5'),
                    SelectOption(label='4 - High priority.', value='4'),
                    SelectOption(label='3 - Medium priority.', value='3'),
                    SelectOption(label='2 - Low priority.', value='2'),
                    SelectOption(label='1 - Lowest priority.', value='1'),
                ]
            )
        ]
    )
    priorityInteraction = await client.wait_for('select_option',
                                                check=lambda x: x.values[0] in ('1', '2', '3', '4', '5'))
    # Prevents "Interaction failed" message
    if priorityInteraction.channel == ctx.channel:
        await priorityInteraction.respond(content=f"{priorityInteraction.values[0]} selected")
    priority = priorityInteraction.values[0]
    event_array.append(priority)

    create_type_tree(str(ctx.author.id))
    output = turn_types_to_string(str(ctx.author.id))
    await channel.send(
        "Tell me what type of event this is. Here are a list of event types I currently know:\n" + output
    )
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    await create_event_type(ctx, client, event_msg, hrMinArray)  # Running event_type creation subroutine
    event_array.append(event_msg)
    await channel.send("Any additional description you want me to add about the event? If not, enter 'done'")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    if event_msg.lower() == "done":
        event_array.append("")
    else:
        event_array.append(event_msg)

    # Tries to create an Event object from the user input
    try:
        current = Event(event_array[0], event_array[1], event_array[2], event_array[3], event_array[4], event_array[5])
        print(event_array)
        await channel.send("Your event was successfully created!")
        print(current)
        create_event_tree(str(ctx.author.id))
        add_event_to_file(str(ctx.author.id), current)
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)
        traceback.print_exc()
        await channel.send(
            "There was an error creating your event. "
            "Make sure your formatting is correct and try creating the event again."
        )
