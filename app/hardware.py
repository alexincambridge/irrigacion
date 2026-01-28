# Estado global simple (luego irá a BD)
_irrigation_state = False

def irrigation_on():
    global _irrigation_state
    _irrigation_state = True

def irrigation_off():
    global _irrigation_state
    _irrigation_state = False
    # aquí GPIO.output(RELAY_PIN, GPIO.LOW)

def irrigation_status():
    return _irrigation_state

_active_zones = set()

def zone_on(zone_id):
    _active_zones.add(zone_id)
    # GPIO.output(pin, GPIO.HIGH)

def zone_off(zone_id):
    _active_zones.discard(zone_id)
    # GPIO.output(pin, GPIO.LOW)

def zone_state(zone_id):
    return zone_id in _active_zones


