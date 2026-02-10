import time
import board
import adafruit_dht
import sqlite3

DB = "/home/pi/irrigacion/irrigacion.db"
dht = adafruit_dht.DHT11(board.D22)

while True:
    try:
        t = dht.temperature
        h = dht.humidity

        if t is not None and h is not None:
            conn = sqlite3.connect(DB)
            conn.execute("""
                INSERT INTO dht_readings (temperature, humidity)
                VALUES (?, ?)
            """, (t, h))
            conn.commit()
            conn.close()

            print("DHT OK", t, h)

    except RuntimeError:
        pass

    time.sleep(5)
