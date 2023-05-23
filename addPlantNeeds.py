import sqlite3
from sqlite3 import Error

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM days")
print(cursor.fetchone())
connection.close()
