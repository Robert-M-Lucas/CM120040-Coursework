import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Callable, Optional, Tuple, List

conn = sqlite3.connect("table.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS aircraft (
    id INTEGER NOT NULL PRIMARY KEY,
    name STRING NOT NULL
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER NOT NULL PRIMARY KEY,
    name STRING NOT NULL
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER NOT NULL PRIMARY KEY,
    source_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    aircraft INTEGER NOT NULL,
    FOREIGN KEY (aircraft) REFERENCES aircraft(id),
    FOREIGN KEY (source_id) REFERENCES destinations(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS pilots (
    id INTEGER NOT NULL PRIMARY KEY,
    name STRING NOT NULL,
    surname STRING NOT NULL
)
""")
conn.execute("""
CREATE TABLE IF NOT EXISTS pilot_flights (
    pilot_id INTEGER NOT NULL,
    flight_id INTEGER NOT NULL,
    PRIMARY KEY (pilot_id, flight_id)
)
""")
conn.commit()


def print_table(table: [[str]]):
    widths = [0 for _ in range(len(table[0]))]

    for row in table:
        for i, s in enumerate(row):
            widths[i] = max(widths[i], len(s))

    for row in table:
        for i, s in enumerate(row):
            print(s + " " * (widths[i] - len(s)), end="    ")
        print()



def choices(heading: str, options: [str]) -> int:
    while True:
        print(heading)
        print("\n".join([str(i + 1) + ". " + t for i, t in enumerate(options)]))

        try:
            choice = int(input("> "))
            print()
            if choice < 1 or choice > len(options):
                raise ValueError
        except ValueError:
            print("Invalid input")
            continue

        return choice


def get_datetime_or_none() -> Optional[datetime]:
    while True:
        print("Enter either the date and time in the format 'dd/mm/yyyy hh:mm' or 'None'")
        date_str = input("> ")
        print()
        if date_str.lower() == "none": return None

        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Invalid input")


def dt_format(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")


def get_destinations_from_id(destination_id: int) -> str:
    global conn
    return conn.execute("SELECT name FROM destinations WHERE id=?", (destination_id,)).fetchone().name


def get_pilot_from_id(pilot_id: int) -> str:
    global conn
    row = conn.execute("SELECT (name, surname) FROM pilots WHERE id=?", (pilot_id,)).fetchone()
    return row.name + " " + row.surname


def get_aircraft_from_id(aircraft_id: int) -> str:
    global conn
    return conn.execute("SELECT (name) FROM aircraft WHERE id=?", (aircraft_id,)).fetchone().name


@dataclass
class DateRange:
    start: datetime = datetime.now()
    end: datetime = None

    def get_condition_or_none(self, column: str) -> Optional[Tuple[str, List[datetime]]]:
        if self.start is None and self.end is None:
            return None
        elif self.end is None:
            return f"{column} > ?", [self.start]
        elif self.start is None:
            return f"{column} < ?", [self.end]
        else:
            return f"{column} > ? AND {column} < ?", [self.start, self.end]

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
    selections: [int] = field(default_factory=list) 
    
    def modify(self):
        pass
    
    def to_string(self) -> str:
        def selection_to_string(sel: [int], f: Callable[[int], str]) -> str:
            s = "Any"
            if len(sel) != 0:
                s = ", ".join(map(f, sel))
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
        order_str = "Date Ascending"
        if not self.ascending:
            order_str = "Date Descending"

        c = choices("Select an option:", [
            f"Change Departure Time Range - {self.departure_time.to_string()}",
            f"Change Arrival Time Range - {self.arrival_time.to_string()}",
            f"Change Sources - {self.sources.to_string()}",
            f"Change Destinations - {self.destinations.to_string()}",
            f"Change Pilots - {self.pilots.to_string()}",
            f"Change Aircraft - {self.aircraft.to_string()}",
            f"Change Results to Display - {self.count}",
            f"Change Result Order - {order_str}",
            f"Modify/View/Delete Flight with ID",
            f"Add Flight"
            f"Return"
        ])

        if c == 1: self.departure_time.modify()
        elif c == 2: self.arrival_time.modify()
        elif c == 3: self.sources.modify()
        elif c == 4: self.destinations.modify()
        elif c == 5: self.pilots.modify()
        elif c == 6:
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
        elif c == 7: pass  # Modify/View/Delete flight given an ID
        elif c == 8: pass  # Add flight
        elif c == 9: return False

        return True

    def display_flights(self):
        conditions = []
        arguments = []

        r = self.departure_time.get_condition_or_none("departure_time")
        if r is not None:
            conditions.append(r[0])
            arguments += r[1]

        r = self.arrival_time.get_condition_or_none("arrival_time")
        if r is not None:
            conditions.append(r[0])
            arguments += r[1]

        if len(conditions) == 0 or True:
            conditions = ""
        else:
            conditions = "WHERE " + " AND ".join(conditions)

        print(conditions)

        rows = conn.execute(f"""
            SELECT id, departure_time, arrival_time, source_id, destination_id FROM flights {conditions}
        """).fetchmany(self.count)

        table = [["ID", "Departure Time", "Arrival Time", "Source", "Destination"]]

        for i, row in enumerate(rows):
            if i == self.count:
                break
            table.append([
                str(row[0]),
                str(dt_format(datetime.fromtimestamp(row[1] / 1000, UTC))),
                str(dt_format(datetime.fromtimestamp(row[2] / 1000, UTC))),
                str(row[3]),
                str(row[4]),
            ])

        print_table(table)

        if len(rows) == 0:
            print("[NO DATA]")
        print()


def flight_options():
    options = FlightSearchOptions()
    options.display_flights()

    while not options.choices():
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
