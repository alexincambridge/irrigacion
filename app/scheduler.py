import sqlite3
import time
import random

DB_PATH = "instance/irrigacion.db"

def scheduler_loop():
    while True:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()

        temperature = round(random.uniform(15, 35), 1)
        humidity    = round(random.uniform(30, 80), 1)
        solar       = round(random.uniform(200, 1000), 0)
        pressure    = round(random.uniform(980, 1030), 1)
        ec          = round(random.uniform(0.5, 3.5), 2)
        ph          = round(random.uniform(5.5, 7.5), 2)

        cur.execute("""
            INSERT INTO sensor_data
            (temperature, humidity, solar, pressure, ec, ph)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (temperature, humidity, solar, pressure, ec, ph))

        conn.commit()
        conn.close()

        time.sleep(10)
