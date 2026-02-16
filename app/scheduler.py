import sqlite3
from datetime import datetime, time

from app import irrigation_off
from app.db import DB_PATH
from app.hardware import irrigation_on


def scheduler_loop(DEFAULT_DURATION=None):
    global _last_run

    irrigation_off()  # seguridad al arrancar

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

                _last_run = now_time
                sector = row["sector"]

                print(f"[SCHEDULER] Activando sector {sector}")

                # Activar zona
                irrigation_on(sector)

                start_time = datetime.now()

                cur.execute("""
                    INSERT INTO irrigation_log (sector, start_time, type)
                    VALUES (?, ?, 'programado')
                """, (sector, start_time))
                conn.commit()

                # Duración fija
                time.sleep(DEFAULT_DURATION * 60)

                irrigation_off(sector)

                end_time = datetime.now()

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE end_time IS NULL
                      AND sector = ?
                      AND type = 'programado'
                """, (end_time, sector))
                conn.commit()

                print(f"[SCHEDULER] Sector {sector} finalizado")

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)
