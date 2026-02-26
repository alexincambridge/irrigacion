#!/usr/bin/env python3
"""
Script para generar datos de sensores aleatorios en la BD
para visualizar en el histórico del dashboard
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

DB_PATH = "instance/irrigation.db"

def generate_sensor_data():
    """Genera datos aleatorios de sensores para las últimas 24 horas"""

    if not os.path.exists(DB_PATH):
        print("❌ Base de datos no encontrada.")
        return False

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        print("🔄 Generando datos de sensores...")

        # Generar datos para las últimas 24 horas
        now = datetime.now()

        for i in range(48):  # 48 puntos = cada 30 minutos durante 24 horas
            timestamp = now - timedelta(hours=24) + timedelta(minutes=i*30)

            # Generar datos realistas
            temperature = round(random.uniform(15, 35), 1)  # 15-35°C
            humidity = round(random.uniform(30, 90), 1)     # 30-90%
            solar = round(random.uniform(0, 1000), 1)       # 0-1000 W/m²
            pressure = round(random.uniform(1010, 1030), 1) # 1010-1030 hPa
            ec = round(random.uniform(0.5, 3.0), 2)         # 0.5-3.0 mS/cm
            ph = round(random.uniform(6.0, 8.5), 1)         # 6.0-8.5

            # Insertar en BD
            cur.execute("""
                INSERT INTO sensor_data 
                (temperature, humidity, solar, pressure, ec, ph, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (temperature, humidity, solar, pressure, ec, ph,
                  timestamp.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        print(f"✅ Se generaron 48 registros de datos de sensores")
        print(f"   Período: últimas 24 horas")
        print(f"   Sensores: Temperatura, Humedad, Solar, Presión, EC, pH")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  GENERADOR DE DATOS DE SENSORES")
    print("=" * 60)
    print()

    success = generate_sensor_data()

    print()
    if success:
        print("🎉 Datos generados correctamente!")
        print("   Abre http://localhost:5000/dashboard")
        print("   para ver el histórico de sensores")
    else:
        print("❌ Falló la generación de datos")
    print()

