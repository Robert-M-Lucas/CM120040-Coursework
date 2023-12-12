import sqlite3


def initialise_db(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS aircraft (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        destination_id INTEGER NOT NULL,
        departure_time DATETIME NOT NULL,
        arrival_time DATETIME NOT NULL,
        aircraft_id INTEGER NOT NULL,
        FOREIGN KEY (aircraft_id) REFERENCES aircraft(id),
        FOREIGN KEY (source_id) REFERENCES destinations(id),
        FOREIGN KEY (destination_id) REFERENCES destinations(id)
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pilots (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pilot_flights (
        pilot_id INTEGER NOT NULL,
        flight_id INTEGER NOT NULL,
        PRIMARY KEY (pilot_id, flight_id)
    )
    """)

    # conn.execute("INSERT INTO aircraft (id, name) VALUES (?, ?)", (0, "Undefined"))
    # conn.execute("INSERT INTO destinations (id, name) VALUES (?, ?)", (0, "Undefined"))

    conn.commit()
