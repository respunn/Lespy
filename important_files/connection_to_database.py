import sqlite3

# Connecting to database
try:
    conn = sqlite3.connect("level_system.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, name TEXT, level INTEGER, xp INTEGER)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS admins
                (id INTEGER PRIMARY KEY, name TEXT)"""
    )
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
