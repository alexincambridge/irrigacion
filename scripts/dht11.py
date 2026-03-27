#!/usr/bin/env python3
"""
Generador de datos simulados para pruebas
Inserta datos aleatorios en sensor_data para dashboard histórico

⚠️  SOLO USAR PARA DESARROLLO/PRUEBAS
✅ En producción, usa sensor_data_logger.py con sensores reales
"""

import sqlite3
import os
import time
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

def random_sensor_data():
    """Generar datos simulados realistas"""
    return (
        round(random.uniform(15, 35), 1),     # temperature °C
        round(random.uniform(30, 80), 1),     # humidity %
        round(random.uniform(200, 1000), 0),  # solar W/m2
        round(random.uniform(980, 1030), 1),  # pressure hPa
        round(random.uniform(0.5, 3.5), 2),   # EC mS/cm
        round(random.uniform(5.5, 7.5), 2)    # pH
    )

def insert_simulation_data():
    """Insertar datos simulados"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()

    data = random_sensor_data()

    cur.execute(
        """
        INSERT INTO sensor_data
        (temperature, humidity, solar, pressure, ec, ph, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (*data, datetime.now())
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("🎲 SIMULADOR DE DATOS - Pruebas solamente")
    print("=" * 60)
    print(f"BD: {DB_PATH}")
    print("Insertando datos cada 5 segundos...")
    print("Presiona Ctrl+C para detener")
    print("=" * 60)
    print()

    try:
        while True:
            insert_simulation_data()
            data = random_sensor_data()
            print(
                f"[✅] T={data[0]:.1f}°C | H={data[1]:.1f}% | "
                f"S={data[2]:.0f}W/m² | P={data[3]:.1f}hPa | "
                f"pH={data[5]:.2f} | EC={data[4]:.2f}mS/cm"
            )
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[⛔ STOP] Detenido")

