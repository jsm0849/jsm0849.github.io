import sqlite3
import csv
from City import City

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

# Retrieving the Cities from the csv file
with open("city_info_modified.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    for row in csvReader:
        command = "INSERT INTO cities VALUES('" + row[0] + "', '" + row[1] + "', '" + row[2] + "')"
        print(command)
        cursor.execute(command)
csvfile.close()

# Sorting Cities in ascending order by latitude and longitude
cities = []     # Array of Cities retrieved from the database.
arrLat = []     # Array of Cities sorted in ascending order by latitude.
arrLong = []    # Array of Cities sorted in ascending order by longitude.
closeCityLat = []   # Array of Cities that are close to the current zip code by latitude.
closeCityLong = []  # Array of Cities that are close to the current zip code by longitude.
cursor.execute("SELECT * FROM cities")
cities = cursor.fetchall()

# Populating the arrays to be sorted by latitude and longitude
for row in cities:
    print(row[0], row[1], row[2])
    arrLat.append(City(row[0], row[1], row[2]))
    arrLong.append(City(row[0], row[1], row[2]))
# Sorting one array of Cities in ascending order by latitude
for i in range(len(arrLat)):
    for j in range(len(arrLat) - 1):
        city = arrLat[j]
        nextCity = arrLat[j + 1]
        if city.latitude > nextCity.latitude:
            tempCity = arrLat[j]
            arrLat[j] = arrLat[j + 1]
            arrLat[j + 1] = tempCity

# Sorting the second array of Cities in ascending order by longitude
for i in range(len(arrLong)):
    for j in range(len(arrLong) - 1):
        city = arrLong[j]
        nextCity = arrLong[j + 1]
        if city.longitude > nextCity.longitude:
            tempCity = arrLong[j]
            arrLong[j] = arrLong[j + 1]
            arrLong[j + 1] = tempCity

# Retrieving the zip codes from the csv file
with open("ZIPlatlong.csv", 'r') as csvfile:
    csvReader = csv.reader(csvfile)
    latStack = []       # Stack of Cities sorted by latitude, closest to zip code are on top
    longStack = []      # Stack of Cities sorted by longitude, closest to zip code are on top
    for row in csvReader:
        # This section ensures the top five elements in both latStack and longStack are the five closest latitudes and
        # longitudes to the coordinates of the current zip code.
        for i in range(len(arrLat)):
            latStack.append(arrLat[i])
            if arrLat[i].latitude <= float(row[1]):
                if i < len(arrLat) - 1:
                    latStack.append(arrLat[i + 1])
                if i < len(arrLat) - 2:
                    latStack.append(arrLat[i + 2])
                break
        for i in range(len(arrLong)):
            longStack.append(arrLong[i])
            if arrLong[i].longitude <= float(row[2]):
                if i < len(arrLong) - 1:
                    longStack.append(arrLat[i + 1])
                if i < len(arrLong) - 2:
                    longStack.append(arrLong[i + 2])
                break
        # This section finds a match between latStack and longStack, the coordinates of the closest City to the current
        # zip code.
        for i in range(5):
            closeCityLat.append(latStack.pop())
            closeCityLong.append(longStack.pop())
        for i in range(len(closeCityLat)):
            for j in range(len(closeCityLong)):
                if closeCityLat[i].id == closeCityLong[j].id:
                    command = ("INSERT INTO zipcodes VALUES('" + row[0] + "', '" + closeCityLat[i].latitude + "', '" +
                                closeCityLat[i].longitude + "', '" + closeCityLat[i].id + "')")
                    print(command)
                    cursor.execute(command)
csvfile.close()

# Associating zip codes with their closest cities


connection.close()
