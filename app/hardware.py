import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ZONE_PINS = {
    1: 23,
    2: 24,
    3: 25,
}

_active_zones = set()

# Inicializar pines en LOW
for pin in ZONE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


def zone_on(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        print(f"[HW] Zona inválida: {zone_id}")
        return

    GPIO.output(pin, GPIO.HIGH)
    _active_zones.add(zone_id)
    print(f"[HW] Zona {zone_id} ON (GPIO {pin})")


def zone_off(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        return

    GPIO.output(pin, GPIO.LOW)
    _active_zones.discard(zone_id)
    print(f"[HW] Zona {zone_id} OFF (GPIO {pin})")


def zone_state(zone_id):
    return zone_id in _active_zones


def all_off():
    for zone in list(_active_zones):
        zone_off(zone)

