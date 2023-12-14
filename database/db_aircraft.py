import sqlite3
from typing import Optional

import util


def get_aircraft_from_id(conn: sqlite3.Connection, aircraft_id: int) -> str:
    """Returns the aircraft's name given its ID"""
    return conn.execute("SELECT name FROM aircraft WHERE id=?", (aircraft_id,)).fetchone()[0]


def get_aircraft_selection(conn: sqlite3.Connection, base_selection: set[int], assignment: bool) -> set[int]:
    """Allows the user to select multiple aircraft"""
    selection = set(base_selection.copy())
    rows = conn.execute("SELECT id, name FROM aircraft").fetchall()

    while True:
        table = [["ID", "Name", "Selected"]]
        all_ids = []
        for row in rows:
            all_ids.append(row[0])
            table.append(
                [
                    str(row[0]),
                    row[1],
                    "True" if row[0] in selection else "False"
                ]
            )

        if len(all_ids) == 0:
            print("No aircraft - add more from main menu")
            print()
            return set()

        util.print_table(table)
        print()

        if util.add_or_remove_ids(selection, all_ids, assignment):
            return selection


def get_aircraft(conn: sqlite3.Connection) -> Optional[int]:
    """Allows the user to select an aircraft"""
    rows = conn.execute("SELECT id, name FROM aircraft").fetchall()
    table = [["ID", "Name"]]
    all_ids = []
    for row in rows:
        all_ids.append(row[0])
        table.append(
            [
                str(row[0]),
                row[1],
            ]
        )

    if len(all_ids) == 0:
        print("No aircraft - add more from main menu")
        print()
        return
    util.print_table(table)
    print()

    print("Select aircraft:")
    return util.choose_number_from_options(all_ids)
