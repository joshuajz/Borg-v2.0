import discord
import os
import traceback
from commands import *
from methods.database import create_filesystem, database_connection
from dotenv import load_dotenv

load_dotenv()

# Intents
intents = discord.Intents().default()
intents.members = True
intents.reactions = True

# TODO: Potentially change programs commands, and cange the commands in general so they're more consistant

# TODO: Setup a bot channel where all messages are deleted after being sent (after a timeout)

# TODO: Add some sort of class system to store each server's DB and potentially other info so you don't have to call the DB everytime
# TODO: Start using the new find_user function in methods.user.py

# Commmands
command_list = {
    "help": help_command,
    "create_role": create_role,
    "roles": roles,
    "role": role,
    "remove_role": remove_role,
    "create_command": create_command,
    "remove_command": remove_command,
    "commands": commands,
    "programs_setup": programs_setup,
    "programs_add": programs_add,
    "programs": programs,
    "programs_remove": programs_remove,
    "welcome_setup": welcome_setup,
    "welcome_toggle": welcome_toggle,
    "warn": warn,
    "userinfo": userinfo,
    "programs_edit": programs_edit,
}

# Bot Instance
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}.")

    await create_filesystem(client)


@client.event
async def on_message(ctx):
    print(ctx.content)

    # Don't do anything with a bot's message
    if ctx.author == client.user:
        return

    # Potential regex: (?<=^!)(\w*)

    if ctx.content.startswith("!"):
        if "\n" in ctx.content:
            command = (
                ctx.content.split("\n")[0]
                .split(" ")[0]
                .strip()
                .replace("!", "")
                .lower()
            )
        else:
            command = ctx.content[1::].split(" ")[0].lower().strip().lower()

        if command in command_list:
            await command_list[command](ctx, client)
        else:
            await check_custom_command(ctx, client, command)


@client.event
async def on_raw_reaction_add(ctx):
    if ctx.member.bot:
        return

    if await program_reaction_handling(ctx, client) == True:
        return


@client.event
async def on_member_join(ctx):
    await welcome_handling(ctx, client)


# Runs the bot with the token in .env
client.run(os.environ.get("bot_token"))