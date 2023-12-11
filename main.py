import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Callable, Optional, Tuple, List
import db_initialisation
import db_queries
import util
from db_queries import get_destinations_from_id, get_pilot_from_id, get_aircraft_from_id
from util import print_table, choices, get_datetime_or_none, dt_format

conn = sqlite3.connect("table.db")
db_initialisation.initialise_db(conn)


@dataclass
class DateRange:
    start: datetime = field(default_factory=lambda: datetime.now())
    end: datetime = None

    def get_condition_or_none(self, column: str) -> Optional[tuple[str, list[int]]]:
        if self.start is None and self.end is None:
            return None
        elif self.end is None:
            return f"{column} > ?", [int(self.start.timestamp())]
        elif self.start is None:
            return f"{column} < ?", [int(self.end.timestamp())]
        else:
            return f"{column} > ? AND {column} < ?", [int(self.start.timestamp()), int(self.end.timestamp())]

    def modify(self):
        def time_or_none(dt: datetime) -> str:
            if dt is None: return "Any"
            else: return dt_format(dt)

        while True:
            c = choices("Select an option:", [
                f"Change Start - {time_or_none(self.start)}",
                f"Change End - {time_or_none(self.end)}",
                f"Done"
            ])

            if c == 1: self.start = get_datetime_or_none()
            elif c == 2: self.end = get_datetime_or_none()
            else: break

    def to_string(self) -> str:
        if self.start is None and self.end is None:
            return "Any"
        elif self.end is None:
            return f"After {dt_format(self.start)}"
        elif self.start is None:
            return f"Before {dt_format(self.end)}"
        else:
            return f"From {dt_format(self.start)} to {dt_format(self.end)}"


class MultiSelectionType(Enum):
    DESTINATION = 1
    PILOT = 2
    AIRCRAFT = 3


@dataclass
class MultiSelection:
    selection_type: MultiSelectionType
    selections: set[int] = field(default_factory=list)

    def get_condition_or_none(self) -> Optional[tuple[str, list[int]]]:
        if len(self.selections) == 0: return None

        id_text = ""
        if self.selection_type == MultiSelectionType.DESTINATION:
            return f"destination_id in ({", ".join(["?" for _ in range(len(self.selections))])})", list(self.selections)
        elif self.selection_type == MultiSelectionType.AIRCRAFT:
            return f"aircraft_id in ({", ".join(["?" for _ in range(len(self.selections))])})", list(self.selections)
        elif self.selection_type == MultiSelectionType.PILOT:
            return f"id in (SELECT flight_id FROM pilot_flights WHERE pilot_id in ({", ".join(["?" for _ in range(len(self.selections))])}))", list(self.selections)

    def modify(self):
        global conn
        if self.selection_type == MultiSelectionType.DESTINATION:
            self.selections = db_queries.get_destination_selection(conn, self.selections)
        elif self.selection_type == MultiSelectionType.PILOT:
            self.selections = db_queries.get_pilot_selection(conn, self.selections)
        elif self.selection_type == MultiSelectionType.AIRCRAFT:
            self.selections = db_queries.get_aircraft_selection(conn, self.selections)
    
    def to_string(self) -> str:
        global conn

        def selection_to_string(sel: set[int], f: Callable[[sqlite3.Connection, int], str]) -> str:
            s = "Any"
            if len(sel) != 0:
                s = ", ".join(map(lambda x: f(conn, x), sel))
            return s
        
        g = lambda f: selection_to_string(self.selections, f)
        
        if self.selection_type == MultiSelectionType.DESTINATION: return g(get_destinations_from_id)
        elif self.selection_type == MultiSelectionType.PILOT: return g(get_pilot_from_id)
        elif self.selection_type == MultiSelectionType.AIRCRAFT: return g(get_aircraft_from_id)           


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
        elif c == 9: pass  # Modify/View/Delete flight given an ID
        elif c == 10: pass  # Add flight
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
        "Quit"
    ])

    if c == 1:
        flight_options()
    elif c == 5:
        break

conn.close()
