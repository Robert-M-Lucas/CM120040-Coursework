import sqlite3
from datetime import datetime, timedelta
from typing import Tuple

import util
from util import dt_to_db, db_to_dt

from database.db_pilots import get_pilot_from_id
from database.db_destinations import get_destinations_from_id
from database.db_aircraft import get_aircraft_from_id


def print_stat(conn: sqlite3.Connection, title: str, table: str, cond: str, params: Tuple) -> None:
    print(f"\t{title}: {conn.execute('SELECT COUNT() FROM ' + table + ' ' + cond, params).fetchone()[0]}")

def show_statistics(conn: sqlite3.Connection):
    print("Flights:")
    total_flights = conn.execute('SELECT COUNT() FROM flights').fetchone()[0]
    print("\tTotal Flights:", total_flights)
    if total_flights == 0:
        print("\t [Remaining statistics omitted due to no flights]")
    else:
        print_stat(conn, "Completed", "flights", "WHERE arrival_time < ?", (dt_to_db(datetime.now()),))
        print_stat(conn, "To Complete", "flights", "WHERE arrival_time > ?", (dt_to_db(datetime.now()),))
        print_stat(conn, "In Flight", "flights", "WHERE departure_time < ? AND arrival_time > ?", (dt_to_db(datetime.now()), dt_to_db(datetime.now())))

        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        print_stat(conn, "Flights departed in last 24h", "flights", "WHERE departure_time > ? AND departure_time < ?", (dt_to_db(start), dt_to_db(end)))

        start = datetime.now()
        end = datetime.now() + timedelta(days=1)
        print_stat(conn, "Flights departing in next 24h", "flights", "WHERE departure_time > ? AND departure_time < ?", (dt_to_db(start), dt_to_db(end)))



        print("\tLast scheduled flight departure: ", end="")
        last = conn.execute("SELECT departure_time FROM flights ORDER BY departure_time DESC").fetchone()[0]
        print(util.dt_format(db_to_dt(last)))

        print("\tLast scheduled flight arrival: ", end="")
        last = conn.execute("SELECT arrival_time FROM flights ORDER BY arrival_time DESC").fetchone()[0]
        print(util.dt_format(db_to_dt(last)))

    print()

    print("Pilots")
    print_stat(conn, "Total Pilots", "pilots", "", ())

    row = conn.execute("SELECT pilot_id, COUNT(pilot_id) AS `frequency` FROM pilot_flights GROUP BY pilot_id ORDER BY `frequency` DESC").fetchone()
    if row is not None:
        pilot, count = row[0], row[1]
        print(f"\tPilot with most scheduled flights (all time): {get_pilot_from_id(conn, pilot)} - {count} flight(s)")

    print()

    print("Destinations")
    print_stat(conn, "Total Destinations", "destinations", "", ())

    row = conn.execute("SELECT destination_id, COUNT(destination_id) AS `frequency` FROM flights GROUP BY destination_id ORDER BY `frequency` DESC").fetchone()
    if row is not None:
        destination, count = row[0], row[1]
        print(f"\tMost popular destination: {get_destinations_from_id(conn, destination)} - {count} flight(s)")

    start = datetime.now()
    end = datetime.now() + timedelta(days=7)
    row = conn.execute(
        "SELECT destination_id, COUNT(destination_id) AS `frequency` FROM flights WHERE departure_time > ? AND departure_time < ? GROUP BY destination_id ORDER BY `frequency` DESC", (dt_to_db(start), dt_to_db(end))).fetchone()
    if row is not None:
        destination, count = row[0], row[1]
        print(f"\tMost popular destination over next week: {get_destinations_from_id(conn, destination)} - {count} flight(s)")

    print()

    print("Aircraft")
    print_stat(conn, "Total Aircraft", "aircraft", "", ())
    row = conn.execute(
        "SELECT aircraft_id, COUNT(aircraft_id) AS `frequency` FROM flights GROUP BY aircraft_id ORDER BY `frequency` DESC").fetchone()
    if row is not None:
        aircraft, count = row[0], row[1]
        print(f"\tMost popular aircraft: {get_aircraft_from_id(conn, aircraft)} - {count} flight(s)")
    print()



    print()
    input("Press enter...")
    print()
