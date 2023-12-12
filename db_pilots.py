import sqlite3

import util


def get_pilot_from_id(conn: sqlite3.Connection, pilot_id: int) -> str:
    row = conn.execute("SELECT name, surname FROM pilots WHERE id=?", (pilot_id,)).fetchone()
    return row[0] + " " + row[1]


def get_pilot_selection(conn: sqlite3.Connection, base_selection: set[int], assignment: bool) -> set[int]:
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

        if util.add_or_remove_ids(selection, all_ids, assignment):
            return selection