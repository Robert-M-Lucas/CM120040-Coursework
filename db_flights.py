import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, UTC

import db_aircraft
import util
from typing import Optional, List


@dataclass
class FlightData:
    source_id: Optional[int] = None,
    destination_id: Optional[int] = None,
    departure_time: Optional[datetime] = None,
    arrival_time: Optional[datetime] = None,
    aircraft_id: Optional[int] = None,
    existing_pilots: List[int] = field(default_factory=list)
    new_pilots: List[int] = field(default_factory=list)
    remove_pilots: List[int] = field(default_factory=list)


def modify_flight(conn: sqlite3.Connection, flight_id=None):
    if flight_id is None:
        data = FlightData()
    else:
        flight_row = conn.execute(
            "SELECT source_id, destination_id, departure_time, arrival_time, aircraft_id FROM flights WHERE id = ?",
            (flight_id,)).fetchone()
        if flight_row is None:
            print("Invalid Flight ID")
            print()
            return

        pilots = conn.execute("SELECT pilot_id from pilot_flights WHERE flight_id = ?", (flight_id,)).fetchall()

        data = FlightData(
            flight_row[0], flight_row[1],
            datetime.fromtimestamp(flight_row[2] / 1000, UTC), datetime.fromtimestamp(flight_row[3] / 1000, UTC),
            flight_row[4],
            [x[0] for x in pilots], [], []
        )

    while True:
        choice = util.choices("Select an option", [
            f"Change Source - {data.source_id}",
            f"Change Destination - {data.destination_id}",
            f"Change Departure Time - {None if data.departure_time is None else util.dt_format(data.departure_time)}",
            f"Change Arrival Time - {None if data.arrival_time is None else util.dt_format(data.arrival_time)}",
            f"Change Pilots",
            f"Change Aircraft",
            f"Delete Flight",
            f"Done",
        ])

        if choice == 1: pass
        elif choice == 2: pass
        elif choice == 3: data.departure_time = util.get_datetime()
        elif choice == 4: data.arrival_time = util.get_datetime()
        elif choice == 5: pass
        elif choice == 7: data.aircraft_id = db_aircraft.get_aircraft(conn)
