import sqlite3

import check_for_errors
import statistics
from database import db_initialisation
from flights import flight_options
from non_flights import non_flight_options, NonFlightType
from util import choices

if __name__ == '__main__':
    # Initialise connection
    conn = sqlite3.connect("table.db")
    db_initialisation.initialise_db(conn)

    # Main loop
    while True:
        c = choices("Select option:", [
            "View/Modify Flights",
            "View/Modify Pilots",
            "View/Modify Aircraft",
            "View/Modify Destinations",
            "Statistics",
            "Check for Errors",
            "Save and Quit",
            "Quit without Saving"
        ])

        if c == 1:
            flight_options(conn)
        elif c == 2:
            non_flight_options(conn, NonFlightType.PILOTS)
        elif c == 3:
            non_flight_options(conn, NonFlightType.AIRCRAFT)
        elif c == 4:
            non_flight_options(conn, NonFlightType.DESTINATIONS)
        elif c == 5:
            statistics.show_statistics(conn)
        elif c == 6:
            check_for_errors.check_for_errors(conn)
        elif c == 7:
            conn.commit()
            break
        elif c == 8:
            c2 = choices("Are you sure you want to quit without saving?", ["Yes", "No"])
            if c2 == 1:
                break

    conn.close()
