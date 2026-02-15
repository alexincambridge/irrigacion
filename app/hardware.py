import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ZONE_PINS = {
    1: 23,
    2: 24,
    3: 25
}

for pin in ZONE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def zone_on(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin:
        GPIO.output(pin, GPIO.HIGH)
        print(f"GPIO {pin} ON")


def zone_off(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin:
        GPIO.output(pin, GPIO.LOW)
        print(f"GPIO {pin} OFF")


def zone_state(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin:
        return GPIO.input(pin) == GPIO.HIGH
    return False


def irrigation_off():
    for pin in ZONE_PINS.values():
        GPIO.output(pin, GPIO.LOW)
