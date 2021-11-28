import io
import discord
import matplotlib.pyplot as plt
import numpy as np
from functionality.shared_functions import read_event_file, create_event_tree

async def retrieve_event(ctx, client):
    """
    Function:
        retrieve_event
    Description:
        All existing events are retrieved from the user's schedule file
    Input:
        ctx: the current context
        client: the instance of the bot
    Output:
        - A pie chart showing the time the user has scheduled an event for.
    """

    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel and m.author == ctx.author

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
            event['startTime'] = start[1][:-3]
            end = row[3].split()
            event['endDate'] = end[0]
            event['endTime'] = end[1][:-3]
            event['type'] = row[4]
            event['desc'] = row[5]
            # dates = [event['startDate'], event['endDate']]

            events.append(event)

            # reset event
            event = {'name': '', 'startDate': '', 'startTime': '', 'endDate': '', 'endTime': '', 'type': '', 'desc': ''}

        time = []
        status = []
        if len(events) != 0:
            for e in events:
                time.append(e['startTime'])
                time.append(e['endTime'])
                status.append("Start of " + e['name'])
                status.append("End of " + e['name'])

        # Choose some nice levels
        levels = np.tile([-5, 5, -3, 3, -1, 1],
                         int(np.ceil(len(time) / 6)))[:len(time)]

        # Create figure and plot a stem plot with the date
        fig, ax = plt.subplots(figsize=(8.8, 4), constrained_layout=True)
        ax.set(title="Scheduled Events")

        markerline, stemline, baseline = ax.stem(time, levels,
                                                 linefmt="C3-", basefmt="k-",
                                                 use_line_collection=True)

        plt.setp(markerline, mec="k", mfc="w", zorder=3)

        # Shift the markers to the baseline by replacing the y-data by zeros.
        markerline.set_ydata(np.zeros(len(time)))

        # annotate lines
        vert = np.array(['top', 'bottom'])[(levels > 0).astype(int)]
        for d, l, r, va in zip(time, levels, status, vert):
            ax.annotate(r, xy=(d, l), xytext=(-3, np.sign(l) * 3),
                        textcoords="offset points", va=va, ha="right")

        # format xaxis with 4 month intervals
        # ax.get_xaxis().set_major_locator(mdates.MonthLocator(interval=4))
        # ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

        # remove y axis and spines
        ax.get_yaxis().set_visible(False)
        for spine in ["left", "top", "right"]:
            ax.spines[spine].set_visible(False)

        ax.margins(y=0.1)

        embed = discord.Embed(colour=discord.Colour.dark_red(), timestamp=ctx.message.created_at,
                              title="Your Scheduled Events:")
        plt.savefig('graph.png', transparent=False)
        plt.close(fig)

        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        image = discord.File(file, filename='graph.png')
        embed.set_image(url=f'attachment://graph.png')

        await ctx.send(file=image, embed=embed)
