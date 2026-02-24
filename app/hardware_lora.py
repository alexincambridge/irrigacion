"""
Hardware control abstraction layer
Supports both direct GPIO control and LoRa-based ESP32 control
"""

import logging
from app.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine hardware mode from config
HARDWARE_MODE = getattr(Config, 'HARDWARE_MODE', 'GPIO')  # 'GPIO' or 'LORA'

if HARDWARE_MODE == 'LORA':
    from app.lora_controller import get_lora_controller
    logger.info("Hardware mode: LoRa (ESP32)")
elif HARDWARE_MODE == 'GPIO':
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        logger.info("Hardware mode: Direct GPIO")
    except ImportError:
        logger.warning("RPi.GPIO not available, using simulation mode")
        GPIO = None
        HARDWARE_MODE = 'SIMULATION'
else:
    logger.info("Hardware mode: Simulation")
    HARDWARE_MODE = 'SIMULATION'

# Zone/Valve configuration
ZONE_PINS = {
    1: 23,  # sector 1
    2: 24,  # sector 2
    3: 25,  # sector 3
    4: 27,  # sector 4 (added for 4 zones)
}

_active_zones = set()
_lora_controller = None

# Initialize GPIO pins if using direct GPIO mode
if HARDWARE_MODE == 'GPIO' and GPIO:
    for pin in ZONE_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

# Initialize LoRa controller if using LoRa mode
if HARDWARE_MODE == 'LORA':
    _lora_controller = get_lora_controller()


def zone_on(zone_id, duration=0):
    """
    Turn on a zone/valve

    Args:
        zone_id: Zone number (1-4)
        duration: Auto-off duration in seconds (0 = manual mode)
    """
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            success = _lora_controller.valve_on(zone_id, duration)
            if success:
                _active_zones.add(zone_id)
                logger.info(f"[LoRa] Zone {zone_id} ON" +
                          (f" (auto-off in {duration}s)" if duration > 0 else ""))
            else:
                logger.error(f"[LoRa] Failed to turn on zone {zone_id}")
            return success
        return False

    elif HARDWARE_MODE == 'GPIO':
        pin = ZONE_PINS.get(zone_id)
        if pin is None:
            logger.error(f"Invalid zone: {zone_id}")
            return False

        if GPIO:
            GPIO.output(pin, GPIO.HIGH)
        _active_zones.add(zone_id)
        logger.info(f"[GPIO] Zone {zone_id} ON (GPIO {pin})")
        return True

    else:  # SIMULATION
        _active_zones.add(zone_id)
        logger.info(f"[SIMULATION] Zone {zone_id} ON" +
                   (f" (auto-off in {duration}s)" if duration > 0 else ""))
        return True


def zone_off(zone_id):
    """
    Turn off a zone/valve

    Args:
        zone_id: Zone number (1-4)
    """
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            success = _lora_controller.valve_off(zone_id)
            if success:
                _active_zones.discard(zone_id)
                logger.info(f"[LoRa] Zone {zone_id} OFF")
            else:
                logger.error(f"[LoRa] Failed to turn off zone {zone_id}")
            return success
        return False

    elif HARDWARE_MODE == 'GPIO':
        pin = ZONE_PINS.get(zone_id)
        if pin is None:
            return False

        if GPIO:
            GPIO.output(pin, GPIO.LOW)
        _active_zones.discard(zone_id)
        logger.info(f"[GPIO] Zone {zone_id} OFF (GPIO {pin})")
        return True

    else:  # SIMULATION
        _active_zones.discard(zone_id)
        logger.info(f"[SIMULATION] Zone {zone_id} OFF")
        return True


def zone_state(zone_id):
    """
    Get current state of a zone

    Args:
        zone_id: Zone number (1-4)

    Returns:
        True if zone is on, False if off
    """
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            status = _lora_controller.get_status()
            if status:
                return status.get(zone_id, False)
        return zone_id in _active_zones

    else:
        return zone_id in _active_zones


def all_off():
    """Turn off all zones/valves"""
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            success = _lora_controller.all_valves_off()
            if success:
                _active_zones.clear()
                logger.info("[LoRa] All zones OFF")
            return success
        return False

    elif HARDWARE_MODE == 'GPIO':
        for zone in list(_active_zones):
            zone_off(zone)
        logger.info("[GPIO] All zones OFF")
        return True

    else:  # SIMULATION
        _active_zones.clear()
        logger.info("[SIMULATION] All zones OFF")
        return True


def get_all_zones_status():
    """
    Get status of all zones

    Returns:
        Dictionary with zone states {1: True, 2: False, ...}
    """
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            status = _lora_controller.get_status()
            if status:
                return status

    # Fallback to local tracking
    return {zone_id: zone_id in _active_zones for zone_id in ZONE_PINS.keys()}


def get_hardware_info():
    """
    Get hardware configuration and status

    Returns:
        Dictionary with hardware information
    """
    info = {
        'mode': HARDWARE_MODE,
        'zones': len(ZONE_PINS),
        'active_zones': list(_active_zones)
    }

    if HARDWARE_MODE == 'LORA' and _lora_controller:
        info['lora_connected'] = _lora_controller.connected
        quality = _lora_controller.get_signal_quality()
        if quality:
            info['signal_quality'] = quality

    return info


def check_connection():
    """
    Check if hardware is connected and responding

    Returns:
        True if hardware is responding, False otherwise
    """
    if HARDWARE_MODE == 'LORA':
        if _lora_controller:
            return _lora_controller.ping()
        return False

    elif HARDWARE_MODE == 'GPIO':
        return GPIO is not None

    else:  # SIMULATION
        return True


def cleanup():
    """Cleanup hardware resources"""
    if HARDWARE_MODE == 'LORA' and _lora_controller:
        _lora_controller.cleanup()
    elif HARDWARE_MODE == 'GPIO' and GPIO:
        GPIO.cleanup()

    logger.info("Hardware cleaned up")

