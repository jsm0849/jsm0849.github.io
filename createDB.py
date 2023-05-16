import sqlite3
from sqlite3 import Error


def create_database(file):
    conn = None
    try:
        conn = sqlite3.connect(file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_database(r"C:\Users\Jacob\Desktop\Capstone\jsm0849.github.io\DB.db")

