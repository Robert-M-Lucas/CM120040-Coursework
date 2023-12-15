import sqlite3
from faker import Faker
import random
from datetime import datetime, timezone, timedelta
from util import dt_to_db, db_to_dt

faker: Faker = Faker()

if __name__ != "__main__":
    exit(-1)

conn = sqlite3.connect("table.db")

pilot_count = int(input("How many pilots do you want to add: "))

for _ in range(pilot_count):
    name = faker.first_name()
    surname = faker.last_name()
    date_joined = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 365 * 5))
    conn.execute("INSERT INTO pilots (name, surname, date_joined) VALUES (?, ?, ?)", (name, surname, dt_to_db(date_joined)))


location_count = int(input("How many locations do you want to add: "))

for _ in range(location_count):
    city = faker.city()
    code = ""
    for word in city.split(" "):
        code += word[0]

    if len(code) < 3:
        code += "".join(reversed(city.split(" ")))

    if len(code) > 4:
        code = code[:3]
    code = code.upper()

    latitude = float(faker.latitude())
    longitude = float(faker.longitude())
    conn.execute("INSERT INTO destinations (name, code, latitude, longitude) VALUES (?, ?, ?, ?)", (city, code, latitude, longitude))


aircraft_count = int(input("How many aircraft do you want to add: "))

for _ in range(aircraft_count):
    name = faker.last_name() + str(random.randint(1, 99) * 100)
    conn.execute("INSERT INTO aircraft (name) VALUES (?)", (name,))

flight_count = int(input("How many flights do you want to add: "))
spacing = int(input("Spacing between flights (h): "))
valid_pilots = [r[0] for r in conn.execute("SELECT id FROM pilots").fetchall()]
valid_aircraft = [r[0] for r in conn.execute("SELECT id FROM aircraft").fetchall()]
valid_destinations = [r[0] for r in conn.execute("SELECT id FROM destinations").fetchall()]

aircraft = random.choices(valid_aircraft, k=flight_count)
sources = random.choices(valid_destinations, k=flight_count)
destinations = random.choices(valid_destinations, k=flight_count)
pilots = random.choices(valid_pilots, k=flight_count)
co_pilots = random.choices(valid_pilots + [None for _ in range(len(valid_pilots))], k=flight_count)

t = datetime.now(tz=timezone.utc)
for i in range(flight_count):
    takeoff = t
    t += timedelta(hours=random.randint(1, 2), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    landing = t
    t += timedelta(hours=spacing, minutes=random.randint(0, 59))

    source = sources[i]
    destination = destinations[i]

    aircraft_id = aircraft[i]

    c = conn.cursor()

    c.execute("INSERT INTO flights (source_id, destination_id, departure_time, arrival_time, aircraft_id) VALUES (?, ?, ?, ?, ?)", (source, destination, dt_to_db(takeoff), dt_to_db(landing), aircraft_id))

    flight_id = c.lastrowid

    c.execute("INSERT INTO pilot_flights (pilot_id, flight_id) VALUES (?, ?)", (pilots[i], flight_id))

    if co_pilots[i] is not None and co_pilots[i] != pilots[i]:
        c.execute("INSERT INTO pilot_flights (pilot_id, flight_id) VALUES (?, ?)", (co_pilots[i], flight_id))

input("Press Enter to commit")
conn.commit()
conn.close()