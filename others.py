import sqlite3
from enum import Enum

import util


class OthersType(Enum):
    AIRCRAFT = 1
    DESTINATIONS = 2
    PILOTS = 3

    def get_name(self) -> str:
        if self == OthersType.AIRCRAFT:
            return "Aircraft"
        elif self == OthersType.DESTINATIONS:
            return "Destination"
        elif self == OthersType.PILOTS:
            return "Pilot"


def others_options(conn: sqlite3.Connection, others_type: OthersType):
    while True:
        if others_type == OthersType.AIRCRAFT:
            rows = conn.execute("SELECT id, name FROM aircraft").fetchall()
            table = [["ID", "Name"]]
        elif others_type == OthersType.DESTINATIONS:
            rows = conn.execute("SELECT id, name FROM destinations").fetchall()
            table = [["ID", "Name"]]
        elif others_type == OthersType.PILOTS:
            rows = conn.execute("SELECT id, name, surname FROM pilots").fetchall()
            table = [["ID", "Name", "Surname"]]

        for row in rows:
            if others_type == OthersType.PILOTS:
                table.append([str(row[0]), row[1], row[2]])
            else:
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

        if choice == 1:
            print("Enter name:")
            name = input("> ")
            print()

            if others_type == OthersType.PILOTS:
                print("Enter surname:")
                surname = input("> ")
                print()

                conn.execute("INSERT INTO pilots (name, surname) VALUES (?, ?)", (name, surname))
            elif others_type == OthersType.AIRCRAFT:
                conn.execute("INSERT INTO aircraft (name) VALUES (?) ", (name,))
            elif others_type == OthersType.DESTINATIONS:
                conn.execute("INSERT INTO destinations (name) VALUES (?)", (name,))

        elif choice == 2:
            print("Enter ID:")
            id = input("> ")
            print()

            if others_type == OthersType.PILOTS:
                rows = conn.execute("SELECT flight_id FROM pilot_flights WHERE pilot_id = ?", (id,)).fetchall()

                to_delete = []

                for row in rows:
                    pilots_on_flight = conn.execute("SELECT pilot_id FROM pilot_flights WHERE flight_id = ?", (row[0],)).fetchall()
                    if len(pilots_on_flight) == 1:
                        to_delete.append(row[0])

                if len(to_delete) > 0:
                    print(f"Deleting this pilot will result in {len(to_delete)} flight(s) ({", ".join([str(d for d in to_delete)])}) being deleted due to having no pilot")
                    c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                    if c2 == 2: continue
                    conn.execute("DELETE FROM pilots WHERE id = ?", (id,))
                    for flight_id in to_delete:
                        conn.execute("DELETE FROM flights WHERE id = ?", (flight_id,))
            else:
                if others_type == OthersType.AIRCRAFT:
                    deleted = list(map(lambda x: x[0], conn.execute("SELECT id FROM flights WHERE aircraft_id = ?", (id,)).fetchall()))
                elif others_type == OthersType.DESTINATIONS:
                    deleted = list(map(lambda x: x[0], conn.execute("SELECT id FROM flights WHERE source_id = ? OR destination_id = ?", (id, id)).fetchall()))

                print(f"Deleting this {others_type.get_name().lower()} will result in {len(deleted)} flight(s) ({", ".join([str(d for d in deleted)])}) being deleted due to having no {others_type.get_name().lower()}")
                c2 = util.choices("Are you sure you want to continue?", ["Yes", "No"])
                if c2 == 2: continue

                if others_type == OthersType.AIRCRAFT:
                    conn.execute("DELETE FROM aircraft where id = ?", (id,))
                elif others_type == OthersType.DESTINATIONS:
                    conn.execute("DELETE FROM destinations where id = ?", (id,))

        elif choice == 3:
            util.ask_commit(conn)
            return
