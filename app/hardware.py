import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
from app.config import RELAY_PIN, DHT_PIN

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

dht = adafruit_dht.DHT11(board.D22)

def read_dht():
    try:
        return dht.temperature, dht.humidity
    except Exception:
        return None, None

def water(seconds):
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(seconds)
    GPIO.output(RELAY_PIN, GPIO.HIGH)
