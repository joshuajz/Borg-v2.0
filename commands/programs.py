import discord
from methods.database import database_connection
import shlex
from methods.embed import create_embed, add_field
import re
from methods.user import find_user

# TODO: Editing


async def programs_add(ctx, client):
    content_temp = ctx.content.split(" ")
    if len(ctx.content.split(" ")) <= 1 and len(ctx.content.split("\n")) <= 1:
        embed = create_embed(
            "Programs_add",
            "!programs_add {user (optional, admin only)} Program #1, Program #2, Program #3...",
            "orange",
        )

        add_field(
            embed,
            "user",
            "Admin Only: You can supply a user and their programs for them.",
            True,
        )

        add_field(
            embed,
            "Programs",
            "You'll provide a list of programs.  Seperate each program with a comma.",
            True,
        )

        add_field(embed, "Example", "!programs_add UW - CS, UW - SE", True)

        await ctx.channel.send(embed=embed)
        return

    db = await database_connection(ctx.guild.id)

    programs_channel = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if programs_channel is None:
        embed = create_embed(
            "Error",
            "The admins have not setup !programs.  Ask them to run !programs_setup.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs_channel = int(programs_channel)

    content = "".join(list(ctx.content)[14::])

    # Finding the user_id to use
    user_id = find_user(content.split(" ")[0])
    if user_id:
        content = "".join(content.split(" ")[1::])
        if ctx.author.guild_permissions.administrator != True:
            user_id = ctx.author.id
    else:
        user_id = ctx.author.id

    add_programs = []

    if "\n" in content:
        for program in content.split("\n"):
            add_programs.append(program.strip())
        temp_list = []
        if "," in "".join(add_programs):
            for program in add_programs:
                if "," in program:
                    for p in program.split(","):
                        temp_list.append(p)
                else:
                    temp_list.append(program)

        add_programs = temp_list
    else:
        for program in content.split(","):
            add_programs.append(program.strip())

    current_programs = (
        db["db"]
        .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
        .fetchone()
    )

    embed = create_embed("Programs Verification Required", "", "magenta")
    add_field(embed, "User", client.get_user(user_id).mention, False)
    clist = ""
    if current_programs is not None:
        for p in current_programs[0].split("\n"):
            if p != "":
                clist += p + "\n"

        add_field(embed, "Current Programs", clist, True)
    plist = ""
    for p in add_programs:
        plist += p.strip() + "\n"

    add_field(embed, "Program Additions", plist, True)
    add_field(embed, "Final Programs", clist + plist, True)

    verification_msg = await client.get_channel(programs_channel).send(embed=embed)

    emojis = ["✅", "❌"]
    for emoji in emojis:
        await verification_msg.add_reaction(emoji)

    embed = create_embed(
        "Successfully Sent to Moderators",
        "Your !programs additions have been sent to the administrators for review.  Please sit tight!",
        "light_green",
    )
    add_field(embed, "User", client.get_user(int(user_id)).mention, True)
    add_field(embed, "Added Programs", plist, True)
    await ctx.channel.send(embed=embed)


async def programs_remove(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)
    if len(content) <= 1:
        embed = create_embed("Programs_remove", "!programs_remove", "red")
        await ctx.channel.send(embed=embed)

    content = ctx.content[16::]
    # Finding the user_id to use
    user_id = find_user(content.split(" ")[0])
    if user_id:
        content = "".join(content.split(" ")[1::])
        if ctx.author.guild_permissions.administrator != True:
            user_id = ctx.author.id
    else:
        user_id = ctx.author.id

    remove_list = []

    if content.strip().lower() in ["*", "all"]:
        db["db"].execute("DELETE FROM programs WHERE user_id = (?)", (user_id,))
        db["con"].commit()

        embed = create_embed("All Programs Removed Successfully", "", "dark_blue")
        await ctx.channel.send(embed=embed)

        return

    if "\n" in content:
        for i in content.split("\n"):
            if "," in i:
                for z in i.split(","):
                    remove_list.append(int(z.strip()))
            else:
                remove_list.append(int(i.strip()))
    elif "," in content:
        for i in content.split(","):
            remove_list.append(int(i.strip()))
    else:
        print(content.strip())
        remove_list = content.strip()

    # Remove duplicates
    remove_list = list(dict.fromkeys(remove_list))
    remove_list = [int(i) for i in remove_list]
    programs_raw = (
        db["db"]
        .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
        .fetchone()[0]
        .split("\n")
    )

    programs = {}
    i = 1
    for p in programs_raw:
        programs[i] = p
        i += 1

    new_programs = {key: val for key, val in programs.items() if key not in remove_list}
    description = ""
    description_display = ""
    i = 1
    space_amount = (len(new_programs) // 10) + 1
    for key, val in new_programs.items():
        if val == "":
            continue
        number = f"{i}".rjust(space_amount, " ")
        description_display += f"{number}. {val.strip()}\n"
        description += val.strip() + "\n"
        i += 1

    db["db"].execute(
        "UPDATE programs SET description = (?) WHERE user_id = (?)",
        (description, user_id),
    )
    db["con"].commit()

    embed = create_embed("New Programs List", description_display, "dark_blue")
    await ctx.channel.send(embed=embed)


async def programs(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Programs", "!programs {user}", "orange")
        add_field(
            embed, "user", "The user's programs you'd like to see. (ie. @JZ)", True
        )
        await ctx.channel.send(embed=embed)
        return

    # user_id = content[1][3:-1]
    # Finding the user_id to use
    user_id = find_user(content[1])

    db["db"].execute("SELECT * FROM programs WHERE user_id = (?)", (user_id,))

    user_data = db["db"].fetchone()

    if user_data is None:
        embed = create_embed(
            "Error",
            "That user hasn't created a !programs.  Create one with !programs_add",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs = user_data[1].split("\n")

    message = "```\n"
    space_amount = (len(programs) // 10) + 1
    for program in range(len(programs)):
        if programs[program] != "":
            number = f"{program + 1}".rjust(space_amount, " ")
            message += f"{number}. {programs[program]}\n"
    message += "```"

    embed = create_embed(f"Programs", "", "orange")
    add_field(embed, "User", f"{client.get_user(int(user_id)).mention}", False)
    add_field(embed, "Programs", message, True)

    await ctx.channel.send(embed=embed)


async def programs_edit(ctx, client):
    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)
    if len(content) < 3:
        embed = create_embed("Programs_edit", "!programs_edit", "red")
        await ctx.channel.send(embed=embed)
        return

    programs_channel = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if programs_channel is None:
        embed = create_embed(
            "Error",
            "The admins have not setup !programs.  Ask them to run !programs_setup.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs_channel = int(programs_channel)

    # Finding the user_id to use
    user_id = find_user(content[1])
    if len(str(user_id)) == 18:
        program_to_edit = content[2]
        new_content = "".join(content[3::])
        if ctx.author.guild_permissions.administrator != True:
            user_id = ctx.author.id
    else:
        user_id = ctx.author.id
        program_to_edit = content[1]
        new_content = "".join(content[2::])

    current_programs = (
        db["db"]
        .execute("SELECT description FROM programs WHERE user_id = (?)", (user_id,))
        .fetchone()
    )[0]

    if current_programs is None:
        embed = create_embed(
            "You don't have a !programs",
            "Create a !programs with !programs_add before trying to edit.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs = {}
    i = 1
    for p in current_programs.split("\n"):
        programs[i] = p
        i += 1

    if int(program_to_edit) not in programs.keys():
        embed = create_embed(
            "Invalid program to edit.",
            "You've selected an invalid program to edit, try another one.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    programs[int(program_to_edit)] = new_content

    programs_print = ""
    for key, value in programs.items():
        programs_print += value + "\n"

    user = client.get_user(user_id)

    embed = create_embed("Programs Edit Verification Required", "", "magenta")
    add_field(embed, "User", user.mention, False)
    add_field(embed, "New Text", new_content, True)
    add_field(embed, "Programs", programs_print, True)

    channel = client.get_channel(programs_channel)
    verification_msg = await channel.send(embed=embed)

    emojis = ["✅", "❌"]
    for emoji in emojis:
        await verification_msg.add_reaction(emoji)

    embed = create_embed(
        "Successfully Sent to Moderators",
        "Your !programs additions have been sent to the administrators for review.  Please sit tight!",
        "light_green",
    )
    add_field(embed, "User", user.mention, True)
    add_field(embed, "Programs List", programs_print, True)
    await ctx.channel.send(embed=embed)


async def programs_setup(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return
    content = shlex.split(ctx.content)
    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Programs_setup", "!programs_setup {channel}", "orange")
        add_field(
            embed,
            "channel",
            "The channel (ie. #mod-queue) or the name of the channel (ie. mod-queue).  When a user uses !programs_add, a moderator will have to 'accept' the submission for it to be useable with !programs.",
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    channel = content[1]

    if channel[0:2] == "<#":
        # Real channel
        channel_id = channel[2:-1]
    else:
        # Name of a channel
        channel_id = [i.id for i in ctx.guild.channels if i.name == channel]

        if len(channel_id) == 1:
            channel_id = channel_id[0]
        else:
            #! Error Message
            embed = create_embed(
                "Error",
                "The channel provided is invalid.  Make sure it's spelled correctly with proper capitlization (case sensitive).  Consider trying to use the actual # for the channel (ie. #channel)",
                "red",
            )
            await ctx.channel.send(embed=embed)
            return

    db["db"].execute("UPDATE settings SET programs_channel = (?)", (channel_id,))
    db["con"].commit()

    embed = create_embed("Programs Setup Successfully", "", "light_green")
    add_field(
        embed, "channel", f"{ctx.guild.get_channel(int(channel_id)).mention}", True
    )
    await ctx.channel.send(embed=embed)


async def program_reaction_handling(ctx, client):
    db = await database_connection(ctx.guild_id)

    mod_channel_id = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )
    if mod_channel_id is None:
        return False

    mod_channel_id = int(mod_channel_id)

    if mod_channel_id != ctx.channel_id:
        return

    m = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)
    m_embeds = m.embeds[0]

    if m.embeds[0].title == "Programs Verification Required":
        if ctx.emoji.name == "❌":
            await m.delete()
            return True
        elif ctx.emoji.name == "✅":
            user_id = find_user(m_embeds.fields[0].value)
            if not user_id:
                return False

            if (
                db["db"]
                .execute(
                    "SELECT COUNT(user_id) FROM programs WHERE user_id = (?)",
                    (user_id,),
                )
                .fetchone()[0]
                != 1
            ):
                programs_list = m_embeds.fields[2].value
                await m.delete()
                if not programs_list:
                    return False
                db["db"].execute(
                    "INSERT INTO programs (user_id, description) VALUES (?, ?)",
                    (user_id, programs_list),
                )
                db["con"].commit()
            else:
                programs_additions = m_embeds.fields[2].value
                await m.delete()
                if not programs_additions:
                    return False

                current_programs = (
                    db["db"]
                    .execute(
                        "SELECT description FROM programs WHERE user_id = (?)",
                        (user_id,),
                    )
                    .fetchone()
                )[0]
                current_programs += "\n"
                for p in programs_additions.split("\n"):
                    current_programs += p + "\n"
                programs_list = current_programs

                db["db"].execute(
                    "UPDATE programs SET description = ? WHERE user_id = ?",
                    (current_programs, user_id),
                )
                db["con"].commit()

            user = client.get_user(user_id)
            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            embed = create_embed(
                "!Programs Command Created Successfully", "", "light_green"
            )
            add_field(embed, "Programs", programs_list, True)

            try:
                await dm_channel.send(embed=embed)
            except:
                return True

            return True
    elif m.embeds[0].title == "Programs Edit Verification Required":
        print("temp need to dev")
        #! dev
    return False