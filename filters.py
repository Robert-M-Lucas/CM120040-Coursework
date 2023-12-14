import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable

import util
from database import db_aircraft
from database import db_destinations
from database import db_pilots
from database.db_aircraft import get_aircraft_from_id
from database.db_destinations import get_destinations_from_id
from database.db_pilots import get_pilot_from_id

from util import dt_format, choices, get_datetime_or_none


@dataclass
class DateRange:
    """Class representing a range of dates"""
    start: Optional[datetime] = field(default_factory=lambda: datetime.now())
    end: Optional[datetime] = None

    def get_condition_or_none(self, column: str) -> Optional[tuple[str, list[int]]]:
        """Returns (SQL condition, arguments) or None based on data"""
        if self.start is None and self.end is None:
            return None
        elif self.end is None:
            return f"{column} > ?", [util.dt_to_db(self.start)]
        elif self.start is None:
            return f"{column} < ?", [util.dt_to_db(self.end)]
        else:
            return f"{column} > ? AND {column} < ?", [int(self.start.timestamp()), int(self.end.timestamp())]

    def modify(self):
        """Allows the user to modify the date range"""
        def time_or_none_to_str(dt: Optional[datetime]) -> str:
            if dt is None: return "Any"
            else: return dt_format(dt)

        while True:
            c = choices("Select an option:", [
                f"Change Start - {time_or_none_to_str(self.start)}",
                f"Change End - {time_or_none_to_str(self.end)}",
                f"Done"
            ])

            if c == 1: self.start = get_datetime_or_none()
            elif c == 2: self.end = get_datetime_or_none()
            else: break

    def to_string(self) -> str:
        """Converts the date range to a user-readable string"""
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
    """Class representing a multi-selection of IDs"""
    selection_type: MultiSelectionType
    selection: set[int] = field(default_factory=list)

    def get_condition_or_none(self) -> Optional[tuple[str, list[int]]]:
        """Returns (SQL condition, arguments) or None based on data"""
        if len(self.selection) == 0: return None

        if self.selection_type == MultiSelectionType.DESTINATION:
            return f"destination_id in ({', '.join(['?' for _ in range(len(self.selection))])})", list(self.selection)
        elif self.selection_type == MultiSelectionType.AIRCRAFT:
            return f"aircraft_id in ({', '.join(['?' for _ in range(len(self.selection))])})", list(self.selection)
        elif self.selection_type == MultiSelectionType.PILOT:
            return (
                f"id in (SELECT flight_id FROM pilot_flights WHERE "
                f"pilot_id in ({', '.join(['?' for _ in range(len(self.selection))])}))",
                list(self.selection)
            )

    def modify(self, conn: sqlite3.Connection, assignment=False):
        """Allows the user to modify the selection"""
        if self.selection_type == MultiSelectionType.DESTINATION:
            self.selection = db_destinations.get_destination_selection(conn, self.selection, assignment)
        elif self.selection_type == MultiSelectionType.PILOT:
            self.selection = db_pilots.get_pilot_selection(conn, self.selection, assignment)
        elif self.selection_type == MultiSelectionType.AIRCRAFT:
            self.selection = db_aircraft.get_aircraft_selection(conn, self.selection, assignment)

    def to_string(self, conn: sqlite3.Connection, assignment=False) -> str:
        """Converts the selection to a user-readable string"""
        def selection_to_string(sel: set[int], f: Callable[[sqlite3.Connection, int], str], a: bool) -> str:
            if a:
                s = "None"
            else:
                s = "Any"
            if len(sel) != 0:
                s = ", ".join(map(lambda x: f(conn, x), sel))
            return s

        string_builder = lambda f: selection_to_string(self.selection, f, assignment)

        if self.selection_type == MultiSelectionType.DESTINATION: return string_builder(get_destinations_from_id)
        elif self.selection_type == MultiSelectionType.PILOT: return string_builder(get_pilot_from_id)
        elif self.selection_type == MultiSelectionType.AIRCRAFT: return string_builder(get_aircraft_from_id)
