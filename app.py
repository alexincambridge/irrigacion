# irrigacion/app.py
from flask import Flask, render_template, jsonify, request
import RPi.GPIO as GPIO
import adafruit_dht
import board
import time
import threading

RELAY_PIN = 23
DHT_PIN = board.D22

TEMP_MAX = 30
HUM_MIN = 40
WATER_TIME = 5
COOLDOWN = 120

AUTO_MODE = False
last_water = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)

dht = adafruit_dht.DHT11(DHT_PIN)
app = Flask(__name__)

def read_dht():
    try:
        return dht.temperature, dht.humidity
    except Exception:
        return None, None

def water():
    global last_water
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(WATER_TIME)
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    last_water = time.time()

def auto_irrigation():
    global last_water
    while True:
        if AUTO_MODE:
            temp, hum = read_dht()
            now = time.time()

            if temp and hum:
                if (temp >= TEMP_MAX or hum <= HUM_MIN) and (now - last_water > COOLDOWN):
                    water()

        time.sleep(10)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    t, h = read_dht()
    return jsonify({
        "temperature": t,
        "humidity": h,
        "auto": AUTO_MODE
    })

@app.route("/water", methods=["POST"])
def manual_water():
    water()
    return jsonify({"status": "Riego manual activado"})

@app.route("/auto", methods=["POST"])
def auto_toggle():
    global AUTO_MODE
    AUTO_MODE = request.json.get("state", False)
    return jsonify({"auto": AUTO_MODE})

if __name__ == "__main__":
    threading.Thread(target=auto_irrigation, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
