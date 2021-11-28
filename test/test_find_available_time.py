import os
import sys
from datetime import datetime

import discord
import discord.ext.commands as commands
import discord.ext.test as test
import pytest
from Event import Event
from functionality.FindAvailableTime import getEventsOnDate
from functionality.shared_functions import create_event_tree, add_event_to_file



# @pytest.mark.asyncio
# async def test_get_events_on_date(bot, client):
#     guild = bot.guilds[0]
#     channel = guild.text_channels[0]
#     message = await channel.send("!day")
#
#     start = datetime(2021, 9, 30, 0, 0)
#     end = datetime(2021, 9, 30, 23, 59)
#
#     current = Event("SE project", start, end, 2, "homework", "Finish it")
#     create_event_tree(str(message.author.id))
#     add_event_to_file(str(message.author.id), current)
#
#     getEventsOnDate(message, start)
