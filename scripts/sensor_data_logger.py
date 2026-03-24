"""
Logger para sensores adicionales (presión, pH, EC, radiación solar)
Inserta datos en la tabla sensor_data

NOTA: Este script genera datos de SIMULACIÓN.
Reemplaza las funciones read_* con lecturas reales cuando tengas los sensores.
"""

import time
import sqlite3
import random
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "instance" / "irrigation.db"
INTERVAL = 10  # segundos entre lecturas

def read_pressure():
    """
    Lee presión del agua en hPa
    TODO: Conectar sensor de presión real (ej: MPX5700)
    """
    # Por ahora: simulación
    return round(random.uniform(1000, 1020), 1)

def read_solar():
    """
    Lee radiación solar en W/m²
    TODO: Conectar fotodiodo o sensor solar real
    """
    # Por ahora: simulación (más alta durante el día)
    return round(random.uniform(50, 1000), 0)

def read_ph():
    """
    Lee pH del agua
    TODO: Conectar sensor de pH real (ej: DFRobot Analog pH)
    """
    # Por ahora: simulación
    return round(random.uniform(6.0, 7.5), 2)

def read_ec():
    """
    Lee conductividad eléctrica (EC) en mS/cm
    TODO: Conectar sensor EC real (ej: DFRobot Analog EC)
    """
    # Por ahora: simulación
    return round(random.uniform(0.5, 2.5), 2)

def insert_sensor_data(temp, humidity, solar, pressure, ec, ph):
    """Insertar datos en tabla sensor_data"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sensor_data 
        (temperature, humidity, solar, pressure, ec, ph, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (temp, humidity, solar, pressure, ec, ph, datetime.now())
    )
    conn.commit()
    conn.close()

def get_latest_dht_reading():
    """Obtener última lectura del DHT22 de la BD"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()
        cur.execute(
            "SELECT temperature, humidity FROM dht_readings ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()

        if row:
            return row[0], row[1]  # temp, humidity
    except Exception as e:
        print(f"[⚠️  Error al leer DHT de BD] {e}")

    return None, None

def main():
    print("📊 Sensor Data Logger iniciado")
    print("=" * 60)
    print(f"Sensores: Presión, Radiación Solar, pH, EC")
    print(f"Intervalo: {INTERVAL}s")
    print(f"BD: {DB_PATH}")
    print("=" * 60)
    print("⚠️  NOTA: Datos simulados. Reemplaza read_* con sensores reales.")
    print("=" * 60)

    while True:
        try:
            # Obtener datos del DHT22 más reciente
            temp, humidity = get_latest_dht_reading()

            if temp is None or humidity is None:
                print("[⚠️  INFO] Esperando primeras lecturas del DHT22...")
                time.sleep(INTERVAL)
                continue

            # Leer sensores adicionales
            pressure = read_pressure()
            solar = read_solar()
            ph = read_ph()
            ec = read_ec()

            # Guardar en BD
            insert_sensor_data(temp, humidity, solar, pressure, ec, ph)

            print(
                f"[✅ OK] T={temp:.1f}°C | H={humidity:.1f}% | "
                f"P={pressure:.1f}hPa | S={solar:.0f}W/m² | "
                f"pH={ph:.2f} | EC={ec:.2f}mS/cm"
            )

        except Exception as e:
            print(f"[❌ ERROR] {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[⛔ STOP] Detenido por usuario")

