from datetime import datetime
from app.hardware import zone_on, zone_off
import sqlite3

import time

DB_PATH = "instance/irrigation.db"
DEFAULT_DURATION = 1

_last_run = None


def scheduler_loop():
    global _last_run

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            now = datetime.now()
            now_time = now.strftime("%H:%M")
            today = now.strftime("%Y-%m-%d")

            row = cur.execute("""
                SELECT id, sector
                FROM irrigation_schedule
                WHERE date = ?
                  AND start_time = ?
                  AND enabled = 1
            """, (today, now_time)).fetchone()

            if row and _last_run != now_time:

                sector = row["sector"]
                _last_run = now_time

                print(f"[SCHEDULER] Activando sector {sector}")

                zone_on(sector)

                start_time = datetime.now()

                cur.execute("""
                    INSERT INTO irrigation_log (sector, start_time, type)
                    VALUES (?, ?, 'programado')
                """, (sector, start_time))
                conn.commit()

                time.sleep(DEFAULT_DURATION * 60)

                zone_off(sector)

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE end_time IS NULL
                      AND sector = ?
                      AND type = 'programado'
                """, (datetime.now(), sector))
                conn.commit()

                print(f"[SCHEDULER] Sector {sector} finalizado")

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)
