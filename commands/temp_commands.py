import discord
import datetime
import pytz
from methods.embed import create_embed


async def stress(ctx, client):
    eng_round = datetime.datetime(2021, 3, 31, 12, 0, 0, 0)
    eng_round = eng_round.astimezone(pytz.timezone("US/Eastern"))

    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.UTC)
    now = now.astimezone(pytz.timezone("US/Eastern"))

    difference = eng_round - now
    seconds = difference.seconds
    hours = seconds // 60 // 60
    seconds -= hours * 60 * 60
    mins = seconds // 60
    seconds -= mins * 60

    embed = create_embed(
        "Engineering Round",
        f"There is {difference.days} days {hours} hours and {mins} minutes until the Engineering Round.  Time to cope :)",
        "orange",
    )
    await ctx.channel.send(embed=embed)