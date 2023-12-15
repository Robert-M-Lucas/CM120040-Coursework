import sqlite3

conn = sqlite3.connect("test.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS test (
    id INTEGER PRIMARY KEY,
    test_col VARCHAR(4)
)
""")

conn.commit()

conn.execute("""
INSERT INTO test (test_col) VALUES ("Too Long")
""")

conn.commit()
conn.close()

