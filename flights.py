import sqlite3
from dataclasses import dataclass, field

from database import db_flights
import util
from filters import DateRange, MultiSelection, MultiSelectionType
from util import choices
import consts


@dataclass
class FlightSearchOptions:
    departure_time: DateRange = field(default_factory=DateRange)
    arrival_time: DateRange = field(default_factory=DateRange)
    sources: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.DESTINATION))
    destinations: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.DESTINATION))
    pilots: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.PILOT))
    aircraft: MultiSelection = field(default_factory=lambda: MultiSelection(MultiSelectionType.AIRCRAFT))
    ascending: bool = True
    page: int = 0
    has_next_page: bool = False

    def modify(self, conn: sqlite3.Connection) -> int:
        """
        Allow users to modify the search criteria or add/modify/delete flights
        """
        page_text = ["No Previous Page", "No Next Page"]

        if self.page > 0:
            page_text[0] = f"Previous Page ({self.page})"
        if self.has_next_page:
            page_text[1] = f"Next Page ({self.page + 2})"

        c = choices("Select an option:", [
            f"Change Departure Time Range - {self.departure_time.to_string()}",
            f"Change Arrival Time Range - {self.arrival_time.to_string()}",
            f"Change Sources - {self.sources.to_string(conn)}",
            f"Change Destinations - {self.destinations.to_string(conn)}",
            f"Change Pilots - {self.pilots.to_string(conn)}",
            f"Change Aircraft - {self.aircraft.to_string(conn)}",
            f"Change Result Order - Departure Time {'Ascending' if self.ascending else 'Descending'}",
            page_text[0],
            page_text[1],
            f"View/Modify/Delete Flight",
            f"Add Flight",
            f"Return"
        ])

        reset_page = True

        if c == 1: self.departure_time.modify()
        elif c == 2: self.arrival_time.modify()
        elif c == 3: self.sources.modify(conn)
        elif c == 4: self.destinations.modify(conn)
        elif c == 5: self.pilots.modify(conn)
        elif c == 6: self.aircraft.modify(conn)
        # Change ordering
        elif c == 7: self.ascending = not self.ascending
        # Prev page
        elif c == 8:
            if self.page > 0:
                self.page -= 1
            reset_page = False
        # Next page
        elif c == 9:
            if self.has_next_page:
                self.page += 1
            reset_page = False
        # Modify flight
        elif c == 10:
            print("Enter flight ID:")
            db_flights.modify_flight(conn, util.choose_number())
        # New flight
        elif c == 11:
            db_flights.modify_flight(conn, None)
        # Done
        elif c == 12: return False

        if reset_page:
            self.page = 0

        return True

    def display_flights(self, conn: sqlite3.Connection):
        """
        Displays the flights given the current search options
        """
        conditions = []
        arguments = []

        # All search conditions
        temp = [
            self.departure_time.get_condition_or_none("departure_time"),
            self.arrival_time.get_condition_or_none("arrival_time"),
            self.sources.get_condition_or_none(),
            self.destinations.get_condition_or_none(),
            self.pilots.get_condition_or_none()
        ]

        for r in temp:
            if r is not None:
                # Apply condition
                conditions.append(r[0])
                arguments += r[1]

        if len(conditions) == 0:
            conditions = ""
        else:
            conditions = "WHERE " + " AND ".join(conditions)

        rows = conn.execute(
            f"SELECT id, departure_time, arrival_time, source_id, destination_id, aircraft_id FROM flights "
            f"{conditions} ORDER BY departure_time {'ASC' if self.ascending else 'DESC'} LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * self.page}",
            arguments
        ).fetchall()

        self.has_next_page = False
        if len(rows) > consts.LIMIT_PER_PAGE:
            self.has_next_page = True
            rows = rows[:consts.LIMIT_PER_PAGE]

        print(f"Page: {self.page + 1}")
        util.print_flight_rows(conn, rows, consts.LIMIT_PER_PAGE)

        if len(rows) == 0:
            print("[NO DATA FOR CRITERIA]")
        print()


def flight_options(conn: sqlite3.Connection):
    """
    Allows users to view and modify flights
    """
    options = FlightSearchOptions()
    options.display_flights(conn)

    while options.modify(conn):
        options.display_flights(conn)
