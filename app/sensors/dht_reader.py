"""
Lectura DHT22 y guardado en SQLite
"""
import time
import sqlite3
import board
import adafruit_dht
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "instance" / "irrigation.db"

dht = adafruit_dht.DHT22(board.D4)  # GPIO 4

def save_reading(temp: float, hum: float) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO dht_readings (temperature, humidity)
        VALUES (?, ?)
    """, (temp, hum))
    conn.commit()
    conn.close()

def main() -> None:
    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity

            if temperature is not None and humidity is not None:
                save_reading(temperature, humidity)
                print(f"OK → {temperature} °C | {humidity} %")

        except RuntimeError as exc:
            print(f"Lectura fallida: {exc}")

        time.sleep(3)  # cada 3s (DHT22 soporta mínimo 2s)

if __name__ == "__main__":
    main()
