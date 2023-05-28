import pandas
import numpy
from sklearn.model_selection import train_test_split
import sqlite3
import csv
import random
from datetime import datetime, timedelta
from City import City
from urllib.request import urlopen
import math

# This script creates a dataset (csv file) that the scikit learn random forest regressor can use to make predictions
# about watering needs. The file will have the following columns:
# (SOIL WATER RETENTION FACTOR) (RAIN THIS WEEK) (AVG RAIN NEXT THREE DAYS) (AVG TEMP THIS WEEK) (AVG TEMP NEXT THREE DAYS)
#                       (AVG WATER NEEDS OF SELECTED PLANTS) (WATER GIVEN THIS WEEK) (WATER GIVEN TODAY)

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()

with open("random_forest_data.csv", 'w', newline='') as forest_file:
    forest_writer = csv.writer(forest_file)
    forest_list = []
    for i in range(1000):
        recent_rain = 0.0
        avg_temp_past = 0.0
        avg_temp_next = 0.0
        avg_rain_next = 0.0
        avg_water_need = 0.0
        water_this_week = 0.0
        water_today = 0.0
        soil_retention = 0.0
        zipcode = None
        while zipcode == None:
            zip = random.randint(2000, 80000)
            command = "SELECT * FROM zipcodes WHERE id = '" + str(zip) + "'"
            cursor.execute(command)
            zipcode = cursor.fetchone()
        today = datetime.today()
        date_offset = random.randint(5, 369)
        currentDay = today - timedelta(days=date_offset)  # Holds the current date needed to loop through the past week.
        recent_rain = 0  # Holds the total rainfall in inches at the user's location in the past week.

        # This segment loops through all days in the past week, scraping data from the National Weather Service website
        # about precipitation.
        closest = []  # Holds the latitude and longitude and distance of the closest weather center to the zip code.
        command = "SELECT * FROM zipcodes WHERE id = '" + str(zip) + "'"
        cursor.execute(command)
        zipcode = cursor.fetchone()
        command = "SELECT * FROM cities WHERE id = '" + zipcode[1] + "'"
        cursor.execute(command)
        cityTuple = cursor.fetchone()
        city = City(cityTuple[0], cityTuple[1], cityTuple[2])
        city_id = cityTuple[0]
        latitude = city.latitude
        longitude = city.longitude
        for a in range(6):
            data = []  # Array to hold a list of all data points on the page.
            entries = []  # Array of Lists to hold entries for each set of coordinates in the country.
            dateText = currentDay.strftime("%Y%m%d")
            # Requesting the precipitation data for currentDay:
            URL = "https://www.wpc.ncep.noaa.gov/qpf/obsmaps/p24i_" + dateText + "_sortbyarea.txt"
            page = urlopen(URL)
            html = page.read().decode("utf-8")
            # Parsing the webpage text into relevant data:
            text = str(html).split("Precipitation")
            data = text[2].split("\n")
            for j in range(len(data)):
                if j > 1:  # Ignoring the first two rows, which are whitespace.
                    entries.append(data[j].split())
            if a == 0:
                # Finding the coordinates of the closest weather station to the user's zip code:
                for k in range(len(entries) - 1):
                    latDistance = abs(float(latitude) - float(entries[k][0])) * 69
                    longDistance = abs(float(longitude) - float(entries[k][1])) * 53
                    distance = math.sqrt(latDistance ** 2 + longDistance ** 2)
                    if len(closest) == 0:
                        closest = [entries[k][0], entries[k][1], distance]
                    elif closest[2] > distance:
                        closest = [entries[k][0], entries[k][1], distance]
            # Adding the rain for currentDay in the current City to recent_rain:
            for k in range(len(entries) - 1):
                if entries[k][0] == closest[0] and entries[k][1] == closest[1]:
                    recent_rain = recent_rain + float(entries[k][2])
                    break
            # Retrieving median temperature for currentDay in the current City:
            date_key = currentDay.strftime("%d/%m")
            day_id = date_key + "_" + city.id
            command = "SELECT * FROM days WHERE id = '" + day_id + "'"
            cursor.execute(command)
            day = cursor.fetchone()
            avg_temp_past = avg_temp_past + float(day[1])
            currentDay = currentDay - timedelta(days=1)
        avg_temp_past = avg_temp_past / 6
        currentDay = today - timedelta(days=date_offset)
        # Retrieving median temperature and rainfall for today and the next three days in the current City:
        for a in range(4):
            date_key = currentDay.strftime("%d/%m")
            day_id = date_key + "_" + city.id
            command = "SELECT * FROM days WHERE id = '" + day_id + "'"
            cursor.execute(command)
            day = cursor.fetchone()
            avg_temp_next = avg_temp_next + float(day[1])
            avg_rain_next = avg_rain_next + float(day[2])
        avg_temp_next = avg_temp_next / 4
        avg_rain_next = avg_rain_next / 4
        avg_water_need = random.random() * 6
        command = "SELECT * from soilTypes"
        cursor.execute(command)
        soils = cursor.fetchall()
        soilValue = random.randint(0, 4)
        soil_retention = float(soils[soilValue][1])
        water_this_week = random.random() * 6
        # Determining water to give today:
        retained_water = (water_this_week + recent_rain) * soil_retention
        if avg_temp_past > 90:
            retained_water = 0
        elif avg_temp_past > 80:
            retained_water = retained_water * 0.5
        elif avg_temp_past > 70:
            retained_water = retained_water * 0.75
        upcoming_water_need = (avg_water_need - avg_rain_next) + ((avg_water_need - avg_rain_next) * soil_retention)
        if avg_temp_next > 90:
            upcoming_water_need = upcoming_water_need * 1.3
        elif avg_temp_next > 80:
            upcoming_water_need = upcoming_water_need * 1.2
        elif avg_temp_next > 70:
            upcoming_water_need = upcoming_water_need * 1.1
        water_today = upcoming_water_need - retained_water
        forest_list.append([soil_retention, recent_rain, avg_rain_next, avg_temp_past, avg_temp_next, avg_water_need,
                            water_this_week, water_today])
    forest_writer.writerows(forest_list)
