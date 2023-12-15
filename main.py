import sqlite3

import check_for_errors
import statistics
from database import db_initialisation
from flights import flight_options
from non_flights import non_flight_options, NonFlightType
from util import choices

if __name__ == '__main__':
    # Initialise connection and create tables
    conn = db_initialisation.initialise_db()

    # Main loop
    while True:
        c = choices("Select option:", [
            "View/Modify Flights",
            "View/Modify Pilots",
            "View/Modify Aircraft",
            "View/Modify Destinations",
            "Lookup Destination By Code",
            "Statistics",
            "Check for Errors",
            "Save and Quit",
            "Quit without Saving"
        ])

        if c == 1:  # Flights
            flight_options(conn)
        elif c == 2:  # Pilots
            non_flight_options(conn, NonFlightType.PILOTS)
        elif c == 3:  # Aircraft
            non_flight_options(conn, NonFlightType.AIRCRAFT)
        elif c == 4:  # Destinations
            non_flight_options(conn, NonFlightType.DESTINATIONS)
        elif c == 5:  # Lookup destination
            print("Enter destination code:")
            code = input("> ")

            destinations = conn.execute("SELECT id, name FROM destinations WHERE code = ?", (code,)).fetchall()
            if len(destinations) == 0:
                print("No destination matches that code")
                print()
                continue

            print("Destinations matching that code:")
            for destination in destinations:
                print(f"\t{destination[1]} [ID: {destination[0]}]")
            print()
        elif c == 6:  # Stats
            statistics.show_statistics(conn)
        elif c == 7:  # Errors
            check_for_errors.check_for_errors(conn)
        elif c == 8:  # Save and quit
            conn.commit()
            break
        elif c == 9:  # Quit without saving
            c2 = choices("Are you sure you want to quit without saving?", ["Yes", "No"])
            if c2 == 1:
                break

    conn.close()
