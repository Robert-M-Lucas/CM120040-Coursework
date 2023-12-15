import sqlite3

import consts
import util


def get_pilot_from_id(conn: sqlite3.Connection, pilot_id: int) -> str:
    """Returns a pilots name given their ID"""
    row = conn.execute("SELECT name, surname FROM pilots WHERE id=?", (pilot_id,)).fetchone()
    if row is None: return "[NO PILOT]"
    return row[0] + " " + row[1]


def get_pilot_selection(conn: sqlite3.Connection, base_selection: set[int]) -> set[int]:
    """Allows the user to select multiple pilots"""
    page = 0
    if type(base_selection) != set:
        selection = set(base_selection)
    else:
        selection = base_selection.copy()

    while True:
        rows = conn.execute(
            f"SELECT id, name, surname FROM pilots LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()

        has_next = len(rows) > consts.LIMIT_PER_PAGE
        rows = rows[:consts.LIMIT_PER_PAGE]

        print(f"Page: {page + 1}")
        table = [["ID", "Name", "Surname", "Selected"]]
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
        c = util.choices("Select an option: ",
                         [page_text[0], page_text[1], "Select/Deselect ID", "Deselect All", "Done"])

        if c == 1:
            if page > 0: page -= 1
        elif c == 2:
            if has_next: page += 1
        elif c == 3:
            print("Enter ID:")
            _id = util.choose_number()
            if conn.execute("SELECT id FROM pilots WHERE id = ?", (_id,)).fetchone() is None:
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


def get_pilots_for_flight(conn: sqlite3.Connection, flight_id: int) -> set[int]:
    """Returns all the pilots on a given flight"""
    pilots = conn.execute("SELECT pilot_id from pilot_flights WHERE flight_id = ?", (flight_id,)).fetchall()
    return {p[0] for p in pilots}
