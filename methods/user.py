import discord


def find_user(data):
    data = data.strip()
    if data.isnumeric():
        # User ID is given
        user_id = int(data)
    elif data[0:3] == "<@!":
        user_id = int(data[3:-1])
    elif data[0:2] == "<@":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id
