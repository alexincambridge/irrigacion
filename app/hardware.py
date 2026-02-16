import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

ZONE_PINS = {
    1: 23,
    2: 24,
    3: 25
}

_active_zones = set()

for pin in ZONE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def zone_on(sector):
    pin = ZONE_PINS.get(sector)
    if pin:
        GPIO.output(pin, GPIO.HIGH)
        _active_zones.add(sector)


def zone_off(sector):
    pin = ZONE_PINS.get(sector)
    if pin:
        GPIO.output(pin, GPIO.LOW)
        _active_zones.discard(sector)


def zone_state(sector):
    return sector in _active_zones
