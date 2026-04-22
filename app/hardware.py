import RPi.GPIO as GPIO
import threading
import logging

logger = logging.getLogger(__name__)

ZONE_PINS = {
    1: 16,  # sector 1 - Jardn
    2: 23,  # sector 2 - Huerta
    3: 25,  # sector 3 - Csped
    4: 27,  # sector 4 - rboles
}

PUMP_PIN = 17  # Changed to 17

# ACTIVE LOW CONFIGURATION
# Set to True if your relays turn ON with LOW and OFF with HIGH (typical for 4-channel relay modules)
ACTIVE_LOW = True
RELAY_ON = GPIO.LOW if ACTIVE_LOW else GPIO.HIGH
RELAY_OFF = GPIO.HIGH if ACTIVE_LOW else GPIO.LOW

_active_zones = set()
_pump_active = False
_pump_timer = None
_gpio_initialized = False


def _init_gpio():
    """Initialize GPIO once, safely"""
    global _gpio_initialized

    if _gpio_initialized:
        return

    try:
        try:
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)
        except RuntimeError:
            pass

        GPIO.setwarnings(False)

        # Initialize all zone pins as OUTPUT, set to RELAY_OFF
        for zone_id, pin in ZONE_PINS.items():
            try:
                GPIO.setup(pin, GPIO.OUT, initial=RELAY_OFF)
                _active_zones.discard(zone_id)
                logger.info(f"[HW] ✅ GPIO {pin} inicializado a OFF (Zona {zone_id})")
            except Exception as e:
                logger.error(f"[HW] ❌ Error inicializando GPIO {pin}: {e}")

        # Initialize pump pin
        try:
            GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.LOW)
            _pump_active = False
            logger.info(f"[HW] ✅ Pump GPIO {PUMP_PIN} inicializado a OFF")
        except Exception as e:
            logger.error(f"[HW] ❌ Error inicializando pump GPIO {PUMP_PIN}: {e}")

        _gpio_initialized = True
        logger.info("[HW] ✅ GPIO inicializado correctamente")

    except Exception as e:
        logger.error(f"[HW] Error crítico inicializando GPIO: {e}")
        _gpio_initialized = False


# Initialize GPIO on module load
_init_gpio()


def zone_on(zone_id, duration=0):
    """Turn on a zone/valve"""
    _init_gpio()

    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        logger.warning(f"[HW] Zona inválida: {zone_id}")
        return False

    try:
        GPIO.output(pin, RELAY_ON)
        _active_zones.add(zone_id)
        logger.info(f"[HW] ✅ Zona {zone_id} ON (GPIO {pin})")
        return True
    except Exception as e:
        logger.error(f"[HW] ❌ Error activando zona {zone_id}: {e}")
        return False


def zone_off(zone_id):
    """Turn off a zone/valve"""
    _init_gpio()

    pin = ZONE_PINS.get(zone_id)
    if pin is None:
        return False

    try:
        GPIO.output(pin, RELAY_OFF)
        _active_zones.discard(zone_id)
        logger.info(f"[HW] ✅ Zona {zone_id} OFF (GPIO {pin})")
        return True
    except Exception as e:
        logger.error(f"[HW] ❌ Error desactivando zona {zone_id}: {e}")
        return False


def zone_state(zone_id):
    """Check if zone is active from internal state"""
    return zone_id in _active_zones


def all_off():
    """Turn off ALL zones"""
    for zone_id in ZONE_PINS:
        zone_off(zone_id)
    pump_off()


# --- Peristaltic Pump ---
def pump_on(duration_seconds=0):
    """Turn on peristaltic pump with optional auto-off"""
    global _pump_active, _pump_timer

    _init_gpio()

    if _pump_timer:
        _pump_timer.cancel()
        _pump_timer = None

    try:
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        _pump_active = True
        logger.info(f"[HW] ✅ Bomba peristáltica ON (GPIO {PUMP_PIN})")

        if duration_seconds > 0:
            max_dur = 3600
            duration_seconds = min(duration_seconds, max_dur)
            _pump_timer = threading.Timer(duration_seconds, pump_off)
            _pump_timer.daemon = True
            _pump_timer.start()
            logger.info(f"[HW] Bomba auto-off en {duration_seconds}s")

        return True
    except Exception as e:
        logger.error(f"[HW] ❌ Error activando bomba: {e}")
        return False


def pump_off():
    """Turn off peristaltic pump"""
    global _pump_active, _pump_timer

    _init_gpio()

    if _pump_timer:
        _pump_timer.cancel()
        _pump_timer = None

    try:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        _pump_active = False
        logger.info(f"[HW] ✅ Bomba peristáltica OFF")
        return True
    except Exception as e:
        logger.error(f"[HW] ❌ Error desactivando bomba: {e}")
        return False


def pump_state():
    """Check if pump is running"""
    return _pump_active


def get_hardware_info():
    """Get hardware configuration and status"""
    active = [z for z in ZONE_PINS if zone_state(z)]
    return {
        'mode': 'GPIO',
        'zones': len(ZONE_PINS),
        'active_zones': active,
        'pump_active': _pump_active
    }


def check_connection():
    """Check if GPIO hardware is available"""
    return GPIO is not None


def get_all_zones_status():
    """Get status of all zones — reads actual GPIO"""
    return {zone_id: zone_state(zone_id) for zone_id in ZONE_PINS}
