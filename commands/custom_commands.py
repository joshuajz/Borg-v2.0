import discord
import shlex
from methods.embed import create_embed, add_field
from methods.database import database_connection

# TODO: Fix the happyboi fix, by using None instead of NULL


async def create_command(ctx, client):
    # Todo: !create_command !commandname 'text here'

    if ctx.author.guild_permissions.administrator != True:
        return

    db = await database_connection(ctx.guild.id)

    content = shlex.split(ctx.content, posix=False)
    # x = 3, 4
    if len(content) != 3 and len(content) != 4:
        embed = create_embed(
            "Create_command",
            "!create_command {'!command name'} {'description'} {'image (optional)'}",
            "orange",
        )
        add_field(
            embed,
            "command name",
            "The 'name' of the command (ie. !info or !welcome).",
            True,
        )
        add_field(
            embed,
            "description",
            'The actual text provided by the command (ie. "Information can be found here: https://wikipedia.com")',
            True,
        )
        add_field(
            embed,
            "image (optional)",
            "An optional image to display with the command.",
            True,
        )
        example_list = """```
- item 1
- item 2
- item 3
- etc...```"""
        add_field(
            embed,
            "Hint",
            f'If you want to add multiple lines OR use a space (for example, as Code or as a list.  You\'ll need to use qutoation marks ("").  Example: !create_command !list "Here is a list: {example_list}',
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    command = content[1]

    # Automatically adds '!' to the command name if it does not start with '!'
    # a command name not starting with '!' will cause unexpected behaviour when calling and deleting
    if command[0] != '!':
        command = '!' + command

    if command[0] == '"' and command[-1] == '"':
        command = command[1:-1]

    description = content[2]
    if len(content) == 3:
        image = None
    else:
        if content[3][0] == '"' and content[3][-1] == '"':
            image = content[3][1:-1]
        else:
            image = content[3]

    #! settings_location
    # with open(await settings_location(ctx.guild.id)) as f:
    #     l = yaml.safe_load(f)
    #     command_list = []
    #     for group in l["default_commands"]:
    #         for c in l["default_commands"][group]:
    #             if type(c) == str:
    #                 command_list.append(c)

    command_list = [
        i[0][1::]
        for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    if command[1::] in command_list:
        embed = create_embed(
            "Error",
            "That command is already a registerd command for this server.",
            "red",
        )
        await ctx.channel.send(embed=embed)
        return

    if description[0] == '"' and description[-1] == '"':
        description = description[1:-1]

    db["db"].execute(
        "INSERT INTO custom_commands VALUES (?, ?, ?)",
        (command, description, image),
    )
    db["con"].commit()

    embed = create_embed("Command Created Successfully.", "", "light_green")
    add_field(embed, "Command", command, True)
    add_field(embed, "Description", description, True)
    add_field(embed, "Image", image, True)

    await ctx.channel.send(embed=embed)


async def remove_command(ctx, client):
    if ctx.author.guild_permissions.administrator != True:
        return

    content = shlex.split(ctx.content)

    db = await database_connection(ctx.guild.id)

    if len(content) != 2:
        embed = create_embed("Remove_command", "!remove_command {command}", "orange")
        add_field(
            embed,
            "command",
            "The command you would like to remove (ie. !info or !hello)",
            True,
        )

        await ctx.channel.send(embed=embed)
        return

    command = content[1]

    if command[0] != "!":
        command = "!" + command

    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    for c in command_list:
        if c[0] == command:
            db["db"].execute(
                "DELETE FROM custom_commands WHERE command = (?)", (command,)
            )
            db["con"].commit()

            embed = create_embed("Command Removed Successfully.", "", "dark_blue")
            add_field(embed, "command", c[0], True)
            add_field(embed, "description", c[1], True)
            add_field(embed, "image", c[2], True)

            await ctx.channel.send(embed=embed)
            return

    embed = create_embed(
        "Error",
        "Invalid Command to Remove.  Try checking all of the commands with !commands",
        "red",
    )

    await ctx.channel.send(embed=embed)


async def check_custom_command(ctx, client, command):
    db = await database_connection(ctx.guild.id)

    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    for c in command_list:
        if f"!{command.lower()}" == c[0]:

            embed = create_embed(f"{command.capitalize()}", f"{c[1]}", "orange")
            if c[2] != None:
                embed.set_image(url=c[2])
            await ctx.channel.send(embed=embed)


async def commands(ctx, client):
    # TODO
    db = await database_connection(ctx.guild.id)

    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]
    if len(command_list) >= 1:
        final = """```"""

        for command in command_list:
            final += command + "\n"

        final += "```"

        embed = create_embed("Commands", final, "orange")
        await ctx.channel.send(embed=embed)
    else:
        embed = create_embed(
            "Error",
            "There are currently no commands!  Ask an admin to use !create_command",
            "red",
        )
        await ctx.channel.send(embed=embed)