# Lespy
It is a level system discord bot made for Respy Project.

Lespy that has a leveling system, Lespy listens to messages sent by users, and if the message contains certain words defined in the code, it checks whether the message is a reply or mentions the message author. If not, it finds the user who is tagged or replied to in the message and adds 1 XP to their current XP in the database. If the user reaches the required XP to level up, the bot sends an embed message announcing the user's level-up. The bot also has lots of commands that users can use. The bot uses SQLite3 database to store users' XP and level information, and it also has a separate table for admin users.

## Config file
You need to create config.py file into the important_files and paste this:
```python
WORDS = ("ty", "thanks", "thank you") # Words needed to gain XP.
level_xp_multiplier = 1.2 # The number that multiplies the xp required when leveling up.
max_level = 500 # Maximum reachable level.
min_level = 1 # Minimum adjustable level.
min_level_experience = 10 # Minimum required xp to level up.
max_level_experience = 1000 # Maximum required xp to level up.
cooldown_duration = 60 # 60 seconds cooldown for on_message event.

super_admin_ids = (
    "123456789123456789" # Discord id of the person you want to make super admin.
)
```

## Required packages
You need to install requirements.txt with this code.
```bash
  $ pip install -r requirements.txt
```

## .env File
To run this project you will need to add the following environment variables to your .env file.

`TOKEN = 'your_discord_bot_token'`

## Commands
Run `!help` command to see every command that bot has.
