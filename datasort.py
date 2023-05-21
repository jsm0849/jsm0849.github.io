import sqlite3
import csv
from City import City
import math

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

# Retrieving the Cities from the csv file
with open("city_info_modified.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        command = "INSERT INTO cities VALUES('" + row[0] + "', '" + row[1] + "', '" + row[2] + "')"
        cursor.execute(command)
csvfile.close()

# Sorting Cities in ascending order by latitude and longitude
cities = []     # Array of city data retrieved from the database.
arrCities = []  # Array of City objects retrieved from the database.
cursor.execute("SELECT * FROM cities")
cities = cursor.fetchall()

# Populating the array with City objects using data from the database:
for row in cities:
    arrCities.append(City(row[0], row[1], row[2]))

# Retrieving the zip codes from the csv file
with open("ZIPlatlong.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    zipFileRows = []    # List of rows to be added to the zipData.csv file.
    closestCity = City(0, 0, 0)      # Stores the closest city to the current zip code so far.
    closestCityDistance = [0, -1]    # Stores the distance to current zip code and id of the closest city so far.
    for row in csvReader:
        # This section finds the city closest to the current zip code.
        latDistance = 0
        longDistance = 0
        distance = 0
        closestCityDistance = [0, -1]
        # Finding the city with the smallest distance to the current zip code. Each degree of latitude is about 69 miles
        # apart, and each degree of longitude is about 53 miles apart in most of the United States.
        for i in range(len(arrCities)):
            latDistance = abs(float(arrCities[i].latitude) - float(row[1])) * 69
            longDistance = abs(float(arrCities[i].longitude) - float(row[2])) * 53
            distance = math.sqrt(latDistance ** 2 + longDistance ** 2)
            # if the previously closest city found is not as close as the current city, or if this is the first city:
            if closestCityDistance[1] == -1 or closestCityDistance[1] > distance:
                closestCityDistance = [arrCities[i].id, distance]
                closestCity = City(arrCities[i].id, arrCities[i].latitude, arrCities[i].longitude)
        # Adding the zip code to the list to be written to file now that the closest city has been found.
        zipFileRows.append([row[0], closestCity.latitude, closestCity.longitude, closestCity.id])
    # Writing the completed list of zip codes with associated cities to a file (for accuracy verification).
    with open("zipData.csv", mode='w') as zip_file:
        zip_writer = csv.writer(zip_file)
        zip_writer.writerows(zipFileRows)
    zip_file.close()
    # Reading the data back from the file and adding it to the zipcodes table in the database now that I've verified its
    # accuracy.
    with open("zipData.csv", mode='r') as zip_file:
        fileReader = csv.reader(zip_file)
        for row in fileReader:
            if(len(row) > 0):
                command = "INSERT INTO zipcodes VALUES('" + row[0] + "', '" + row[3] + "')"
                cursor.execute(command)
    zip_file.close()
csvfile.close()

# Associating zip codes with their closest cities


connection.close()
