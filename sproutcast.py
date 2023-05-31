import sqlite3
import streamlit
import math
from City import City
from urllib.request import urlopen
from datetime import datetime, timedelta
import pandas
import numpy
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import tree
from sklearn.metrics import r2_score


def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


page_title = "SproutCast: A Gardener's Companion"
page_icon = ":seedling:"
layout = "centered"

streamlit.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

plant_types = {}    # Dictionary to hold the available plant types and their water needs.
plant = []
soil_types = {}     # Dictionary to hold the available soil types and their ability to retain water.
soil = []
plant_checkboxes = []   # Array of bools to hold the statuses of each checkbox.
all_data_recorded = False  # Keeps track of the state of data collection.
# Necessary data for the Random Forest algorithm:
selected_plants = []    # Array to hold the plants the user has growing in their garden.
selected_soil = ""      # Holds the soil type selected by the user.
inputZipcode = "0"      # Holds the zipcode of the user.
recent_rain = 0         # Holds the amount of rain the user got within the last week (inches).
city_id = ""            # Holds the ID of the City closest to the user for which there is data available.
extra_water = ""        # Number of inches of extra water the user gave their garden in the last week.
temp_this_week = 0      # Stores the average temperature of the week that ends today.
median_temperatures = []  # Stores a pattern of temperatures for display purposes.
local_dates = []  # Stores the dates close to today for display purposes.
recent_rains = []  # Stores the recent rains for the user's area.
rain_dates = []  # Stores relevant dates for recent rains.

# Connecting to the database
connection = sqlite3.connect("DB.db")
cursor = connection.cursor()
# Retrieving the available plant types from the database.
cursor.execute("SELECT * FROM plantNeeds")
plants = cursor.fetchall()
for row in plants:
    plant_types.update({row[0]: row[1]})
    plant.append(row[0])
cursor.close()
cursor = connection.cursor()
# Retrieving the available soil types from the database.
cursor.execute("SELECT * FROM soilTypes")
soils = cursor.fetchall()
for row in soils:
    soil_types.update({row[0]: row[1]})
    soil.append(row[0])
cursor.close()
cursor = connection.cursor()

# Form to take user inputs
textValid = False   # Bool indicating whether the text field inputs were valid.
allInputsValid = False  # Bool indicating whether all input fields are valid.
streamlit.header(f"Tell us about your garden! Please enter your information below.")
with streamlit.form("input_form"):
    col1, col2, col3 = streamlit.columns(3)
    col1.text_input("Enter your five digit zipcode:", key="inputZipcode")
    col2.selectbox("Select Soil Type:", soil, key="selectedSoil")
    col3.text_input("Enter amount of water given this week (inches):", key="extraWater", placeholder="0")
    with streamlit.expander("Select which plants you are growing in your garden"):
        for i in range(len(plant)):
            plant_checkboxes.append(streamlit.checkbox(label=f"{plant[i]}", key=plant[i]))
    "---"
    submitted = streamlit.form_submit_button("Submit Form")

    # Input data validation:
    if submitted:
        inputZipcode = str(streamlit.session_state["inputZipcode"])
        extra_water = str(streamlit.session_state["extraWater"])
        if not inputZipcode.isdigit():
            streamlit.error("Please enter a valid zip code.")
        else:
            inputZipcode = int(inputZipcode)
            command = "SELECT * FROM zipcodes WHERE id = '" + str(inputZipcode) + "'"
            cursor.execute(command)
            zip = cursor.fetchone()
            if zip == None:
                streamlit.error("Please enter a valid zip code.")
            else:
                if not is_number(extra_water) and extra_water != '':
                    streamlit.error("Please enter a valid number of inches of water recently given.")
                else:
                    textValid = True
        for i in range(len(plant)):
            if plant_checkboxes[i]:
                selected_plants.append(plant[i])
        if len(selected_plants) == 0:
            streamlit.error("Please select at least one plant being grown in your garden.")
        elif textValid:
            allInputsValid = True

    # Web scraper and other code to retrieve the necessary data:
    if allInputsValid:
        median_temperatures = []
        local_dates = []
        recent_rains = []
        rain_dates = []
        selected_soil = str(streamlit.session_state["selectedSoil"])
        today = datetime.today()
        currentDay = today - timedelta(days=1)  # Holds the current date needed to loop through the past week.
        recent_rain = 0  # Holds the total rainfall in inches at the user's location in the past week.

        # This segment loops through all days in the past week, scraping data from the National Weather Service website
        # about precipitation.
        closest = []  # Holds the latitude and longitude and distance of the closest weather center to the zip code.
        command = "SELECT * FROM zipcodes WHERE id = '" + str(inputZipcode) + "'"
        cursor.execute(command)
        zipcode = cursor.fetchone()
        command = "SELECT * FROM cities WHERE id = '" + zipcode[1] + "'"
        cursor.execute(command)
        cityTuple = cursor.fetchone()
        city = City(cityTuple[0], cityTuple[1], cityTuple[2])
        city_id = cityTuple[0]
        latitude = city.latitude
        longitude = city.longitude
        for i in range(6):
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
            if i == 0:
                # Finding the coordinates of the closest weather station to the user's zip code:
                for k in range(len(entries) - 1):
                    latDistance = abs(float(latitude) - float(entries[k][0])) * 69
                    longDistance = abs(float(longitude) - float(entries[k][1])) * 53
                    distance = math.sqrt(latDistance ** 2 + longDistance ** 2)
                    if len(closest) == 0:
                        closest = [entries[k][0], entries[k][1], distance]
                    elif closest[2] > distance:
                        closest = [entries[k][0], entries[k][1], distance]
            for k in range(len(entries) - 1):
                if entries[k][0] == closest[0] and entries[k][1] == closest[1]:
                    recent_rain = recent_rain + float(entries[k][2])
                    recent_rains.append(float(entries[k][2]))
                    break
            # Retrieving median temperature for currentDay in the current City:
            date_key = currentDay.strftime("%d/%m")
            day_id = date_key + "_" + city.id
            command = "SELECT * FROM days WHERE id = '" + day_id + "'"
            cursor.execute(command)
            day = cursor.fetchone()
            temp_this_week = temp_this_week + float(day[1])
            median_temperatures.append(float(day[1]))
            local_dates.append(currentDay.strftime("%m/%d"))
            rain_dates.append(currentDay.strftime("%m/%d"))
            currentDay = currentDay - timedelta(days=1)
        temp_this_week = temp_this_week / 6
        all_data_recorded = True

