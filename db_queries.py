import sqlite3

import util


def get_destinations_from_id(conn: sqlite3.Connection, destination_id: int) -> str:
    return conn.execute("SELECT name FROM destinations WHERE id=?", (destination_id,)).fetchone()[0]


def get_pilot_from_id(conn: sqlite3.Connection, pilot_id: int) -> str:
    row = conn.execute("SELECT name, surname FROM pilots WHERE id=?", (pilot_id,)).fetchone()
    return row[0] + " " + row[1]


def get_aircraft_from_id(conn: sqlite3.Connection, aircraft_id: int) -> str:
    return conn.execute("SELECT name FROM aircraft WHERE id=?", (aircraft_id,)).fetchone()[0]


def add_or_remove_ids(selection: set[int], all_ids: list[int]) -> bool:
    choice = util.choices("Add or Remove", ["Add", "Remove", "Allow Any", "Done"])
    if choice == 1:
        print("Select ID to add")
        to_add = util.choose_number_from_options(all_ids)
        if to_add in selection:
            print("ID already selected\n")
        else:
            selection.add(to_add)
    elif choice == 2:
        print("Select ID to remove")
        try:
            selection.remove(util.choose_number_from_options(all_ids))
        except KeyError:
            print("ID not already selected\n")
    elif choice == 3:
        selection.clear()
        return True
    else:
        return True


def get_destination_selection(conn: sqlite3.Connection, base_selection: set[int]) -> set[int]:
    selection = set(base_selection.copy())
    rows = conn.execute("SELECT id, name FROM destinations").fetchall()

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

        util.print_table(table)
        if len(rows) == 0:
            print("[NO DATA]")
        print()

        if add_or_remove_ids(selection, all_ids):
            return selection


def get_pilot_selection(conn: sqlite3.Connection, base_selection: set[int]) -> set[int]:
    selection = set(base_selection.copy())
    rows = conn.execute("SELECT id, name, surname FROM pilots").fetchall()

    while True:
        table = [["ID", "Name", "Surname", "Selected"]]
        all_ids = []
        for row in rows:
            all_ids.append(row[0])
            table.append(
                [
                    str(row[0]),
                    row[1],
                    row[2],
                    "True" if row[0] in selection else "False"
                ]
            )

        util.print_table(table)
        if len(rows) == 0:
            print("[NO DATA]")
        print()

        if add_or_remove_ids(selection, all_ids):
            return selection


def get_aircraft_selection(conn: sqlite3.Connection, base_selection: set[int]) -> set[int]:
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

        util.print_table(table)
        if len(rows) == 0:
            print("[NO DATA]")
        print()

        if add_or_remove_ids(selection, all_ids):
            return selection


def modify_flight_with_id(conn: sqlite3.Connection, flight_id: int):
    while True:
        row = conn.execute("SELECT source_id, destination_id, departure_time, arrival_time FROM flights WHERE id = ?", (flight_id,)).fetchone()
        if row is None:
            print("Invalid ID")
            print()
            return

        util.print_flight_rows([row], 1)
        print()

        rows = conn.execute("SELECT id, name, surname FROM pilots where id in (SELECT pilot_id FROM pilot_flights WHERE flight_id = ?)", (flight_id,)).fetchall()
        table = [["ID", "Name", "Surname"]]
        for r in rows:
            table.append([
                str(r[0]),
                r[1],
                r[2]
            ])

        util.print_table(table)
        if len(rows) == 0:
            print("[NO PILOTS]")

        choice = util.choices("Select an option", [
            "Change Source",
            "Change Destination",
            "Change Departure Time",
            "Change Arrival Time",
            "Add Pilot",
            "Remove Pilot",
            "Change Aircraft",
            "Delete Flight",
            "Done"
        ])


