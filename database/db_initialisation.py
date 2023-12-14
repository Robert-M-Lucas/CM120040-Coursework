import sqlite3


def initialise_db() -> sqlite3.Connection:
    """Initialises the database creating the database, tables and setting flags"""
    conn = sqlite3.connect("table.db")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS aircraft (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        longitude REAL NOT NULL,
        latitude REAL NOT NULL,
        code VARCHAR(4) NOT NULL
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
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL,
        destination_id INTEGER NOT NULL,
        departure_time DATETIME NOT NULL,
        arrival_time DATETIME NOT NULL,
        aircraft_id INTEGER NOT NULL,
        FOREIGN KEY (aircraft_id) REFERENCES aircraft(id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES destinations(id) ON DELETE CASCADE,
        FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pilot_flights (
        pilot_id INTEGER NOT NULL,
        flight_id INTEGER NOT NULL,
        FOREIGN KEY (pilot_id) REFERENCES pilots(id) ON DELETE CASCADE,
        FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
        PRIMARY KEY (pilot_id, flight_id)
    )
    """)

    # conn.execute("INSERT INTO aircraft (id, name) VALUES (?, ?)", (0, "Undefined"))
    # conn.execute("INSERT INTO destinations (id, name) VALUES (?, ?)", (0, "Undefined"))

    conn.commit()
    return conn