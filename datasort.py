import sqlite3
import csv
import City

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

with open("city_info_modified.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        command = "INSERT INTO cities VALUES('" + row[0] + "', '" + row[1] + "', '" + row[2] + "')"
        print(command)
        cursor.execute(command)
csvfile.close()

# Associating zip codes with their closest cities


connection.close()
