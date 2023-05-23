import sqlite3
from sqlite3 import Error


def create_database(file):
    connection = None
    try:
        connection = sqlite3.connect(file)
    except Error as e:
        print(e)
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE zipcodes
                        (id INTEGER, cityID TEXT)""")
    cursor.execute("""CREATE TABLE cities
                        (id TEXT, latitude REAL, longitude REAL)""")
    cursor.execute("""CREATE TABLE days 
                        (id TEXT, medianTemp REAL, medianRain REAL)""")
    if connection:
        connection.close()


if __name__ == '__main__':
    create_database(r"C:\Users\Jacob\Desktop\Capstone\jsm0849.github.io\DB.db")

