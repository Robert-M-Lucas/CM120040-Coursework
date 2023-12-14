import sqlite3


def check_for_errors(conn: sqlite3.Connection):
    # Arrival time before departure
    rows = conn.execute("SELECT * FROM flights WHERE departure_time > arrival_time").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have their arrival time set before their departure time:")
        for row in rows:
            print("\t" + str(row[0]))
    else:
        print("All arrival times occur after departure times")

    # Flights with invalid aircraft
    rows = conn.execute("SELECT flights.id FROM flights LEFT JOIN aircraft ON flights.aircraft_id = aircraft.id WHERE aircraft.id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have invalid aircraft IDs:")
        for row in rows:
            print("\t" + str(row[0]))
    else:
        print("All flights have valid aircraft IDs")

    # Flights with invalid locations
    rows = conn.execute("SELECT flights.id FROM flights LEFT JOIN destinations ON flights.source_id = destinations.id WHERE destinations.id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have invalid departure location IDs:")
        for row in rows:
            print("\t" + str(row[0]))
    else:
        print("All flights have valid departure location IDs")

    # Contd.
    rows = conn.execute("SELECT flights.id FROM flights LEFT JOIN destinations ON flights.destination_id = destinations.id WHERE destinations.id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have invalid destination IDs:")
        for row in rows:
            print("\t" + str(row[0]))
    else:
        print("All flights have valid destination IDs")

    # Pilot-Flights table row with invalid pilot / flight
    rows = conn.execute("SELECT pilot_flights.pilot_id, pilot_flights.flight_id FROM pilot_flights LEFT JOIN flights ON pilot_flights.flight_id = flights.id WHERE flights.id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following pilot IDs have been assigned to invalid flight IDs:")
        for row in rows:
            print("\t" + str(row[0]) + " (Invalid flight: " + str(row[1]) + ")")
    else:
        print("All pilots have been assigned to flights with valid IDs")

    # Contd.
    rows = conn.execute("SELECT pilot_flights.flight_id, pilot_flights.pilot_id FROM pilot_flights LEFT JOIN pilots ON pilot_flights.pilot_id = pilots.id WHERE pilots.id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have been assigned invalid pilot IDs:")
        for row in rows:
            print("\t" + str(row[0]) + " (Invalid pilot: " + str(row[1]) + ")")
    else:
        print("All flights have been assigned pilots with valid IDs")

    # Flights with no pilots assigned to them
    rows = conn.execute("SELECT flights.id, pilot_flights.pilot_id AS `frequency` FROM flights LEFT JOIN pilot_flights ON flights.id = pilot_flights.flight_id WHERE pilot_flights.pilot_id IS NULL").fetchall()
    if len(rows) > 0:
        print("The following flight IDs have no pilots assigned to them:")
        for row in rows:
            print("\t" + str(row[0]))
    else:
        print("All flights have at least one pilot")

    print()

    print("Checks complete")
    print()
