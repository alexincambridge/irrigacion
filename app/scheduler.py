from datetime import datetime
from app.hardware import zone_on, zone_off, zone_state
import sqlite3

import time

DB_PATH = "instance/irrigation.db"
DEFAULT_DURATION = 1

_last_run = None


def scheduler_loop():

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            now = datetime.now()
            now_time = now.strftime("%H:%M")
            today = now.strftime("%Y-%m-%d")

            # Buscar riegos activos ahora mismo
            rows = cur.execute("""
                SELECT sector
                FROM irrigation_schedule
                WHERE date = ?
                  AND enabled = 1
                  AND start_time <= ?
                  AND end_time > ?
            """, (today, now_time, now_time)).fetchall()

            active_sectors = {row["sector"] for row in rows}

            # Comprobar todos los sectores
            for sector in [1, 2, 3]:

                if sector in active_sectors:
                    if not zone_state(sector):
                        zone_on(sector)

                        cur.execute("""
                            INSERT INTO irrigation_log (sector, start_time, type)
                            VALUES (?, ?, 'programado')
                        """, (sector, now.strftime("%Y-%m-%d %H:%M:%S")))
                        conn.commit()

                else:
                    if zone_state(sector):
                        zone_off(sector)

                        cur.execute("""
                            UPDATE irrigation_log
                            SET end_time = ?
                            WHERE end_time IS NULL
                              AND sector = ?
                              AND type = 'programado'
                        """, (now.strftime("%Y-%m-%d %H:%M:%S"), sector))
                        conn.commit()

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)
