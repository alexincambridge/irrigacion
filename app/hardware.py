import RPi.GPIO as GPIO

# GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Zonas → GPIO reales
ZONE_PINS = {
    7: 23,   # Jardín
    8: 24,   # Huerto
    9: 25,   # Goteo
}

# Inicializar pines
for pin in ZONE_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Estado en memoria (simple, como querías)
_active_zones = set()

def zone_on(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        return
    GPIO.output(pin, GPIO.HIGH)
    _active_zones.add(zone_id)

def zone_off(zone_id):
    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        return
    GPIO.output(pin, GPIO.LOW)
    _active_zones.discard(zone_id)

def zone_state(zone_id):
    return zone_id in _active_zones

# Riego global (si lo usas)
_irrigation_state = False

def irrigation_on():
    global _irrigation_state
    _irrigation_state = True

def irrigation_off():
    global _irrigation_state
    _irrigation_state = False
    for pin in ZONE_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    _active_zones.clear()

def irrigation_status():
    return _irrigation_state
