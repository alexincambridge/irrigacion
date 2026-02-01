import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

_initialized = set()

def setup_pin(pin):
    if pin not in _initialized:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # 🔒 FAIL-SAFE: apagado
        _initialized.add(pin)

def relay_on(pin):
    setup_pin(pin)
    GPIO.output(pin, GPIO.HIGH)

def relay_off(pin):
    setup_pin(pin)
    GPIO.output(pin, GPIO.LOW)

def cleanup():
    GPIO.cleanup()
