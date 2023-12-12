import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

import db_queries
from main import MultiSelectionType

from util import dt_format, choices, get_datetime_or_none


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
