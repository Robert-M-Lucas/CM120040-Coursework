import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone

from database import db_aircraft
from database import db_destinations
from database import db_pilots
import filters
import util
from typing import Optional, List


@dataclass
class FlightData:
    source_id: Optional[int] = None
    destination_id: Optional[int] = None
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    aircraft_id: Optional[int] = None
    pilots: filters.MultiSelection = field(default_factory=lambda: filters.MultiSelection(filters.MultiSelectionType.PILOT))

    def check(self) -> Optional[str]:
        if self.source_id is None or self.destination_id is None or self.departure_time is None or self.arrival_time is None or self.aircraft_id is None:
            return "Some data hasn't been filled in"
        if len(self.pilots.selection) == 0:
            return "No pilots assigned to flight"
        if self.arrival_time < self.departure_time:
            return "Arrival time is before departure time - no time travelling allowed"
        return None


def modify_flight(conn: sqlite3.Connection, flight_id=None):
    """
    Modifies a flight with the given id. If none is passed in, a new flight is created.
    """
    current_pilots = None
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

        current_pilots = db_pilots.get_pilots_for_flight(conn, flight_id)

        data = FlightData(
            flight_row[0], flight_row[1],
            datetime.fromtimestamp(flight_row[2] / 1000, timezone.utc), datetime.fromtimestamp(flight_row[3] / 1000, timezone.utc),
            flight_row[4],
            filters.MultiSelection(filters.MultiSelectionType.PILOT, current_pilots.copy()),
        )

    while True:
        choice = util.choices("Select an option", [
            f"Change Source - {None if data.source_id is None else db_destinations.get_destinations_from_id(conn, data.source_id)}",
            f"Change Destination - {None if data.destination_id is None else db_destinations.get_destinations_from_id(conn, data.destination_id)}",
            f"Change Departure Time - {None if data.departure_time is None else util.dt_format(data.departure_time)}",
            f"Change Arrival Time - {None if data.arrival_time is None else util.dt_format(data.arrival_time)}",
            f"Change Pilots - {data.pilots.to_string(conn, True)}",
            f"Change Aircraft - {None if data.aircraft_id is None else db_aircraft.get_aircraft_from_id(conn, data.aircraft_id)}",
            f"Delete Flight",
            f"Done",
            f"Cancel"
        ])

        if choice == 1: data.source_id = db_destinations.get_destination(conn)
        elif choice == 2: data.destination_id = db_destinations.get_destination(conn)
        elif choice == 3: data.departure_time = util.get_datetime()
        elif choice == 4: data.arrival_time = util.get_datetime()
        elif choice == 5: data.pilots.modify(conn, True)
        elif choice == 6: data.aircraft_id = db_aircraft.get_aircraft(conn)
        elif choice == 7:
            if flight_id is not None:
                conn.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
                util.ask_commit(conn)
            return
        elif choice == 8:
            check = data.check()
            if check is not None:
                print(check)
                print()
                continue
            if flight_id is None:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO flights (source_id, destination_id, departure_time, arrival_time, aircraft_id)  VALUES (?, ?, ?, ?, ?)",
                    (
                        data.source_id, data.destination_id,
                        int(data.departure_time.timestamp() * 1000), int(data.arrival_time.timestamp() * 1000),
                        data.aircraft_id
                    )
                )
                flight_id = cursor.lastrowid
            else:
                conn.execute(
                    "UPDATE flights SET (source_id, destination_id, departure_time, arrival_time, aircraft_id) = (?, ?, ?, ?, ?) WHERE id = ?",
                    (
                        data.source_id, data.destination_id,
                        int(data.departure_time.timestamp() * 1000), int(data.arrival_time.timestamp() * 1000),
                        data.aircraft_id,
                        flight_id
                    )
                )

            all_pilots: set[int] = data.pilots.selection.copy()
            if current_pilots is not None:
                for p in current_pilots:
                    try:
                        all_pilots.remove(p)
                    except KeyError:
                        pass

            for p in all_pilots:
                conn.execute("INSERT INTO pilot_flights (pilot_id, flight_id) VALUES (?, ?)", (p, flight_id))

            util.ask_commit(conn)
            return
        elif choice == 9:
            c2 = util.choices("Are you sure you don't want to save your changes?", ["Yes", "No"])
            if c2 == 1:
                return
            