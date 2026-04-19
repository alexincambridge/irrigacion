# 🔧 INSTRUCCIONES PASO A PASO - Corregir el Error ImportError

## Problema
```
ImportError: cannot import name 'Config' from 'app.config'
```

## Solución Rápida (2 minutos)

### Paso 1: Conectate a tu RPi
```bash
ssh tu-usuario@tu-ip-rpi
cd /home/alexdev/Documents/irrigacion
```

### Paso 2: Edita el archivo
```bash
nano app/hardware_manager.py
```

### Paso 3: Encuentra estas líneas (arriba del archivo)
```python
from app.config import Config

logger = logging.getLogger(__name__)

HARDWARE_MODE = getattr(Config, 'HARDWARE_MODE', 'GPIO')
```

### Paso 4: Reemplázalas por esto
```python
logger = logging.getLogger(__name__)

# Importar HARDWARE_MODE desde config
try:
    from app import config
    HARDWARE_MODE = getattr(config, 'HARDWARE_MODE', 'GPIO')
except (ImportError, AttributeError):
    HARDWARE_MODE = 'GPIO'  # Fallback a GPIO
```

### Paso 5: Guarda
```
Ctrl+O (Enter para confirmar)
Ctrl+X
```

### Paso 6: Verifica
```bash
python3 -m py_compile app/hardware_manager.py
echo "Sintaxis OK"
```

### Paso 7: Reinicia la app
```bash
sudo systemctl restart irrigacion
```

### Paso 8: Verifica que funciona
```bash
sudo python3 scripts/test_zones_quick.py
```

✅ Si ves "TODAS LAS ZONAS FUNCIONAN CORRECTAMENTE", ¡está hecho!

---

## Solución Completa del Archivo

Si prefieres reemplazar todo el archivo, usa esto:

**Archivo completo correcto:**
```python
"""
Hardware Manager - Centralizado
Maneja todos los modos de hardware de forma segura
"""

import logging

logger = logging.getLogger(__name__)

# Importar HARDWARE_MODE desde config
try:
    from app import config
    HARDWARE_MODE = getattr(config, 'HARDWARE_MODE', 'GPIO')
except (ImportError, AttributeError):
    HARDWARE_MODE = 'GPIO'  # Fallback a GPIO

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
```

---

## Troubleshooting

### Si aún da error
```bash
# Ve el error completo
python3 -c "import app.hardware_manager"

# O revisa los logs
journalctl -u irrigacion -f
```

### Si necesitas revertir
```bash
# Hay un backup automático si usas git
git diff app/hardware_manager.py

# Para volver a la versión anterior
git checkout app/hardware_manager.py
```

### Si la app no inicia
```bash
# Prueba iniciar manualmente para ver el error
python3 run.py 2>&1 | head -30
```

---

## Verificación Final

Después de hacer todos los cambios:

```bash
# 1. Test de sintaxis
python3 -m py_compile app/hardware_manager.py

# 2. Test rápido
sudo python3 scripts/test_zones_quick.py

# 3. En interfaz web
# Abre: http://tu-ip-rpi:5000/irrigation
# Prueba los botones
```

✅ Si todo funciona, el error está resuelto.

---

**Tiempo estimado**: 5 minutos
**Dificultad**: Baja
**Riesgo**: Muy bajo (fácil de revertir)

