import re
import os
import csv
from datetime import datetime
from types import TracebackType
from src.event_type import event_type
from src.functionality.shared_functions import create_type_directory, create_type_file
from src.functionality.shared_functions import load_key, decrypt_file, encrypt_file
import traceback


async def create_event_type(ctx, client, event_msg, hr_min_array):
    """
    Function:
        create_event_type
    Description:
        Walks a user through the creation of types of event or updating time range for existing event types
    Input:
        ctx - Discord context window
        client - Discord bot user
    Output:
        - A new event type added to the user's calendar file or the time range will be update for the existing event type
        - A message sent to the context saying an event type was successfully added or updated
    """

    channel = await ctx.author.create_dm()
    print(ctx.author.id)

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    event_array = [event_msg]
    start_time = datetime.strptime(hr_min_array[0], "%H:%M:%S")
    print(start_time)
    end_time = datetime.strptime(hr_min_array[1], "%H:%M:%S")
    print(end_time)
    event_array.append(start_time)
    event_array.append(end_time)
    try:
        current = event_type(event_array[0], event_array[1], event_array[2])
        # Creates ScheduleBot directory in users Documents folder if it doesn't exist
        create_type_directory()
        filename = str(ctx.author.id) + 'event_types'
        # Checks if the calendar csv file exists, and creates it if it doesn't
        create_type_file(str(ctx.author.id))
        key = load_key(str(ctx.author.id))
        decrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv")
        # Opens the current user's csv calendar file
        with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "r"
        ) as calendar_lines:
            calendar_lines = csv.reader(calendar_lines, delimiter=",")
            fields = next(calendar_lines)  # The column headers will always be the first line of the csv file
            rows = []
            line_number = 0
            flag = 0
            # Stores the current row in an array of rows if the row is not a new-line character
            # This check prevents an accidental empty lines from being kept in the updated file
            for line in calendar_lines:
                if len(line) > 0:
                    # If the file already has the same event type then inform user and exit loop
                    if line[0] == current.event_name:
                        flag = 1
                        if str(line[1]) == current.get_start_time() and str(line[2]) == current.get_end_time():
                            rows.append(line)
                            line_number = line_number + 1
                            await channel.send("Event type: " + str(line[0]) + " already exist in the given time range")
                            continue
                        await channel.send("Event type: " + str(
                            line[0]) + " already exist.\n Existing time range for this event type is " + str(
                            line[1]) + " " + str(line[
                                                     2]) + "\n The new time range entered now is " +
                                           current.get_start_time() + " " + current.get_end_time() +
                                           ". \n Please type 'change' for updating the time range "
                                           "or 'exit' for keeping existing time range.")
                        # Waits for user input
                        event_msg = await client.wait_for("message", check=check)
                        # Strips message to just the text the user entered
                        msg_content = event_msg.content
                        if msg_content == 'change':
                            rows.append(current.to_list_event())
                            await channel.send("The time range for your event was successfully updated!")
                            line_number = line_number + 1
                        elif msg_content == 'exit':
                            rows.append(line)
                            continue
                        else:
                            await channel.send("Invalid input, Time range is not changed.")
                            rows.append(line)
                            continue
                    else:
                        rows.append(line)
                        line_number = line_number + 1

            # If this is a new even type then append it to rows
            if flag == 0:
                rows.append(current.to_list_event())
                line_number = line_number + 1
                await channel.send("Your event was successfully created!")

        # Open current user's calendar file for writing
        with open(
                os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv", "w", newline=""
        ) as calendar_file:
            # Write to column headers and array of rows back to the calendar file
            csvwriter = csv.writer(calendar_file)
            csvwriter.writerow(fields)
            if line_number > 1:
                csvwriter.writerows(rows)
            elif line_number == 1:
                csvwriter.writerow(rows[0])

        key = load_key(str(ctx.author.id))
        encrypt_file(key, os.path.expanduser("~/Documents") + "/ScheduleBot/Type/" + str(filename) + ".csv")

        return True

    except Exception as e:
        # Outputs an error message if the event type could not be created
        print(e)
        traceback.print_exc()
        await channel.send(
            "There was an error while adding this event type. "
            "Make sure your formatting is correct and try creating the event type again."
        )
        return False