with streamlit.container():
    if all_data_recorded:
        today = datetime.today()
        currentDay = today  # Holds the current date needed to loop through the next few days.
        user_data = []  # Array to hold the user's data for the Random Forest regression.
        avg_water_need = 0  # Holds the average water needed by all selected plants.
        avg_rain_next = 0
        avg_temp_next = 0
        temp_array_temps = []
        temp_array_dates = []
        temp_rains = []
        temp_rain_dates = []
        # Reversing the order of median_temperatures and local_dates:
        for i in range(len(median_temperatures)):
            temp_array_temps.append(median_temperatures[len(median_temperatures) - (i + 1)])
            temp_array_dates.append(local_dates[len(local_dates) - (i + 1)])
        median_temperatures = temp_array_temps
        local_dates = temp_array_dates
        # Retrieving median temperature and rainfall for today and the next three days in the closest City to the user:
        for a in range(4):
            date_key = currentDay.strftime("%d/%m")
            day_id = date_key + "_" + city.id
            command = "SELECT * FROM days WHERE id = '" + day_id + "'"
            cursor.execute(command)
            day = cursor.fetchone()
            avg_temp_next = avg_temp_next + float(day[1])
            median_temperatures.append(float(day[1]))
            local_dates.append(currentDay.strftime("%m/%d"))
            avg_rain_next = avg_rain_next + float(day[2])
            currentDay = currentDay + timedelta(days=1)
        avg_temp_next = avg_temp_next / 4
        avg_rain_next = avg_rain_next / 4
        # Determining average water need for selected plants:
        for i in range(len(selected_plants)):
            avg_water_need = avg_water_need + float(plant_types[selected_plants[i]])
        avg_water_need = avg_water_need / len(selected_plants)
        # Determining soil water retention factor:
        soil_retention = float(soil_types[selected_soil])
        # Populating the user_data array:
        user_data.append([soil_retention,
                         recent_rain,
                         avg_rain_next,
                         temp_this_week,
                         avg_temp_next,
                         avg_water_need,
                         extra_water])
        # Training the Random Forest Regressor model using the training data set.
        data_frame = pandas.read_csv("random_forest_data.csv")
        y_train = numpy.array(data_frame["Water Today"])
        X_train = data_frame.drop(["Water Today"], axis=1)
        regressor = RandomForestRegressor()
        regressor.fit(X_train, y_train.reshape(-1, 1))
        user_predict = regressor.predict(user_data)
        output_string = str(round(float(user_predict), 2))
        streamlit.write("Based on all input data, recent rainfall in your area, typical temperatures for this time" +
                        " of year, water needs of your plants, and other data, you need to give your garden " +
                        output_string + " inches of water distributed over the next two or three days" +
                        " to keep your plants healthy.")
        display_rains = []
        display_rain_dates = []
        currentDay = today - timedelta(days=1)
        for i in range(6):
            date_text = currentDay.strftime("%m/%d")
            for j in range(len(recent_rains)):
                if rain_dates[j] == date_text:
                    display_rains.append(recent_rains[j])
                else:
                    display_rains.append(0)
            display_rain_dates.append(date_text)
            currentDay = currentDay - timedelta(days=1)
        # Reversing the order of display_rains and display_rain_dates:
        for i in range(len(display_rains)):
            temp_rains.append(display_rains[len(display_rains) - (i + 1)])
            temp_rain_dates.append(display_rain_dates[len(display_rain_dates) - (i + 1)])
        display_rains = temp_rains
        display_rain_dates = temp_rain_dates
        temp_chart_data = pandas.DataFrame(median_temperatures, local_dates, columns=["Temps in your Area (F)"])
        streamlit.line_chart(temp_chart_data)
        rain_chart_data = pandas.DataFrame(display_rains, display_rain_dates, columns=["Rainfall in your Area (in)"])
        streamlit.line_chart(rain_chart_data)

connection.close()
