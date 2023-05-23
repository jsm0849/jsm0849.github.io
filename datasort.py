import csv
import math
import sqlite3
from datetime import datetime
from datetime import timedelta

from City import City
from Day import Day


def parse_date(datetext):
    for format in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return datetime.strptime(datetext, format)
        except ValueError:
            pass
    raise ValueError('format was not valid!')


# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

# Retrieving the Cities from the csv file
with open("city_info_modified.csv", 'r') as city_file:
    cityReader = csv.reader(city_file)
    for row in cityReader:
        command = "INSERT INTO cities VALUES('" + row[0] + "', '" + row[1] + "', '" + row[2] + "')"
        cursor.execute(command)
city_file.close()

# Sorting Cities in ascending order by latitude and longitude
cities = []  # Array of city data retrieved from the database.
arrCities = []  # Array of City objects retrieved from the database.
cursor.execute("SELECT * FROM cities")
cities = cursor.fetchall()

# Populating the array with City objects using data from the database:
for row in cities:
    arrCities.append(City(row[0], row[1], row[2]))

# Retrieving the zip codes from the csv file
with open("ZIPlatlong.csv", 'r') as zip_origin_file:
    zipReader = csv.reader(zip_origin_file)
    zipFileRows = []  # List of rows to be added to the zipData.csv file.
    closestCity = City(0, 0, 0)  # Stores the closest city to the current zip code so far.
    closestCityDistance = [0, -1]  # Stores the distance to current zip code and id of the closest city so far.
    for row in zipReader:
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
            if (len(row) > 0):
                command = "INSERT INTO zipcodes VALUES('" + row[0] + "', '" + row[3] + "')"
                cursor.execute(command)
    zip_file.close()
zip_origin_file.close()

# Processing weather data. This section looks at historic weather data for all 210 cities and collects data for each day
# of the year for each city, including the median average temperature and median precipitation for each day.
daysOfYear = {}  # Dictionary to hold all the days of the year (including leap day).
for i in range(len(arrCities)):
    cityID = arrCities[i].id
    startDateText = '1/1/2024'
    startDate = datetime.strptime(startDateText, '%d/%m/%Y')
    # Populating daysOfYear with all possible days of the year including leap day. "dayText" is a str key
    # (01/25 for example)which allows later code to update Day objects without searching through every day of the year
    # to find the matching one.
    for j in range(366):
        dayText = datetime.strftime(startDate, '%d/%m')
        daysOfYear.update({dayText: [Day(startDate.day, startDate.month, dayText)]})
        startDate = startDate + timedelta(days=1)
    filename = "Historic Weather Data/" + cityID + ".csv"
    with open(filename, 'r') as weather_file:
        fileReader = csv.reader(weather_file)
        for row in fileReader:
            if row[1] == 'Date' or row[1] == 'date':
                continue
            date = parse_date(row[1])
            dateKey = datetime.strftime(date, '%d/%m')
            currentDay = daysOfYear[dateKey]
            print(currentDay[0].id)
            if row[2] != 'NA' and row[2] != '':
                if row[3] != 'NA' and row[3] != '':
                    avgTemp = (float(row[2]) + float(row[3])) / 2
                    currentDay[0].addTemp(avgTemp)
            if row[4] != 'NA' and row[4] != '':
                currentDay[0].addRain(float(row[4]))
        for key, day in daysOfYear.items():
            print(key, arrCities[i].id)
            medianTemp = str(day[0].getMedianTemp())
            medianRain = str(day[0].getMedianRain())
            id = key + '_' + arrCities[i].id
            command = "INSERT INTO days VALUES('" + id + "', '" + medianTemp + "', '" + medianRain + "')"
    weather_file.close()
connection.close()
