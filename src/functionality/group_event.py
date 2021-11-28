import discord

from src.functionality.shared_functions import create_event_tree, create_type_tree, add_event_to_file, turn_types_to_string
from types import TracebackType
from src.Event import Event
from src.parse.match import parse_period
from src.functionality.create_event_type import create_event_type
from src.functionality.AddEvent import check_complete
from src.parse.match import parse_period24


def check_complete(start, start_date, end, end_date, array):
    if start and end:
        print("Both date objects created")
        array.append(start_date)
        array.append(end_date)
        return True
    else:
        return False


async def add_event2(ctx, client):
    """
    Function:
        add_event2
    Description:
        Walks a user through the event creation process
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - returns an array of the event's information
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = []
    await channel.send("Lets add an event!\n" + "First give me the name of your event:")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered
    event_array.append(event_msg)
    await channel.send(
        "Now give me the start & end dates for you event. "
        + "You can use 12-hour formatting or 24-hour formatting\n\n"
        + "Here is the format you should follow (Start is first, end is second):\n"
        + "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm (12-hour formatting)\n"
        + "Or mm/dd/yy hh:mm mm/dd/yy hh:mm (24-hour formatting)"

    )
    if event_msg == "exit" or event_msg == "quit":
        return None

    event_dates = False
    # A loop that keeps running until a user enters correct start and end dates for their event following the required format
    # Adds start and end dates to the array if both are valid
    while not event_dates:
        date_array = []
        msg_content = ""
        start_complete = False
        end_complete = True
        if ctx.message.author != client.user:
            # Waits for user input
            event_msg = await client.wait_for("message", check=check)
            # Strips message to just the text the user entered
            msg_content = event_msg.content

        if event_msg == "exit" or event_msg == "quit":
            return None

        # print(" yesa  " + str(msg_content))
        if msg_content.__contains__("am") or msg_content.__contains__("pm") or msg_content.__contains__ \
                ("AM") or msg_content.__contains__("PM"):
            try:
                parse_result = parse_period(msg_content)
            except Exception as e:
                await channel.send(
                    "Looks like "
                    + str(e)
                    + ". Please re-enter your dates.\n"
                    + "Here is the format you should follow (Start is first, end is second):\n"
                    + "mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
                start_complete = False
                continue

            start_complete = True

            # print("Lets see for 12 hr it now " + str(parse_result))

            start_date = parse_result[0]
            end_date = parse_result[1]

            # If both datetime objects were successfully created, they get appended to the list and exits the while loop
            if not (event_dates := check_complete(start_complete, start_date, end_complete, end_date, event_array)):
                # If both objects were unsuccessfully created, the bot notifies the user and the loop starts again
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): mm/dd/yy hh:mm am/pm mm/dd/yy hh:mm am/pm"
                )
                date_array = []
                msg_content = ""

        # 24hr format
        elif  msg_content.__contains__("exit") or  msg_content.__contains__("quit"):
            return None
        else:
            try:
                parse_result = parse_period24(msg_content)
            except Exception as e:
                await channel.send(
                    "Looks like "
                    + str(e)
                    + ". Please re-enter your dates.\n"
                    + "Here is the format you should follow (Start is first, end is second):\n"
                    + "mm/dd/yy hh:mm mm/dd/yy hh:mm "
                )
                start_complete = False
                continue

            start_complete = True

            # print("Lets see it now " + str(parse_result))
            start_date = parse_result[0]
            end_date = parse_result[1]


            # If both datetime objects were successfully created, they get appended to the list and exits the while loop
            if not (event_dates := check_complete(start_complete, start_date, end_complete, end_date, event_array)):
                # If both objects were unsuccessfully created, the bot notifies the user and the loop starts again
                await channel.send(
                    "Make sure you follow this format(Start is first, end is second): mm/dd/yy hh:mm mm/dd/yy hh:mm"
                )
                date_array = []
                msg_content = ""

    # A loop to error check when user enters priority value
    event_priority_set = False
    while not event_priority_set:
        await channel.send(
            "How important is this event? Enter a number between 1-5.\n\n" +
            "5 - Highest priority.\n" +
            "4 - High priority.\n" +
            "3 - Medium priority.\n" +
            "2 - Low priority.\n" +
            "1 - Lowest priority.\n"
        )

        event_msg = await client.wait_for("message", check=check)  # Waits for user input
        event_msg = event_msg.content  # Strips message to just the text the user entered

        try:
            if 1 <= int(event_msg) <= 5:
                event_array.append(event_msg)
                event_priority_set = True  # if entered value is in the range, loop exits
            else:
                await channel.send(
                    "Please enter a number between 1-5\n")
        except:
            await channel.send(
                "Please enter a number between 1-5\n")  # Handles when user enters non numeric entries
            continue

    create_type_tree(str(ctx.author.id))
    output = turn_types_to_string(str(ctx.author.id))
    await channel.send(
        "Tell me what type of event this is. Here are a list of event types I currently know:\n" + output
    )
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered

    if event_msg == "exit" or event_msg == "quit":
        return None

    await create_event_type(ctx, client, event_msg)  # Running event_type creation subroutine
    event_array.append(event_msg)
    await channel.send("Any additional description you want me to add about the event? If not, enter 'done'")
    event_msg = await client.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered

    if event_msg == "exit" or event_msg == "quit":
        return None

    if event_msg.lower() == "done":
        event_array.append("-")
    else:
        event_array.append(event_msg)

    # Tries to create an Event object from the user input
    try:
        current = Event(event_array[0], event_array[1], event_array[2], event_array[3], event_array[4], event_array[5])
        await channel.send("Your event was successfully created!")
        create_event_tree(str(ctx.author.id))
        add_event_to_file(str(ctx.author.id), current)
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)
        TracebackType.print_exc()
        await channel.send(
            "There was an error creating your event. Make sure your formatting is correct and try creating the event again."
        )

    return event_array

async def group_event(ctx, client, user, emoji):
    """
    Function:
        group_event
    Description:
        creates a group event by posting a message to the channel and waiting for user input with clickable reactions
    Input:
        ctx - Discord context window
        client - Discord bot user
        user - Discord user
        emoji - Discord emoji
    Output:
        - returns an array of the event's information
        - A new post is created in the channel with an embed showing the event's information
    """
    arr = await add_event2(ctx, client)
    em = discord.Embed(
        title="Group Event Created!",
        description="If you would Like to be notified of this event, please click on the " + emoji,
    )
    em.add_field(name="Name", value=str(arr[0]), inline=False)
    em.add_field(name="Start", value=str(arr[1]), inline=False)
    em.add_field(name="End", value=str(arr[2]), inline=False)
    em.add_field(name="Priority", value=str(arr[3]), inline=True)
    em.add_field(name="Type", value=str(arr[4]), inline=True)
    em.add_field(name="Additional Info", value=str(arr[5]), inline=False)

    for guild in client.guilds:
        temp = await guild.fetch_member(ctx.author.id)
        if temp is not None:
            for channel in guild.text_channels:
                if channel.name == "general":
                    msg = await channel.send(embed=em)
                    await msg.add_reaction(emoji)

    return arr

async def add_others_event(user, event_array):
    """
    Function:
        add_others_event
    Description:
        adds an event to the event tree for a user
    Input:
        user - Discord user
        event_array - array of event information
    Output:
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """
    create_type_tree(str(user.id))
    # Tries to create an Event object from the user input
    try:
        current = Event(event_array[0], event_array[1], event_array[2], event_array[3], event_array[4], event_array[5])
        await user.send("Your event was successfully created!")
        create_event_tree(str(user.id))
        add_event_to_file(str(user.id), current)
    except Exception as e:
        # Outputs an error message if the event could not be created
        print(e)
        TracebackType.print_exc()
        await user.send(
            "There was an error creating your event. Make sure your formatting is correct and try creating the event again."
        )

