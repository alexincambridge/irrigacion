import sqlite3
from app.config import DB_PATH

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

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
