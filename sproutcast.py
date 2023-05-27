import sqlite3
import streamlit


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
streamlit.header(f"Tell us about your garden! Please enter your information below.")
with streamlit.form("input_form"):
    col1, col2, col3 = streamlit.columns(3)
    col1.text_input("Enter your five digit zipcode:", key="inputZipcode")
    col2.selectbox("Select Soil Type:", soil, key="selectedSoil")
    col3.text_input("Enter the amount of extra water given in the last week in inches:", key="extraWater", placeholder="0")
    with streamlit.expander("Select which plants you are growing in your garden"):
        for i in range(len(plant)):
            streamlit.checkbox(label=f"{plant[i]}", key=plant[i])
    "---"
    submitted = streamlit.form_submit_button("Submit Form")
    if submitted:
        inputZipcode = str(streamlit.session_state["inputZipcode"])
        extraWater = str(streamlit.session_state["extraWater"])
        if not inputZipcode.isdigit():
            streamlit.error("Please enter a valid zip code.")
        else:
            inputZipcode = int(inputZipcode)
            command = "SELECT * FROM zipcodes WHERE id = '" + str(inputZipcode) + "'"
            if cursor.execute(command) == None:
                streamlit.error("Please enter a valid zip code.")
            else:
                if not is_number(extraWater) and extraWater != '':
                    streamlit.error("Please enter a valid number of inches of water recently given.")
                else:
                    textValid = True
        for i in range(len(plant)):
            if streamlit.session_state(plant[i]):
                selected_plants.append(plant[i])
        if len(selected_plants) == 0:
            streamlit.error("Please select at least one plant being grown in your garden.")
        elif textValid:
            streamlit.write("All inputs valid!")
connection.close()
