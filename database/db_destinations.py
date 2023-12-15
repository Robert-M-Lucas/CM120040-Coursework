import sqlite3
from typing import Optional

import util
import consts


def get_destinations_from_id(conn: sqlite3.Connection, destination_id: int) -> str:
    """Returns a destination's name given its ID"""
    return conn.execute("SELECT name FROM destinations WHERE id=?", (destination_id,)).fetchone()[0]


def get_destination_code_from_id(conn: sqlite3.Connection, destination_id: int) -> str:
    """Returns a destination's name given its ID"""
    return conn.execute("SELECT code FROM destinations WHERE id=?", (destination_id,)).fetchone()[0]


def get_destination_selection(conn: sqlite3.Connection, base_selection: set[int]) -> set[int]:
    """Allows the user to select multiple destinations"""
    page = 0
    if type(base_selection) != set:
        selection = set(base_selection)
    else:
        selection = base_selection.copy()

    while True:
        rows = conn.execute(
            f"SELECT id, code, name FROM destinations LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()

        has_next = len(rows) > consts.LIMIT_PER_PAGE
        rows = rows[:consts.LIMIT_PER_PAGE]

        print(f"Page: {page + 1}")
        table = [["ID", "Code", "Name", "Selected"]]
        for row in rows:
            table.append(
                [
                    str(row[0]),
                    row[1],
                    row[2],
                    str(row[0] in selection)
                ]
            )

        if len(rows) == 0:
            print("No destinations - add more from main menu")
            print()
            return set()

        util.print_table(table)
        print()

        page_text = ["No Previous Page", "No Next Page"]
        if page > 0:
            page_text[0] = f"Previous Page ({page})"
        if has_next:
            page_text[1] = f"Next Page ({page + 2})"
        c = util.choices("Select an option: ", [page_text[0], page_text[1], "Select/Deselect ID", "Deselect All", "Done"])

        if c == 1:
            if page > 0: page -= 1
        elif c == 2:
            if has_next: page += 1
        elif c == 3:
            print("Enter ID:")
            _id = util.choose_number()
            if conn.execute("SELECT id FROM destinations WHERE id = ?", (_id,)).fetchone() is None:
                print("Invalid ID")
                print()
                continue
            if _id in selection:
                print("Removed from selection")
                selection.remove(_id)
            else:
                print("Added to selection")
                selection.add(_id)
            print()
        elif c == 4:
            selection = set()
        elif c == 5:
            return selection


def get_destination(conn: sqlite3.Connection) -> Optional[int]:
    """Allows the user to select a destinations"""
    page = 0

    while True:
        rows = conn.execute(f"SELECT id, code, name FROM destinations LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()

        has_next = len(rows) > consts.LIMIT_PER_PAGE
        rows = rows[:consts.LIMIT_PER_PAGE]

        print(f"Page: {page + 1}")
        table = [["ID", "Code", "Name"]]
        for row in rows:
            table.append(
                [
                    str(row[0]),
                    row[1],
                    row[2],
                ]
            )

        if len(rows) == 0:
            print("No destinations - add more from main menu")
            print()
            return
        util.print_table(table)
        print()

        page_text = ["No Previous Page", "No Next Page"]
        if page > 0:
            page_text[0] = f"Previous Page ({page})"
        if has_next:
            page_text[1] = f"Next Page ({page + 2})"
        c = util.choices("Select an option: ", [page_text[0], page_text[1], "Select ID"])

        if c == 1:
            if page > 0: page -= 1
        elif c == 2:
            if has_next: page += 1
        elif c == 3:
            print("Enter ID:")
            _id = util.choose_number()
            if conn.execute("SELECT id FROM destinations WHERE id = ?", (_id,)).fetchone() is not None:
                return _id
            print("Invalid ID")
            print()
