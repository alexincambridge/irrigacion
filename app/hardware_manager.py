"""
Hardware Manager - Centralizado
Maneja todos los modos de hardware de forma segura
"""

import logging
from app.config import Config

logger = logging.getLogger(__name__)

HARDWARE_MODE = getattr(Config, 'HARDWARE_MODE', 'GPIO')

# Import the appropriate hardware module based on config
if HARDWARE_MODE == 'GPIO':
    from app.hardware import (
        zone_on, zone_off, zone_state, all_off,
        pump_on, pump_off, pump_state,
        get_hardware_info, check_connection, get_all_zones_status,
        ZONE_PINS, PUMP_PIN
    )
    logger.info("✅ Hardware Manager: Using GPIO mode")

elif HARDWARE_MODE == 'LORA':
    from app.hardware_lora import (
        zone_on, zone_off, zone_state, all_off,
        pump_on, pump_off, pump_state,
        get_hardware_info, check_connection, get_all_zones_status,
        ZONE_PINS, PUMP_PIN
    )
    logger.info("✅ Hardware Manager: Using LoRa mode")

else:  # SIMULATION
    logger.info("✅ Hardware Manager: Using SIMULATION mode")

    ZONE_PINS = {1: 23, 2: 24, 3: 25, 4: 27}
    PUMP_PIN = 17

    _active_zones = set()
    _pump_active = False

    def zone_on(zone_id, duration=0):
        _active_zones.add(zone_id)
        logger.info(f"[SIM] Zone {zone_id} ON")
        return True

    def zone_off(zone_id):
        _active_zones.discard(zone_id)
        logger.info(f"[SIM] Zone {zone_id} OFF")
        return True

    def zone_state(zone_id):
        return zone_id in _active_zones

    def all_off():
        _active_zones.clear()
        pump_off()
        logger.info("[SIM] All zones OFF")

    def pump_on(duration_seconds=0):
        global _pump_active
        _pump_active = True
        logger.info("[SIM] Pump ON")
        return True

    def pump_off():
        global _pump_active
        _pump_active = False
        logger.info("[SIM] Pump OFF")
        return True

    def pump_state():
        return _pump_active

    def get_hardware_info():
        return {
            'mode': 'SIMULATION',
            'zones': 4,
            'active_zones': list(_active_zones),
            'pump_active': _pump_active
        }

    def check_connection():
        return True

    def get_all_zones_status():
        return {i: i in _active_zones for i in range(1, 5)}


# Export all functions
__all__ = [
    'zone_on', 'zone_off', 'zone_state', 'all_off',
    'pump_on', 'pump_off', 'pump_state',
    'get_hardware_info', 'check_connection', 'get_all_zones_status',
    'ZONE_PINS', 'PUMP_PIN', 'HARDWARE_MODE'
]

