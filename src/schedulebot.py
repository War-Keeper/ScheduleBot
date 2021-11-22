import discord  # type: ignore
from discord.ext import commands  # type: ignore
import os
import json

from discord.ext.commands.help import MinimalHelpCommand
from discord_components import DiscordComponents

from functionality.AddEvent2 import add_event  # type: ignore
from functionality.highlights import get_highlight
from functionality.create_event_type import create_event_type
from functionality.FindAvailableTime import find_avaialbleTime
from functionality.delete_event_type import delete_event_type
from functionality.DisplayFreeTime import get_free_time
from functionality.export_file import export_file
from functionality.import_file import import_file
from functionality.edit_event import edit_event
from functionality.group_event import group_event, add_others_event

global groupEvent
global emojiArray
global emojiCounter
from functionality.DeleteEvent import delete_event

bot = commands.Bot(command_prefix="!")  # Creates the bot with a command prefix of '!'
bot.remove_command("help")  # Removes the help command, so it can be created using Discord embed pages later


@bot.group(invoke_without_command=True)
async def help(ctx):
    """
    Function:
        help
    Description:
        A command that allows the user to see all usable commands and their descriptions
    Input:
        ctx - Discord context window
    Output:
        An embed window sent to the context with all commands/descriptions
    """
    em = discord.Embed(
        title="ScheduleBot Commands",
        description="Here are all the commands to use ScheduleBot\nAll events are prefaced by an '!'",
    )
    em.add_field(name="help", value="Displays all commands and their descriptions", inline=False)
    em.add_field(name="schedule", value="Creates an event", inline=False)
    em.add_field(name="freetime", value="Displays when you are available today", inline=False)
    em.add_field(name="day", value="Shows everything on your schedule for a specific date\nHere is the format you "
                                   "should follow:\n!day "
                                   "today\\tomorrow\\yesterday\n!day 3 (3 days from now)\n!day -3 (3 days ago)\n!day "
                                   "4/20/22 (On Apr 20, 2022)", inline=False)
    em.add_field(name="typecreate", value="Creates a new event type", inline=True)
    em.add_field(name="typedelete", value="Deletes an event type", inline=True)
    em.add_field(name="exportfile", value="Exports a CSV file of your events", inline=False)
    em.add_field(name="importfile", value="Import events from a CSV or ICS file", inline=False)
    em.add_field(name="editevent", value="Edits the event with the new information", inline=False)
    await ctx.send(embed=em)


@bot.event
async def on_ready():
    """
    Function:
        on_ready
    Description:
        Displays a welcome message to the ScheduleBot server and allows user to receive
    a direct message from the bot by reacting to the welcome message with an alarm_clock reaction
    Input:
        None
    Output:
        The welcome message sent to the ScheduleBot server
    """
    # Outputs bot name to console once bot is started
    print("We have logged in as {0.user}".format(bot))
    channels = bot.get_all_channels()  # Gets the channels the bot is currently watching
    DiscordComponents(bot)
    text_channel_count = 0
    for channel in channels:
        if str(channel.type) != 'text':
            continue

        text_channel_count += 1
        msg = await channel.send(
            "Hello! My name is Schedule Bot and I am here to help you plan your schedule!\n\n"
            + "React to this message with a '⏰' (\:alarm_clock\:) reaction so I can direct message you!"
            + "Make sure you have allowed non-friends to direct message you or I can't help you."
        )

        await msg.add_reaction("⏰")
    print("Sent Welcome Message to", text_channel_count, "Channel(s)")


