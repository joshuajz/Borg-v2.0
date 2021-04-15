import discord
import shlex
from methods.embed import create_embed, add_field
from methods.database import database_connection
from functools import reduce
import datetime


async def warn(ctx, client):
    # TODO: Add support for ids
    if ctx.author.guild_permissions.administrator != True:
        return

    content = shlex.split(ctx.content)
    db = await database_connection(ctx.guild.id)

    if len(content) <= 2:
        embed = create_embed("!warn", "!warn {user} {reason here}", "orange")
        add_field(embed, "user", "@ the user you'd like to warn", True)
        add_field(embed, "reason", "The reason you're warning the user.", True)
        await ctx.channel.send(embed=embed)
        return

    user_id = content[1][3:-1]
    reason = "".join(content[2::])

    db["db"].execute(
        "INSERT INTO infractions (datetime, type, user_id, moderator_id, reason) VALUES (?, ?, ?, ?, ?)",
        (
            str(datetime.datetime.now()),
            "warn",
            int(user_id),
            int(ctx.author.id),
            reason,
        ),
    )
    db["con"].commit()

    warned_user = client.get_user(int(user_id))

    embed = create_embed(
        f"{warned_user} has been warned for: {reason}", "", "light_green"
    )
    await ctx.channel.send(embed=embed)


async def userinfo(ctx, client):
    # TODO: User ID support
    content = shlex.split(ctx.content)

    if len(content) != 2:
        embed = create_embed("!user_info", "!user_info {user}", "orange")
        add_field(
            embed, "user", "@ the user you'd like to display furthur information.", True
        )
        await ctx.channel.send(embed=embed)
        return

    user_id = content[1][3:-1]

    user_targeted = client.get_user(int(user_id))
    user_targeted_member = ctx.guild.get_member(int(user_id))
    embed = create_embed(str(user_targeted), user_targeted.mention, "magenta")
    embed.set_thumbnail(url=user_targeted.avatar_url)
    add_field(
        embed,
        "Joined",
        f"{user_targeted_member.joined_at.strftime('%a, %b %d, %Y %I:%M %p')}",
        True,
    )
    add_field(
        embed,
        "Account Created",
        user_targeted_member.created_at.strftime("%a, %b %d, %Y %I:%M %p"),
        True,
    )

    roles = user_targeted_member.roles
    role_amount = len(roles)
    roles_string = ", ".join([i.mention for i in roles])

    add_field(embed, f"Roles [{role_amount}]", roles_string, False)
    await ctx.channel.send(embed=embed)


async def infractions(ctx, client):
    print("temp")


async def oldpurge(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return
    
    if ctx.content.split(" ")[1].lower() == "photo":
        yes = lambda x : True in tuple(map(lambda y : y.content_type.split("/")[0] == "image", x.attachments))

        try:
            purge_amount = int(ctx.content.split(" ")[2])
            deleted_amount = len(await ctx.channel.purge(limit=purge_amount, check=yes, bulk=True))

            await ctx.channel.send("Purged " + str(deleted_amount) + " photo(s)") 
        except:
            try:
                deleted_amount = len(await ctx.channel.purge(limit=pow(2,63)-1, check=yes, bulk=True))
                await ctx.channel.send("Purged " + str(deleted_amount) + " photo(s)")
            except:
                await ctx.channel.send("Error, unsuccessful purge")
        return
    
    if ctx.content.split(" ")[1].lower() == "user":
        try:
            users = tuple(map(lambda x : x.id, ctx.mentions))
            yes = lambda x : x.author.id in users

            for i in range(len(users)):
                purge_amount = int(ctx.content.split(" ")[2])
                deleted_amount = len(await ctx.channel.purge(limit=purge_amount, check=yes, bulk=True))

                await ctx.channel.send("Purged " + str(deleted_amount) + " messages(s)") 
        except:
            try:
                deleted_amount = len(await ctx.channel.purge(limit=pow(2,63)-1, check=yes, bulk=True))
                await ctx.channel.send("Purged " + str(deleted_amount) + " messages(s)")  
            except:
                await ctx.channel.send("Error, unsuccessful purge")
        return
    
    try:
        purge_amount = int(ctx.content.split(" ")[1])

        yes = lambda x : True
        deleted_amount = len(await ctx.channel.purge(limit=purge_amount, check=yes, bulk=True))

        await ctx.channel.send("Purged " + str(deleted_amount) + " message(s)")
    except:
        await ctx.channel.send("Error, unsuccessful purge or incorrect arguments") 

async def purge(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return
    
    args = ctx.content.split(" ")
    amount_of_args = len(ctx.content.split(" ")) - 2

    if amount_of_args < 0:
       await ctx.channel.send("Error, incorrect arguments")
    
    check_functions = []

    for i in range(amount_of_args):
        if args[i+1].tolower() == "photo":
            removepics = lambda x : True in tuple(map(lambda y : y.content_type.split("/")[0] == "image", x.attachments))
            check_functions.append(removepics)
            break
    
    users = tuple(map(lambda x : x.id, ctx.mentions))
    removeusers = lambda x : x.author.id in users
    check_functions.append(removeusers)

    finalcheck = lambda x : reduce(lambda init, cum : cum or init(x), check_functions, False)
    purge_amount = pow(2,63)-1 if args[amount_of_args-1].tolower() == "all" else int(args[amount_of_args-1])

    try:
        deleted_amount = len(await ctx.channel.purge(limit=purge_amount, check=finalcheck, bulk=True))
        await ctx.channel.send("Purged " + str(deleted_amount) + " message(s)")
    except:
        await ctx.channel.send("An error occured, message(s) not purged")
    
    return

