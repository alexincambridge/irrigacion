import time
from app.hardware import read_dht
from app.models import get_db

def sensor_loop():
    while True:
        t, h = read_dht()

        if t is not None and h is not None:
            db = get_db()
            db.execute(
                "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)",
                (t, h)
            )
            db.commit()

        time.sleep(60)
