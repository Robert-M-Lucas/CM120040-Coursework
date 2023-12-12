import sqlite3
from dataclasses import dataclass, field

import db_flights
import util
from filters import DateRange, MultiSelection, MultiSelectionType
from util import choices


@dataclass
class FlightSearchOptions:
    departure_time: DateRange = field(default_factory=DateRange)
    arrival_time: DateRange = field(default_factory=DateRange)
    sources: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.DESTINATION))
    destinations: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.DESTINATION))
    pilots: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.PILOT))
    aircraft: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.AIRCRAFT))
    count: int = 5
    ascending: bool = True

    def choices(self, conn: sqlite3.Connection) -> int:
        c = choices("Select an option:", [
            f"Change Departure Time Range - {self.departure_time.to_string()}",
            f"Change Arrival Time Range - {self.arrival_time.to_string()}",
            f"Change Sources - {self.sources.to_string(conn)}",
            f"Change Destinations - {self.destinations.to_string(conn)}",
            f"Change Pilots - {self.pilots.to_string(conn)}",
            f"Change Aircraft - {self.aircraft.to_string(conn)}",
            f"Change Results to Display - {self.count}",
            f"Change Result Order - Departure Time {"Ascending" if self.ascending else "Descending"}",
            f"View/Modify/Delete Flight",
            f"Add Flight",
            f"Return"
        ])

        if c == 1: self.departure_time.modify()
        elif c == 2: self.arrival_time.modify()
        elif c == 3: self.sources.modify(conn)
        elif c == 4: self.destinations.modify(conn)
        elif c == 5: self.pilots.modify(conn)
        elif c == 6: self.aircraft.modify(conn)
        elif c == 7:
            while True:
                print("Choose an amount of results to display:")
                choice = input("> ")
                print()
                try:
                    choice = int(choice)
                    if choice < 1:
                        raise ValueError
                except ValueError:
                    print("Invalid Input")
                    continue
                self.count = choice
                break
        elif c == 8: self.ascending = not self.ascending
        elif c == 9:
            print("Enter flight ID:")
            db_flights.modify_flight(conn, util.choose_number())
        elif c == 10:
            db_flights.modify_flight(conn, None)
        elif c == 11: return False

        return True

    def display_flights(self, conn: sqlite3.Connection):
        conditions = []
        arguments = []

        temp = [
            self.departure_time.get_condition_or_none("departure_time"),
            self.arrival_time.get_condition_or_none("arrival_time"),
            self.sources.get_condition_or_none(),
            self.destinations.get_condition_or_none(),
            self.pilots.get_condition_or_none()
        ]

        for r in temp:
            if r is not None:
                conditions.append(r[0])
                arguments += r[1]

        if len(conditions) == 0:
            conditions = ""
        else:
            conditions = "WHERE " + " AND ".join(conditions)

        rows = conn.execute(f"""
            SELECT id, departure_time, arrival_time, source_id, destination_id, aircraft_id FROM flights {conditions} ORDER BY departure_time {"ASC" if self.ascending else "DESC"}""", arguments).fetchmany(self.count)

        util.print_flight_rows(conn, rows, self.count)

        if len(rows) == 0:
            print("[NO DATA FOR CRITERIA]")
        print()


def flight_options(conn: sqlite3.Connection):
    options = FlightSearchOptions()
    options.display_flights(conn)

    while options.choices(conn):
        options.display_flights(conn)
