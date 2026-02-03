#!/usr/bin/env python3
import sqlite3
import os
import time
import random
sensor_simulator.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigacion.db")

def random_data():
    return (
        round(random.uniform(15, 35), 1),     # temperature °C
        round(random.uniform(30, 80), 1),     # humidity %
        round(random.uniform(200, 1000), 0),  # solar W/m2
        round(random.uniform(980, 1030), 1),  # pressure hPa
        round(random.uniform(0.5, 3.5), 2),   # EC mS/cm
        round(random.uniform(5.5, 7.5), 2)    # pH
    )

while True:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()

    data = random_data()

    cur.execute("""
        INSERT INTO sensor_data
        (temperature, humidity, solar, pressure, ec, ph)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    print("✔ Datos insertados:", data)
    time.sleep(10)
