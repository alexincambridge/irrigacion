import RPi.GPIO as GPIO
import threading
import logging

logger = logging.getLogger(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

_initialized = set()
_pump_timer = None

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

def read_pin(pin):
    """Read the current state of an output pin"""
    setup_pin(pin)
    return GPIO.input(pin)

# --- Peristaltic Pump Control ---
def pump_on(pin, duration_seconds=0):
    """Turn on peristaltic pump with optional auto-off timer"""
    global _pump_timer

    # Cancel any existing timer
    if _pump_timer:
        _pump_timer.cancel()
        _pump_timer = None

    setup_pin(pin)
    GPIO.output(pin, GPIO.HIGH)
    logger.info(f"[PUMP] ON (GPIO {pin})")

    # Safety auto-off
    if duration_seconds > 0:
        max_duration = 3600  # Hard limit 60 min
        duration_seconds = min(duration_seconds, max_duration)
        _pump_timer = threading.Timer(duration_seconds, pump_off, args=[pin])
        _pump_timer.daemon = True
        _pump_timer.start()
        logger.info(f"[PUMP] Auto-off in {duration_seconds}s")

def pump_off(pin):
    """Turn off peristaltic pump"""
    global _pump_timer

    if _pump_timer:
        _pump_timer.cancel()
        _pump_timer = None

    setup_pin(pin)
    GPIO.output(pin, GPIO.LOW)
    logger.info(f"[PUMP] OFF (GPIO {pin})")

def pump_state(pin):
    """Check if pump is running"""
    setup_pin(pin)
    return GPIO.input(pin) == GPIO.HIGH

def cleanup():
    GPIO.cleanup()
