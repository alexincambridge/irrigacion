import sqlite3
from flask import g

DB_PATH = "database/irrigation.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            timeout=5,
            check_same_thread=False
        )
        g.db.execute("PRAGMA journal_mode=WAL;")
    return g.db


def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data(
        id INTEGER PRIMARY KEY,
        temperature REAL,
        humidity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS irrigation_log(
        id INTEGER PRIMARY KEY,
        mode TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    db.commit()

def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()