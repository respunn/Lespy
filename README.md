# Lespy
It is a level system discord bot made for Respy Project.
<br><br><br>
!leaderboard: This command displays the leaderboard of the top users in the server based on their level. The users will be ranked in descending order according to their level.
<br><br>
!progress @user or user_id [Optional]: This command displays the progress of a specific user in the server towards the next level. If a user is specified, the command will display the progress of that user. If no user is specified, the command will display the progress of the user who invoked the command.
<br><br>
!help: This command shows a list of all the available commands and their descriptions.
<br><br>
!setlevel @user or user_id: [Admin Command] This command sets the level of a specific user in the server. Only admins can use this command.
<br><br>
!addxp @user or user_id: [Admin Command] This command adds experience points to a specific user in the server. Only admins can use this command.
<br><br>
!showadmins: [Admin Command] This command shows a list of all the admins in the database. Only admins can use this command.
<br><br>
!deleteuser @user or user_id: [Super Admin Command] This command deletes a specific user's data from the server, including their level and experience points. Only super admins can use this command.
<br><br>
!deleteusers: [Super Admin Command] This command deletes all user data from the server, including their levels and experience points. Only super admins can use this command.
<br><br>
!addadmin @user or user_id: [Super Admin Command] This command adds a new admin to the database. Only super admins can use this command.
<br><br>
!removeadmin @user or user_id: [Super Admin Command] This command removes an admin from the database. Only super admins can use this command.
<br><br>
!resetall: [Super Admin Command] This command resets the level and XP of all users in the database. Only super admins can use this command.
<br><br>
It is important to note that !addxp, !setlevel, !addadmin, !removeadmin, !deleteuser, !deleteusers, and !resetall are considered admin or super admin commands, which means that only users with the appropriate permissions can execute these commands.
<br><br><br><br>

You need to create config.py file into the bot file and paste this:
```python
WORDS = ("ty", "thanks", "thank you") # Words needed to gain XP.
level_xp_multiplier = 1.2 # The number that multiplies the xp required when leveling up.
max_level = 500 # Maximum reachable level.
min_level = 1 # Minimum adjustable level.
min_level_experience = 10 # Minimum required xp to level up.
max_level_experience = 1000 # Maximum required xp to level up.

super_admin_ids = (
    "123456789123456789" # Super Admin
)
```