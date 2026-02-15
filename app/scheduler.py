from datetime import datetime, timedelta
from app.hardware import irrigation_on, irrigation_off
import sqlite3
import time
import random

DB_PATH = "instance/irrigacion.db"

# CONSTANTS
FLOW_RATE = 8.0        # litros por minuto
WATER_COST = 0.002     # €/litro (ejemplo)
DEFAULT_DURATION = 1   # duración en minutos si no usamos columna duration

_last_run = None

# -------------------------------------------------------
# Función principal del scheduler
# -------------------------------------------------------
def scheduler_loop():
    global _last_run

    # 🔒 Seguridad: al arrancar siempre cerramos riego
    irrigation_off()

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.cursor()

            now = datetime.now()
            now_str = now.strftime("%H:%M")
            today_str = now.strftime("%Y-%m-%d")

            # Buscar riego programado para hoy
            row = cur.execute("""
                SELECT id, sector
                FROM irrigation_schedule
                WHERE start_time = ?
                  AND date = ?
                  AND enabled = 1
            """, (now_str, today_str)).fetchone()

            if row and _last_run != now_str:
                schedule_id, sector = row
                _last_run = now_str

                # ▶️ INICIO RIEGO
                irrigation_on(sector)   # activamos GPIO correspondiente
                start_time = datetime.now()

                cur.execute("""
                    INSERT INTO irrigation_log (sector, start_time, type)
                    VALUES (?, ?, 'programado')
                """, (sector, start_time))
                conn.commit()

                # ⏱️ DURACIÓN FIJA
                time.sleep(DEFAULT_DURATION * 60)

                # ⏹️ FIN RIEGO
                irrigation_off(sector)
                end_time = datetime.now()

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE end_time IS NULL AND sector = ? AND type='programado'
                """, (end_time, sector))
                conn.commit()

                # 💧 Registrar litros y coste
                liters = DEFAULT_DURATION * FLOW_RATE
                cost = liters * WATER_COST

                cur.execute("""
                    INSERT INTO water_consumption (irrigation_id, liters, cost, timestamp)
                    VALUES (
                        (SELECT id FROM irrigation_log ORDER BY id DESC LIMIT 1),
                        ?, ?, ?
                    )
                """, (liters, cost, end_time))
                conn.commit()

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        # ⏲️ Revisar cada 30 segundos
        time.sleep(30)
