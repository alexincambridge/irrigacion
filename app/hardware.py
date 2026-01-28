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

