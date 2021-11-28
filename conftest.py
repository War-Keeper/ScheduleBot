import os
import sys
import discord
import discord.ext.commands as commands
import discord.ext.test as test
import pytest
from discord import Intents
from setuptools import glob

intents = Intents.all()
intents.members = True
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../src"))



# Default parameters for the simulated dpytest bot. Loads the bot with commands from the /cogs directory
# Ran everytime pytest is called

@pytest.fixture
def client(event_loop):
    c = discord.Client(loop=event_loop)
    test.configure(c)
    return c


@pytest.fixture
def bot(request, event_loop):

    b = commands.Bot("!", loop=event_loop, intents=intents)

    # marks = request.function.pytestmark
    # mark = None
    # for mark in marks:
    #     if mark.name == "cogs":
    #         break
    #
    # if mark is not None:
    #     for extension in mark.args:
    #         b.load_extension("tests.internal." + extension)
    test.configure(b)
    return b

# Cleans up leftover files generated through dpytest
def pytest_sessionfinish():
    # Clean up attachment files
    files = glob.glob('./dpytest_*.dat')
    for path in files:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error while deleting file {path}: {e}")
    print("\npySession closed successfully")

# Copyright (c) 2021 War-Keeper
