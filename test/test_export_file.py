import os
import sys
import pytest
from functionality.export_file import export_file  # type: ignore

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))


# @pytest.mark.asyncio
# async def test_export_file(bot, client):
#     guild = bot.guilds[0]
#     channel = guild.text_channels[0]
#     message = await channel.send("!exportfile")
#
#     await export_file(message)
