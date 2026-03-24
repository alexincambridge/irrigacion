"""
Lectura DHT22 y guardado en SQLite
Usa use_pulseio=False para compatibilidad con Raspberry Pi
"""

import time
import sqlite3
import board
import adafruit_dht
from datetime import datetime

DB_PATH = "/home/alexdev/Documents/irrigacion/instance/irrigation.db"
DHT_PIN = board.D4  # GPIO 4
INTERVAL = 2  # segundos (DHT22 requiere mínimo 2s)

# use_pulseio=False es NECESARIO en Raspberry Pi para que funcione
dht = adafruit_dht.DHT22(DHT_PIN, use_pulseio=False)

def insert_reading(temp: float, hum: float) -> None:
    """Insertar lectura en base de datos"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO dht_readings (temperature, humidity, created_at)
        VALUES (?, ?, ?)
        """,
        (temp, hum, datetime.now())
    )
    conn.commit()
    conn.close()

def main() -> None:
    print("🌡️ DHT22 Logger iniciado")
    print("=" * 60)
    print(f"Pin: GPIO 4 (board.D4)")
    print(f"Intervalo: {INTERVAL}s")
    print(f"BD: {DB_PATH}")
    print("=" * 60)

    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity

            if temperature is not None and humidity is not None:
                insert_reading(temperature, humidity)
                print(
                    f"[✅ OK] T={temperature:.1f}°C  H={humidity:.1f}%  @ {datetime.now().strftime('%H:%M:%S')}"
                )
            else:
                print("[⚠️  WARN] Lectura None (DHT22 aún calentando)")

        except RuntimeError as e:
            # Errores típicos del DHT22 - son normales
            print(f"[⚠️  WARN] {e.args[0]}")

        except Exception as e:
            print(f"[❌ ERROR] {e}")
            dht.exit()
            raise

        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[⛔ STOP] Detenido por usuario")
        dht.exit()

