# Lespy
It is a level system discord bot made for Respy Project.

## Config file
You need to create config.py file into the bot file and paste this:
```python
WORDS = ("ty", "thanks", "thank you") # Words needed to gain XP.
level_xp_multiplier = 1.2 # The number that multiplies the xp required when leveling up.
max_level = 500 # Maximum reachable level.
min_level = 1 # Minimum adjustable level.
min_level_experience = 10 # Minimum required xp to level up.
max_level_experience = 1000 # Maximum required xp to level up.

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
