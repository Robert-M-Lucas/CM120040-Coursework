import sqlite3
from datetime import datetime, timezone
from typing import Optional

from database import db_aircraft
from database import db_destinations
from database import db_pilots


def print_table(table: list[list[str]]):
    """
    Prints a 2D array of strings as a table
    """
    widths = [0 for _ in range(len(table[0]))]

    for row in table:
        for i, s in enumerate(row):
            widths[i] = max(widths[i], len(s))

    for row in table:
        for i, s in enumerate(row):
            print(s + " " * (widths[i] - len(s)), end="    ")
        print()


def choices(heading: str, options: list[str]) -> int:
    """
    Lets user select an option. Returns a 1-indexed choice from the user
    """
    print(heading)
    print("\n".join([str(i + 1) + ". " + t for i, t in enumerate(options)]))
    return choose_number_from_range(1, len(options))


def choose_number() -> int:
    """
    Lets user select any number
    """
    while True:
        try:
            choice = int(input("> "))
            print()
        except ValueError:
            print("Invalid input")
            continue
        return choice


def choose_number_from_range(minimum: int, maximum: int) -> int:
    """
    Lets the user select a number from the given range (inclusive)
    """
    while True:
        try:
            choice = int(input("> "))
            print()
            if choice < minimum or choice > maximum:
                raise ValueError
        except ValueError:
            print("Invalid input")
            continue
        return choice


def choose_number_from_options(options: list[int]) -> int:
    """
    Lets the user choose a number from the list of options
    """
    while True:
        try:
            choice = int(input("> "))
            print()
            if choice not in options:
                raise ValueError
        except ValueError:
            print("Invalid input")
            continue
        return choice


def get_datetime_or_none() -> Optional[datetime]:
    """
    Returns an inputted datetime or None
    """
    while True:
        print("Enter either the date and time in the format 'dd/mm/yyyy hh:mm' or 'None'")
        date_str = input("> ")
        print()
        if date_str.lower() == "none": return None

        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Invalid input")


def get_datetime() -> datetime:
    """
    Returns an inputted datetime
    """
    while True:
        print("Enter either the date and time in the format 'dd/mm/yyyy hh:mm'")
        date_str = input("> ")
        print()

        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Invalid input")


def dt_format(dt: datetime) -> str:
    """
    Formats the datetime as a string
    """
    return dt.strftime("%d/%m/%Y %H:%M")


def print_flight_rows(conn: sqlite3.Connection, rows, limit):
    """
    Formats database flight rows into a table
    """
    table = [["ID", "Departure Time", "Arrival Time", "Source", "Destination", "Aircraft", "Pilot(s)"]]

    for i, row in enumerate(rows):
        if i == limit:
            break

        pilots = list(db_pilots.get_pilots_for_flight(conn, row[0]))
        table.append([
            str(row[0]),
            str(dt_format(db_to_dt(row[1]))),
            str(dt_format(db_to_dt(row[2]))),
            db_destinations.get_destinations_from_id(conn, row[3]),
            db_destinations.get_destinations_from_id(conn, row[4]),
            db_aircraft.get_aircraft_from_id(conn, row[5]),
            db_pilots.get_pilot_from_id(conn, pilots[0]) if len(pilots) > 0 else "[NO PILOTS]"
        ])

        # Append additional pilots
        if len(pilots) > 1:
            for p in pilots[1:]:
                table.append([
                    "", "", "", "", "", "",
                    db_pilots.get_pilot_from_id(conn, p)
                ])

    print_table(table)


def add_or_remove_ids(selection: set[int], all_ids: list[int], assignment: bool) -> bool:
    """
    Allows a user to add or remove ids from a selection given all the valid IDs
    """
    if not assignment:
        choice = choices("Add or Remove", ["Add", "Remove", "Allow Any", "Done"])
    else:
        choice = choices("Add or Remove", ["Add", "Remove", "Remove All", "Done"])

    if choice == 1:
        print("Select ID to add")
        to_add = choose_number_from_options(all_ids)
        if to_add in selection:
            print("ID already selected\n")
        else:
            selection.add(to_add)

    elif choice == 2:
        print("Select ID to remove")
        try:
            selection.remove(choose_number_from_options(all_ids))
        except KeyError:
            print("ID not already selected\n")

    elif choice == 3:
        selection.clear()
    else:
        return True


def ask_commit(conn: sqlite3.Connection):
    """
    Asks the user whether they want to commit and, if so,
    commits the changes to the database
    """
    print("Do you want to save changes now? (Y/N)")
    while True:
        choice = input("> ").lower()
        print()
        if choice == "y":
            conn.commit()
            return
        elif choice == "n":
            return
        print("Invalid input")


def dt_to_db(date: datetime) -> int:
    """
    Converts a datetime object to an int with the SQLite3 DATETIME representation
    """
    return int(date.timestamp() * 1000)


def db_to_dt(timestamp: int) -> datetime:
    """
    Converts a SQLite3 DATETIME representation to a datetime object
    """
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc)
