import sqlite3
import streamlit
import math
import re
from urllib.request import urlopen
from datetime import datetime, timedelta


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
selected_plants = []  # Array to hold the plants the user has growing in their garden.
plant_checkboxes = []  # Array of bools to hold the statuses of each checkbox.
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
    col3.text_input("Enter the amount of extra water given in the last week in inches:", key="extraWater", placeholder="0")
    with streamlit.expander("Select which plants you are growing in your garden"):
        for i in range(len(plant)):
            plant_checkboxes.append(streamlit.checkbox(label=f"{plant[i]}", key=plant[i]))
    "---"
    submitted = streamlit.form_submit_button("Submit Form")

    # Input data validation:
    if submitted:
        inputZipcode = str(streamlit.session_state["inputZipcode"])
        extraWater = str(streamlit.session_state["extraWater"])
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
                if not is_number(extraWater) and extraWater != '':
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
        today = datetime.today()
        currentDay = today - timedelta(days=1)  # Holds the current date needed to loop through the past week.
        recent_rain = 0  # Holds the total rainfall in inches at the user's location in the past week.

        # This segment loops through all days in the past week, scraping data from the National Weather Service website
        # about precipitation.
        closest = []  # Holds the latitude and longitude and distance of the closest weather center to the zip code.
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
            latitude = "38.40352427808116"
            longitude = "-85.3711418113746"
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
                    break
            currentDay = currentDay - timedelta(days=1)
        streamlit.write(closest, recent_rain)
connection.close()
