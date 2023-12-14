import sqlite3

import util


def get_destinations_from_id(conn: sqlite3.Connection, destination_id: int) -> str:
    return conn.execute("SELECT name FROM destinations WHERE id=?", (destination_id,)).fetchone()[0]


def get_destination_selection(conn: sqlite3.Connection, base_selection: set[int], assignment: bool) -> set[int]:
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

        if util.add_or_remove_ids(selection, all_ids, assignment):
            return selection


def get_destination(conn: sqlite3.Connection) -> int:
    rows = conn.execute("SELECT id, name FROM destinations").fetchall()

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

    util.print_table(table)
    if len(rows) == 0:
        print("[NO DATA]")
    print()

    return util.choose_number_from_options(all_ids)
