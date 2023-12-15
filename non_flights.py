import sqlite3
from enum import Enum

import util
import consts

class NonFlightType(Enum):
    AIRCRAFT = 1
    DESTINATIONS = 2
    PILOTS = 3

    def get_name(self) -> str:
        if self == NonFlightType.AIRCRAFT:
            return "Aircraft"
        elif self == NonFlightType.DESTINATIONS:
            return "Destination"
        elif self == NonFlightType.PILOTS:
            return "Pilot"

    def get_table(self) -> str:
        if self == NonFlightType.AIRCRAFT:
            return "aircraft"
        elif self == NonFlightType.DESTINATIONS:
            return "destinations"
        elif self == NonFlightType.PILOTS:
            return "pilots"


def non_flight_options(conn: sqlite3.Connection, others_type: NonFlightType):
    """
    Allows user to view, add and remove data from the aircraft, destination and pilots tables
    """

    page = 0

    while True:
        # Get data
        if others_type == NonFlightType.AIRCRAFT:
            rows = conn.execute(f"SELECT id, name FROM aircraft LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()
            table = [["ID", "Name"]]
        elif others_type == NonFlightType.DESTINATIONS:
            rows = conn.execute(f"SELECT id, code, name, latitude, longitude FROM destinations LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()
            table = [["ID", "Code", "Name", "Latitude", "Longitude"]]
        else:  # others_type == NonFlightType.PILOTS:
            rows = conn.execute(f"SELECT id, name, surname, date_joined FROM pilots LIMIT {consts.LIMIT_PER_PAGE + 1} OFFSET {consts.LIMIT_PER_PAGE * page}").fetchall()
            table = [["ID", "Name", "Surname", "Date Joined"]]  # Extra column for pilots

        all_ids = []
        has_next = False
        if len(rows) > consts.LIMIT_PER_PAGE:
            rows = rows[:consts.LIMIT_PER_PAGE]
            has_next = True

        # Add data to table
        for row in rows:
            all_ids.append(int(row[0]))
            if others_type == NonFlightType.PILOTS:
                # ID, Name, Surname, Date Joined
                table.append([str(row[0]), row[1], row[2], util.dt_format_no_time(util.db_to_dt(row[3]))])
            elif others_type == NonFlightType.DESTINATIONS:
                # ID, Code, Name, Lat, Long
                table.append([str(row[0]), row[1], row[2], str(row[3]), str(row[4])])
            else:
                # ID, Name
                table.append([str(row[0]), row[1]])

        # Output table
        print(f"Page: {page + 1}")
        util.print_table(table)
        if len(rows) == 0:
            print("[NO DATA]")
        print()

        page_text = ["No Previous Page", "No Next Page"]
        if page > 0:
            page_text[0] = f"Previous Page ({page})"
        if has_next:
            page_text[1] = f"Next Page ({page + 2})"

        choice = util.choices("Select an option:", [
            f"Add {others_type.get_name()}",
            f"Remove {others_type.get_name()}",
            page_text[0],
            page_text[1],
            f"Done"
        ])

        # Add
        if choice == 1:
            print("Enter name:")
            name = input("> ")
            print()

            if others_type == NonFlightType.PILOTS:
                print("Enter surname:")
                surname = input("> ")
                print()

                print("Enter date joined:")
                date_joined = util.get_datetime_no_time()

                conn.execute("INSERT INTO pilots (name, surname, date_joined) VALUES (?, ?, ?)", (name, surname, util.dt_to_db(date_joined)))
            elif others_type == NonFlightType.AIRCRAFT:
                conn.execute("INSERT INTO aircraft (name) VALUES (?) ", (name,))
            elif others_type == NonFlightType.DESTINATIONS:
                print("Enter code:")
                while True:
                    code = input("> ")
                    if len(code) == 0 or len(code) > 4:
                        print("Code must be 1 - 4 characters")
                        continue
                    print()
                    break

                print("Enter latitude")
                lat = util.choose_float_range(-90.0, 90.0)
                print("Enter longitude")
                long = util.choose_float_range(-180.0, 180.0)

                conn.execute("INSERT INTO destinations (name, code, latitude, longitude) VALUES (?, ?, ?, ?)", (name, code.upper(), lat, long))
        # Remove
        elif choice == 2:
            print("Enter ID:")
            while True:
                _id = util.choose_number()
                if conn.execute(f"SELECT id FROM {others_type.get_table()} WHERE id = ?", (_id,)).fetchone() is not None:
                    break
                print("Invalid ID")

            if others_type == NonFlightType.PILOTS:
                rows = conn.execute(
                    "SELECT flight_id FROM pilot_flights WHERE pilot_id = ?",
                    (_id,)
                ).fetchall()

                to_delete = []
                for row in rows:
                    pilots_on_flight = conn.execute(
                        "SELECT pilot_id FROM pilot_flights WHERE flight_id = ?",
                        (row[0],)
                    ).fetchall()

                    # Flight will need to be deleted if last pilot is gone
                    if len(pilots_on_flight) == 1:
                        to_delete.append(row[0])

                if len(to_delete) > 0:
                    print(f"Deleting this pilot will result in {len(to_delete)} flight(s) "
                          f"(ID(s): {', '.join([str(d) for d in to_delete])}) being deleted due to having no pilot")

                    c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                    if c2 == 2: continue

                conn.execute("DELETE FROM pilots WHERE id = ?", (_id,))

                # Delete flights with no pilots
                for flight_id in to_delete:
                    conn.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
            else:
                # Get flights that will be cascade deleted
                if others_type == NonFlightType.AIRCRAFT:
                    deleted = list(map(
                        lambda x: x[0],
                        conn.execute("SELECT id FROM flights WHERE aircraft_id = ?", (_id,)).fetchall()
                    ))
                else:  # others_type == NonFlightType.DESTINATIONS:
                    deleted = list(map(
                        lambda x: x[0],
                        conn.execute(
                            "SELECT id FROM flights WHERE source_id = ? OR destination_id = ?",
                            (_id, _id)
                        ).fetchall()
                    ))

                if len(deleted) > 0:
                    print(f"Deleting this {others_type.get_name().lower()} will result in {len(deleted)} flight(s) "
                          f"(ID(s): {', '.join([str(d) for d in deleted])}) being deleted due to having no "
                          f"{others_type.get_name().lower()}")

                    c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                    if c2 == 2: continue

                if others_type == NonFlightType.AIRCRAFT:
                    conn.execute("DELETE FROM aircraft where id = ?", (_id,))
                elif others_type == NonFlightType.DESTINATIONS:
                    conn.execute("DELETE FROM destinations where id = ?", (_id,))
                # Flights will be deleted automatically

        # Previous page
        elif choice == 3:
            if page > 0:
                page -= 1

        # Next page
        elif choice == 4:
            if has_next:
                page += 1

        # Done
        elif choice == 5:
            util.ask_commit(conn)
            return
