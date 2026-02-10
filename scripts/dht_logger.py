"""
Lectura DHT11 y guardado en SQLite
"""

import time
import sqlite3
import board
import adafruit_dht
from datetime import datetime

DB_PATH = "/home/alexdev/Documents/irrigacion/irrigacion.db"
DHT_PIN = board.D22
INTERVAL = 5  # segundos

dht = adafruit_dht.DHT11(DHT_PIN)

def insert_reading(temp: float, hum: float) -> None:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dht_readings (temperature, humidity, timestamp)
        VALUES (?, ?, ?)
        """,
        (temp, hum, datetime.now())
    )
    conn.commit()
    conn.close()

def main() -> None:
    print("🌡️ DHT logger iniciado")
    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity

            if temperature is not None and humidity is not None:
                insert_reading(temperature, humidity)
                print(
                    f"[OK] Temp={temperature:.1f}°C  Hum={humidity:.1f}%"
                )

        except RuntimeError as e:
            # Errores típicos del DHT (normales)
            print("[WARN]", e)

        except Exception as e:
            print("[ERROR]", e)

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
