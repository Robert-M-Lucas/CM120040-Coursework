import sqlite3

import db_initialisation
from flights import flight_options
from others import others_options, OthersType
from util import choices

conn = sqlite3.connect("table.db")
db_initialisation.initialise_db(conn)

while True:
    c = choices("Select data:", [
        "Flights",
        "Pilots",
        "Aircraft",
        "Destinations",
        "Save and Quit",
        "Quit without Saving"
    ])

    if c == 1:
        flight_options(conn)
    elif c == 2:
        others_options(conn, OthersType.PILOTS)
    elif c == 3:
        others_options(conn, OthersType.AIRCRAFT)
    elif c == 4:
        others_options(conn, OthersType.DESTINATIONS)
    elif c == 5:
        conn.commit()
        break
    elif c == 6:
        c2 = choices("Are you sure you want to quit without saving?", ["Yes", "No"])
        if c2 == 1:
            break

conn.close()
