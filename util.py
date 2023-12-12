from datetime import datetime, UTC
from typing import Optional


def print_table(table: list[list[str]]):
    widths = [0 for _ in range(len(table[0]))]

    for row in table:
        for i, s in enumerate(row):
            widths[i] = max(widths[i], len(s))

    for row in table:
        for i, s in enumerate(row):
            print(s + " " * (widths[i] - len(s)), end="    ")
        print()


def choices(heading: str, options: list[str]) -> int:
    print(heading)
    print("\n".join([str(i + 1) + ". " + t for i, t in enumerate(options)]))
    return choose_number_from_range(1, len(options))


def choose_number() -> int:
    while True:
        try:
            choice = int(input("> "))
            print()
        except ValueError:
            print("Invalid input")
            continue
        return choice


def choose_number_from_range(minimum: int, maximum: int) -> int:
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
    while True:
        print("Enter either the date and time in the format 'dd/mm/yyyy hh:mm'")
        date_str = input("> ")
        print()

        try:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Invalid input")


def dt_format(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")


def print_flight_rows(rows, limit):
    table = [["ID", "Departure Time", "Arrival Time", "Source", "Destination"]]

    for i, row in enumerate(rows):
        if i == limit:
            break
        table.append([
            str(row[0]),
            str(dt_format(datetime.fromtimestamp(row[1] / 1000, UTC))),
            str(dt_format(datetime.fromtimestamp(row[2] / 1000, UTC))),
            str(row[3]),
            str(row[4]),
        ])

    print_table(table)


def add_or_remove_ids(selection: set[int], all_ids: list[int], assignment: bool) -> bool:
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
        return True
    else:
        return True