@bot.event
async def on_reaction_add(reaction, user):
    """
    Function: on_reaction_add
    Description: The bot sends a message to the user when reacting to the server startup message
    and runs the 'help' command
    Input:
        reaction - The emoji the user reacted to the message with
        user - The user who reacted to the post
    Output:
        - A welcome message received as a direct message from the bot
        - The 'help' command is automatically run
    """
    emoji = reaction.emoji
    if emoji == "⏰" and not user.bot:  # if user is not a bot...
        try:
            await user.send(
                "Nice to meet you "
                + user.name
                + "! I am ScheduleBot and I am here to make managing your schedule easier!"
            )
            await help(user)
        except:
            print(user.name + " (" + user.id + ") does not have DM permissions set correctly")
            pass

    global groupEvent
    global emojiArray
    counter = 0
    for i in emojiArray:
        if emoji == i and not user.bot:
            try:
                await add_others_event(user, groupEvent[counter])
                await user.send(
                    "Hey "
                    + user.name
                    + "! I have created the Event that you reacted to! "
                )

            except:
                print(user.name + " (" + user.id + ") does not have DM permissions set correctly")
                pass
        counter += 1

@bot.command()
async def schedule(ctx):
    """
    Function:
        schedule
    Description:
        Calls the add_event function to walk a user through the event creation process
    Input:
        ctx - Discord context window
    Output:
        - A new event added to the user's calendar file
        - A message sent to the context saying an event was successfully created
    """
    await add_event(ctx, bot)

@bot.command()
async def deleteevent(ctx):
    await delete_event(ctx, bot)


@bot.command()
async def find(ctx):
    """
    Function:
        find
    Description:
        Calls the find_avaialbleTime function to walk a user through the range associated with the given event
    Input:
        ctx - Discord context window
    Output:
        - A new event type is added to the users event_type file
        - Provides users with the time range for the given event
    """
    await find_avaialbleTime(ctx, bot)


@bot.command()
async def day(ctx, arg):
    """
    Function:
        get_highlight
    Description:
        Shows the events planned for the day by the user
    Input:
        ctx - Discord context window
        arg - User input argument
    Output:
        - A message sent to the context with all the events that start and/or end today
    """
    await get_highlight(ctx, arg)


@bot.command()
async def exportfile(ctx):
    """
    Function:
        exportfile
    Description:
        Sends the user a CSV file containing their scheduled events.
    Input:
        ctx - Discord context window
    Output:
        - A CSV file sent to the context that contains a user's scheduled events.
    """

    await export_file(ctx)


@bot.command()
async def importfile(ctx):
    """
    Function:
        importfile
    Description:
        Reads a CSV or ICS file containing events submitted by the user, and adds those events
    Input:
        ctx - Discord context window
    Output:
        - Events are added to a users profile.
    """

    await import_file(ctx, bot)


# creating new event type
@bot.command()
async def typecreate(ctx):
    channel = await ctx.author.create_dm()

    # print(ctx.author.id)
    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

    await channel.send("First give me the type of your event:")
    event_msg = await bot.wait_for("message", check=check)  # Waits for user input
    event_msg = event_msg.content  # Strips message to just the text the user entered

    await create_event_type(ctx, bot, event_msg)


# deleting event type
@bot.command()
async def typedelete(ctx):
    await delete_event_type(ctx, bot)

@bot.command()
async def editevent(ctx):
    await edit_event(ctx, bot)

@bot.command()
async def groupevent(ctx):
    global groupEvent
    global emojiCounter

    temp = await group_event(ctx, bot, ctx.author, emojiArray[emojiCounter])
    if temp is not None:
        groupEvent[emojiCounter] = temp
        emojiCounter += 1
        if emojiCounter == len(emojiArray):
            emojiCounter = 0

@bot.command()
async def freetime(ctx):
    """
    Function: freetime
    Description: shows the user their free time today according to the registered events
    Input:
        ctx - Discord context window
        bot - Discord bot user
    Output:
        - A message sent to the user channel stating every free time slot that is available today
    """
    await get_free_time(ctx, bot)


# Runs the bot (local machine)
if __name__ == "__main__":
    from config import TOKEN
    global emojiArray
    global emojiCounter
    global groupEvent
    emojiArray = ["📅", "➕", "✔", "📌", "📢"]
    emojiCounter = 0
    groupEvent = [None, None, None, None, None]
    bot.run(TOKEN)

# client.run(os.environ['TOKEN'])  # Runs the bot (repl.it)
