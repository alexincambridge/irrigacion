from datetime import datetime, timedelta
from app.hardware import irrigation_on, irrigation_off

import sqlite3
import time
import random

DB_PATH = "instance/irrigacion.db"

# CONSTANTS
FLOW_RATE = 8.0        # litros por minuto
WATER_COST = 0.002    # €/litro (ejemplo)

_last_run = None



def check_schedule(cur):
    global _last_run
    now = datetime.now().strftime("%H:%M")

    row = cur.execute("""
        SELECT id, duration
        FROM irrigation_schedule
        WHERE start_time = ? AND enabled = 1
    """, (now,)).fetchone()

    if row and _last_run != now:
        irrigation_on()
        _last_run = now
        return row[1]  # duración en minutos
    return None



# def scheduler_loop():
#
#     while True:
#         conn = sqlite3.connect(DB_PATH, timeout=10)
#         cur = conn.cursor()
#
#         temperature = round(random.uniform(15, 35), 1)
#         humidity    = round(random.uniform(30, 80), 1)
#         solar       = round(random.uniform(200, 1000), 0)
#         pressure    = round(random.uniform(980, 1030), 1)
#         ec          = round(random.uniform(0.5, 3.5), 2)
#         ph          = round(random.uniform(5.5, 7.5), 2)
#
#         cur.execute("""
#             INSERT INTO sensor_data
#             (temperature, humidity, solar, pressure, ec, ph)
#             VALUES (?, ?, ?, ?, ?, ?)
#         """, (temperature, humidity, solar, pressure, ec, ph))
#
#         conn.commit()
#         conn.close()
#
#         time.sleep(10)
#
#         duration = check_schedule(cur)
#         if duration :
#             time.sleep(duration * 60)
#             irrigation_off()

def scheduler_loop():
    global _last_run

    # 🔒 Seguridad: al arrancar SIEMPRE cerramos riego
    irrigation_off()

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.cursor()

            now = datetime.now()
            now_hm = now.strftime("%H:%M")

            # Buscar riego programado
            row = cur.execute("""
                SELECT id, duration
                FROM irrigation_schedule
                WHERE start_time = ?
                  AND enabled = 1
            """, (now_hm,)).fetchone()

            if row and _last_run != now_hm:
                schedule_id, duration = row
                _last_run = now_hm

                # ▶️ INICIO RIEGO
                irrigation_on()
                start_time = datetime.now()

                cur.execute("""
                    INSERT INTO irrigation_log (start_time, duration)
                    VALUES (?, ?)
                """, (start_time, duration))
                conn.commit()

                # ⏱️ DURACIÓN
                time.sleep(duration * 60)

                # ⏹️ FIN RIEGO
                irrigation_off()
                end_time = datetime.now()

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE end_time IS NULL
                """, (end_time,))
                conn.commit()

                liters = duration * FLOW_RATE
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

