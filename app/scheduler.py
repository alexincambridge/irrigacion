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
            now_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            today = now.strftime("%Y-%m-%d")

            # Buscar riegos activos ahora mismo
            rows = cur.execute("""
                SELECT id, sector, start_time, end_time, duration_minutes
                FROM irrigation_schedule
                WHERE date = ?
                  AND enabled = 1
                  AND start_time <= ?
                  AND end_time > ?
            """, (today, now_time, now_time)).fetchall()

            active_schedules = {row["sector"]: row for row in rows}

            # Buscar riegos que ya terminaron
            finished_rows = cur.execute("""
                SELECT id, sector, start_time, end_time, duration_minutes
                FROM irrigation_schedule
                WHERE date = ?
                  AND enabled = 1
                  AND end_time <= ?
            """, (today, now_time)).fetchall()

            # Marcar como finalizados y registrar en log
            for row in finished_rows:
                schedule_id = row["id"]
                sector = row["sector"]
                start_time = row["start_time"]
                end_time = row["end_time"]
                duration = row["duration_minutes"]

                # Buscar si ya está registrado
                existing_log = cur.execute("""
                    SELECT id FROM irrigation_log
                    WHERE sector = ?
                    AND start_time LIKE ?
                    AND end_time IS NOT NULL
                    AND type = 'programado'
                """, (sector, f"{today} {start_time}%")).fetchone()

                if not existing_log:
                    # Registrar en log
                    cur.execute("""
                        INSERT INTO irrigation_log 
                        (sector, start_time, end_time, type, scheduled_id, duration_minutes, status)
                        VALUES (?, ?, ?, 'programado', ?, ?, 'completado')
                    """, (sector, f"{today} {start_time}", f"{today} {end_time}", schedule_id, duration))

                # Marcar como desactivado
                cur.execute("""
                    UPDATE irrigation_schedule
                    SET enabled = 0
                    WHERE id = ?
                """, (schedule_id,))

                conn.commit()

            # Comprobar todos los sectores
            for sector in [1, 2, 3, 4]:

                if sector in active_schedules:
                    if not zone_state(sector):
                        zone_on(sector)

                        schedule = active_schedules[sector]
                        cur.execute("""
                            INSERT OR IGNORE INTO irrigation_log 
                            (sector, start_time, type, scheduled_id, duration_minutes, status)
                            VALUES (?, ?, 'programado', ?, ?, 'activo')
                        """, (sector, now_datetime, schedule["id"], schedule["duration_minutes"]))
                        conn.commit()

                else:
                    if zone_state(sector):
                        zone_off(sector)

                        cur.execute("""
                            UPDATE irrigation_log
                            SET end_time = ?, status = 'completado'
                            WHERE end_time IS NULL
                              AND sector = ?
                              AND type = 'programado'
                        """, (now_datetime, sector))
                        conn.commit()

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)
