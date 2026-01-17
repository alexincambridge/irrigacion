import time
import sqlite3
from app.hardware import read_dht

DB_PATH = "database/irrigation.db"

def scheduler_loop():
    while True:
        t, h = read_dht()

        if t is not None and h is not None:
            db = sqlite3.connect(DB_PATH, timeout=5)
            db.execute("PRAGMA journal_mode=WAL;")
            db.execute(
                "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)",
                (t, h)
            )
            db.commit()
            db.close()

        time.sleep(60)
