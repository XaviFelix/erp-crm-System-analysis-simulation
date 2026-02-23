import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'erp.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')
SEED_PATH = os.path.join(os.path.dirname(__file__), 'seed.sql')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db(seed: bool = True):
    conn = get_connection()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    if seed:
        cur = conn.execute("SELECT COUNT(*) FROM departments")
        if cur.fetchone()[0] == 0:
            with open(SEED_PATH, 'r') as f:
                conn.executescript(f.read())
            print("[DB] Database initialized and seeded successfully.")
        else:
            print("[DB] Database already contains data — skipping seed.")
    conn.commit()
    conn.close()


def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[DB] Existing database removed.")
    initialize_db(seed=True)
    print("[DB] Database reset complete.")


if __name__ == '__main__':
    initialize_db()
