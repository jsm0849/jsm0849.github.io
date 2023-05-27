import re
import math
from datetime import datetime, timedelta
from urllib.request import urlopen


today = datetime.today()
currentDay = today - timedelta(days=1)  # Holds the current date needed to loop through the past week.
recent_rain = 0  # Holds the total rainfall in inches at the user's location in the past week.

# This segment loops through all days in the past week, scraping data from the National Weather Service website about
# precipitation.
closest = []  # Holds the latitude and longitude and distance of the closest weather center to the user's zip code.
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
        if j > 1:       # Ignoring the first two rows, which are whitespace.
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
    print(closest, recent_rain)
