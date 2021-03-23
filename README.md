# BorgV2

#### Setting up a testing environment:

1. git pull https://github.com/joshuajz/BorgV2
2. Within that folder create a .env file.
3. Create a testing bot with the discord developer portal (https://discord.com/developers/applications)
4. Copy the bot's token.
5. Place the bot's token in the .env file -> bot_token = TOKENHERE
6. Run main.py to get the bot up and running



## About The Project

An advanced discord bot made for university applicant servers that allows users to display their programs.  Also allows administrators to add useful commands and welcome messages.  It's a rewrite of my old bot (Borg).

### Built With
- [Python](https://www.python.org/)
- [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html)
- [Sqlite](https://www.sqlite.org/index.html)

### Installation
1. Install [Python](https://www.python.org/downloads/)
2. Clone the repository:
```sh
git clone https://github.com/joshuajz/BorgV2
```
3. Open the cloned repository
4. Install the prerequisites using pip: (ie. run the following in the cloned folder)
```sh
pip install -r requirements.txt
```
5. Create a test discord server (ie. press the + in discord)
![image](https://user-images.githubusercontent.com/35657686/112092497-fc912980-8b6d-11eb-994a-be0667b62bc5.png)
6. Create a [discord application](https://discord.com/developers/applications).
7. Create a bot for the discord application by clicking on the "Bot" tab.
8. Scroll slightly down on the "Bot" tab and select the **Presenece Intent** and **Server Members Intent**.
![image](https://user-images.githubusercontent.com/35657686/112092380-be940580-8b6d-11eb-9dd7-6f91aa9fdc20.png)
9. Click on OAuth2.
10. Select _bot_ under the Scopes.
11. Select _Administrator_ under the permissions.  Since this is for a test server, we won't worry about selecting only the proper ones.
12. Invite the discord bot to the test server that you've created previously by using the invite link created.
