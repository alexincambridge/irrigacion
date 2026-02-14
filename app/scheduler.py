import sqlite3
import time
from datetime import datetime, timedelta

from app.hardware import zone_on, zone_off, irrigation_off
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

conn = sqlite3.connect(DB_PATH, timeout=10)

def scheduler_loop():
    global _last_run

    irrigation_off()  # seguridad al arrancar

    active_irrigation = None
    active_log_id = None
    irrigation_end_time = None
    active_sector = None

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.cursor()

            now = datetime.now()
            now_hm = now.strftime("%H:%M")

            # 1️⃣ Buscar nuevo riego
            if active_irrigation is None:

                row = cur.execute("""
                    SELECT id, sector, duration
                    FROM irrigation_schedule
                    WHERE start_time = ?
                      AND enabled = 1
                """, (now_hm,)).fetchone()

                if row and _last_run != now_hm:
                    schedule_id, sector, duration = row
                    _last_run = now_hm

                    zone_on(sector)

                    irrigation_end_time = now + timedelta(minutes=duration)
                    active_irrigation = schedule_id
                    active_sector = sector

                    cur.execute("""
                        INSERT INTO irrigation_log (sector, start_time)
                        VALUES (?, ?)
                    """, (sector, now))

                    active_log_id = cur.lastrowid
                    conn.commit()

            # 2️⃣ Finalizar riego
            if active_irrigation and now >= irrigation_end_time:

                zone_off(active_sector)

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE id = ?
                """, (now, active_log_id))

                conn.commit()

                active_irrigation = None
                active_log_id = None
                irrigation_end_time = None
                active_sector = None

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)
