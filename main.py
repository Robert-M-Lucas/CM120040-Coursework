import sqlite3
from dataclasses import dataclass, field
from enum import Enum

import db_flights
import db_initialisation
import db_queries
import util
from filters import DateRange, MultiSelection, MultiSelectionType
from util import choices

conn = sqlite3.connect("table.db")
db_initialisation.initialise_db(conn)


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

    def choices(self) -> int:
        c = choices("Select an option:", [
            f"Change Departure Time Range - {self.departure_time.to_string()}",
            f"Change Arrival Time Range - {self.arrival_time.to_string()}",
            f"Change Sources - {self.sources.to_string()}",
            f"Change Destinations - {self.destinations.to_string()}",
            f"Change Pilots - {self.pilots.to_string()}",
            f"Change Aircraft - {self.aircraft.to_string()}",
            f"Change Results to Display - {self.count}",
            f"Change Result Order - {"Date Ascending" if self.ascending else "Date Descending"}",
            f"Modify/View/Delete Flight with ID",
            f"Add Flight",
            f"Return"
        ])

        if c == 1: self.departure_time.modify()
        elif c == 2: self.arrival_time.modify()
        elif c == 3: self.sources.modify()
        elif c == 4: self.destinations.modify()
        elif c == 5: self.pilots.modify()
        elif c == 6: self.aircraft.modify()
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
            db_flights.modify_flight(conn)
        elif c == 10:
            db_flights.modify_flight(conn, None)
        elif c == 11: return False

        return True

    def display_flights(self):
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
            SELECT id, departure_time, arrival_time, source_id, destination_id FROM flights {conditions}
        """, arguments).fetchmany(self.count)

        util.print_flight_rows(rows, self.count)

        if len(rows) == 0:
            print("[NO DATA FOR CRITERIA]")
        print()


def flight_options():
    options = FlightSearchOptions()
    options.display_flights()

    while options.choices():
        options.display_flights()


while True:
    c = choices("Select data:", [
        "Flights",
        "Pilots",
        "Aircraft",
        "Destinations",
        "Save and Quit"
    ])

    if c == 1:
        flight_options()
    elif c == 5:
        conn.commit()
        break

conn.close()
