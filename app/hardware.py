import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

ZONE_PINS = {
    1: 23,
    2: 24,
    3: 25
}

for pin in ZONE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def zone_on(zone_id):
    GPIO.output(ZONE_PINS[zone_id], GPIO.HIGH)

def zone_off(zone_id):
    GPIO.output(ZONE_PINS[zone_id], GPIO.LOW)

def zone_state(zone_id):
    return GPIO.input(ZONE_PINS[zone_id]) == GPIO.HIGH
