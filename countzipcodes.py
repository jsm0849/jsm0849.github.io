from City import City
import sqlite3
import csv

cities_id_names = {}  # Dictionary to hold the list of Cities (their ID and name)
cities_zip_count = {}  # Dictionary to hold the list of Cities and their number of associated zip codes.
zips = []  # Array to hold all zip codes and their associated City IDs

# Retrieving the City names and their IDs to populate the new csv file:
with open("city_info.csv", 'r') as city_file:
    city_reader = csv.reader(city_file)
    for row in city_reader:
        cities_id_names.update({row[2]: row[1]})
        cities_zip_count.update({row[2]: 0})
city_file.close()

# Retrieving all zip codes from the database (with their associated Cities) and creating a tally of the number of zip
# codes associated with each City:
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM zipcodes")
zips = cursor.fetchall()
for i in range(len(zips)):
    count = cities_zip_count[zips[i][1]] + 1
    cities_zip_count.update({zips[i][1]: count})

# Writing the collected data to a new csv file for graphing:
with open("city_zip_count.csv", 'w', newline='') as count_file:
    count_writer = csv.writer(count_file)
    for key in cities_id_names:
        count_row = [cities_id_names[key], cities_zip_count[key]]
        count_writer.writerow(count_row)
