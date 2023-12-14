import sqlite3
from enum import Enum

import util


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


def non_flight_options(conn: sqlite3.Connection, others_type: NonFlightType):
    while True:
        if others_type == NonFlightType.AIRCRAFT:
            rows = conn.execute("SELECT id, name FROM aircraft").fetchall()
            table = [["ID", "Name"]]
        elif others_type == NonFlightType.DESTINATIONS:
            rows = conn.execute("SELECT id, name FROM destinations").fetchall()
            table = [["ID", "Name"]]
        else: # others_type == NonFlightType.PILOTS:
            rows = conn.execute("SELECT id, name, surname FROM pilots").fetchall()
            table = [["ID", "Name", "Surname"]]

        all_ids = []
        for row in rows:
            all_ids.append(int(row[0]))
            if others_type == NonFlightType.PILOTS:
                # ID, Name, Surname
                table.append([str(row[0]), row[1], row[2]])
            else:
                # ID, Name
                table.append([str(row[0]), row[1]])

        util.print_table(table)
        if len(rows) == 0:
            print("[NO DATA]")
        print()

        choice = util.choices("Select an option:", [
            f"Add {others_type.get_name()}",
            f"Remove {others_type.get_name()}",
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

                conn.execute("INSERT INTO pilots (name, surname) VALUES (?, ?)", (name, surname))
            elif others_type == NonFlightType.AIRCRAFT:
                conn.execute("INSERT INTO aircraft (name) VALUES (?) ", (name,))
            elif others_type == NonFlightType.DESTINATIONS:
                conn.execute("INSERT INTO destinations (name) VALUES (?)", (name,))
        # Remove
        elif choice == 2:
            print("Enter ID:")
            _id = util.choose_number_from_options(all_ids)

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

                    if len(pilots_on_flight) == 1:
                        to_delete.append(row[0])

                if len(to_delete) > 0:
                    print(f"Deleting this pilot will result in {len(to_delete)} flight(s) "
                          f"(ID(s): {', '.join([str(d) for d in to_delete])}) being deleted due to having no pilot")

                    c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                    if c2 == 2: continue

                conn.execute("DELETE FROM pilots WHERE id = ?", (_id,))
                for flight_id in to_delete:
                    conn.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
            else:
                if others_type == NonFlightType.AIRCRAFT:
                    deleted = list(map(
                        lambda x: x[0],
                        conn.execute("SELECT id FROM flights WHERE aircraft_id = ?", (_id,)).fetchall()
                    ))
                elif others_type == NonFlightType.DESTINATIONS:
                    deleted = list(map(
                        lambda x: x[0],
                        conn.execute(
                            "SELECT id FROM flights WHERE source_id = ? OR destination_id = ?",
                            (_id, _id)
                        ).fetchall()
                    ))

                print(f"Deleting this {others_type.get_name().lower()} will result in {len(deleted)} flight(s) "
                      f"(ID(s): {', '.join([str(d) for d in deleted])}) being deleted due to having no "
                      f"{others_type.get_name().lower()}")

                c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                if c2 == 2: continue
                if others_type == NonFlightType.AIRCRAFT:
                    conn.execute("DELETE FROM aircraft where id = ?", (_id,))
                elif others_type == NonFlightType.DESTINATIONS:
                    conn.execute("DELETE FROM destinations where id = ?", (_id,))
        # Done
        elif choice == 3:
            util.ask_commit(conn)
            return
