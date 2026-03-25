"""
Lectura DHT22 y guardado en SQLite
Usa use_pulseio=False para compatibilidad con Raspberry Pi
"""
import time
import sqlite3
import board
import adafruit_dht
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "instance" / "irrigation.db"

# use_pulseio=False es NECESARIO en Raspberry Pi para que funcione
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

def save_reading(temp: float, hum: float) -> None:
    """Guardar lectura en base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO dht_readings (temperature, humidity)
        VALUES (?, ?)
    """, (temp, hum))
    conn.commit()
    conn.close()

def main() -> None:
    """Loop principal de lectura del DHT22"""
    print("🌡️ DHT22 Reader iniciado en GPIO 4")
    print("=" * 50)

    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity

            if temperature is not None and humidity is not None:
                save_reading(temperature, humidity)
                print(f"✅ {temperature:.1f}°C | {humidity:.1f}% | Guardado en BD")

        except RuntimeError as exc:
            # Errores típicos del DHT22 - se ignoran
            print(f"⚠️  RuntimeError: {exc.args[0]}")

        except Exception as exc:
            print(f"❌ Error inesperado: {exc}")
            dht.exit()
            raise

        time.sleep(2.0)  # DHT22 requiere mínimo 2 segundos entre lecturas

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Detenido por usuario")
        dht.exit()

