import sqlite3
import time
from datetime import datetime, timedelta

from app.hardware import zone_on, zone_off, irrigation_off, irrigation_on
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")
DB_PATH = "instance/irrigacion.db"


conn = sqlite3.connect(DB_PATH, timeout=10)

def scheduler_loop():

    irrigation_off()
    last_trigger = None

    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            now = datetime.now()
            now_hm = now.strftime("%H:%M")

            row = cur.execute("""
                SELECT sector
                FROM irrigation_schedule
                WHERE start_time = ?
                  AND enabled = 1
            """, (now_hm,)).fetchone()

            if row and last_trigger != now_hm:

                sector = row[0]
                print(f"Activando sector {sector}")

                zone_on(sector)

                cur.execute("""
                    INSERT INTO irrigation_log (sector, start_time, type)
                    VALUES (?, ?, 'programado')
                """, (sector, now))

                conn.commit()

                last_trigger = now_hm

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(20)
