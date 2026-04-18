from datetime import datetime
from app.hardware_manager import zone_on, zone_off, zone_state
from app.notifications import notify_irrigation_completed, notify_irrigation_started
import sqlite3
import os
import time
import logging

logger = logging.getLogger(__name__)

# Use absolute path (same as app/db.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")
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

                # Apagar la zona si sigue encendida
                if zone_state(sector):
                    zone_off(sector)

                # Buscar si ya está registrado (evitar duplicados)
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

                    # 📱 Telegram: riego programado completado (solo 1 vez)
                    notify_irrigation_completed(
                        sector,
                        f"{today} {start_time}",
                        f"{today} {end_time}",
                        duration,
                        "programado"
                    )

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

                        # 📱 Telegram: riego programado iniciado
                        notify_irrigation_started(sector, "programado")

                else:
                    # No active schedule for this sector
                    # ONLY turn off if zone is on AND there's no manual irrigation active
                    if zone_state(sector):
                        manual_active = cur.execute("""
                            SELECT id FROM irrigation_log
                            WHERE sector = ?
                              AND type = 'manual'
                              AND end_time IS NULL
                            LIMIT 1
                        """, (sector,)).fetchone()

                        if manual_active:
                            # Manual irrigation running — don't touch it
                            pass
                        else:
                            # No manual, no schedule — orphaned zone, turn off
                            logger.info(f"[Scheduler] Zona {sector} encendida sin schedule ni manual → apagando")
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
            logger.error(f"Scheduler error: {e}")

        time.sleep(10)
