import time
from datetime import datetime
from app.hardware import read_dht, water
from app.models import get_db
from app.config import TEMP_MAX, HUM_MIN, WATER_TIME

AUTO_MODE = True

def scheduler_loop():
    while True:
        if AUTO_MODE:
            hour = datetime.now().hour
            if 5 <= hour <= 7:
                temp, hum = read_dht()
                if temp and hum and (temp >= TEMP_MAX or hum <= HUM_MIN):
                    water(WATER_TIME)
                    db = get_db()
                    db.execute("INSERT INTO irrigation_log(mode) VALUES('AUTO')")
                    db.commit()
        time.sleep(60)
