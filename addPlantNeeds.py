import sqlite3
import csv

# This script adds the plantNeeds and soilTypes tables to the database. These tables hold the various included plant
# types and the number of inches of water they need per week, and a variety of soil types and their ability to retain
# water.
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()
cursor.execute("""CREATE TABLE plantNeeds
                        (id TEXT, water REAL)""")
cursor.execute("""CREATE TABLE soilTypes
                        (id TEXT, retention REAL)""")
with open("PlantWaterNeeds.csv", 'r') as plant_file:
    plantReader = csv.reader(plant_file)
    for row in plantReader:
        command = "INSERT INTO plantNeeds VALUES('" + row[0] + "', '" + row[1] + "')"
        cursor.execute(command)
        connection.commit()
plant_file.close()
with open("SoilTypes.csv", 'r') as soil_file:
    soilReader = csv.reader(soil_file)
    for row in soilReader:
        command = "INSERT INTO soilTypes VALUES('" + row[0] + "', '" + row[1] + "')"
        cursor.execute(command)
        connection.commit()
soil_file.close()
connection.close()
