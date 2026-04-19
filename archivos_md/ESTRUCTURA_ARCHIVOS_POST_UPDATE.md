# 📁 Estructura de Archivos - Post Actualización

## Cambios en la Estructura

```
irrigacion/
├── app/
│   ├── __init__.py                          (✏️ MODIFICADO)
│   ├── alarms.py
│   ├── alarms_config.py
│   ├── auth.py
│   ├── config.py                            (✏️ MODIFICADO - HARDWARE_MODE)
│   ├── db.py
│   ├── fake_sensors.py
│   ├── gpio.py                              (⚠️ NO USAR - usa hardware_manager)
│   ├── hardware.py                          (✏️ MODIFICADO - Mejorado)
│   ├── hardware_lora.py                     (⚠️ NO USAR directamente)
│   ├── hardware_manager.py                  (🆕 NUEVO - Central)
│   ├── irrigation.py                        (✏️ MODIFICADO)
│   ├── irrigation_1.py
│   ├── lora_controller.py
│   ├── models.py
│   ├── routes.py                            (✏️ MODIFICADO)
│   ├── scheduler.py                         (✏️ MODIFICADO)
│   ├── sensors/
│   │   ├── dht_reader.py
│   │   └── routes.py
│   ├── static/
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   └── templates/
│       └── ... HTML templates
│
├── scripts/
│   ├── dht11.py
│   ├── dht_logger.py
│   ├── diagnose_gpio.py                     (🆕 NUEVO - Test completo)
│   ├── fertilizer_counter.py
│   ├── generate_sensor_data.py
│   ├── health_check.py
│   ├── init_db.py
│   ├── init_db_clean.py
│   ├── migrate_db.py
│   ├── migrate_dht.py
│   ├── migrate_repeat_days.py
│   ├── seed_irrigation_log.py
│   ├── sensor_data_logger.py
│   ├── sensor_simulator.py
│   ├── test_lora.py
│   └── test_zones_quick.py                  (🆕 NUEVO - Test rápido)
│
├── ESP32/
│   └── ... archivos ESP32
│
├── ESP32I/
│   └── ... archivos LoRa
│
├── instance/
│   └── irrigation.db
│
├── wifi/
│   └── ... archivos wifi
│
├── RESUMEN_SOLUCION_GPIO.md                 (🆕 NUEVO)
├── ACTUALIZACION_GPIO_v1.0.md               (🆕 NUEVO)
├── SOLUCION_GPIO_ZONAS.md                   (🆕 NUEVO)
├── CHECKLIST_IMPLEMENTACION_GPIO.md         (🆕 NUEVO)
├── README.md
├── requirements.txt
├── run.py
└── ... otros archivos
```

## Resumen de Cambios por Nivel

### 🎯 Nivel Principal (Raíz)
- ✅ 4 archivos de documentación NUEVOS
- ✏️ Resto de archivos sin cambios

### 📦 Nivel app/
- ✏️ 5 archivos modificados (config.py, hardware.py, __init__.py, routes.py, irrigation.py)
- 🆕 1 archivo NUEVO (hardware_manager.py)
- ⚠️ gpio.py y hardware_lora.py no se usan directamente (ahora se importan a través de hardware_manager.py)

### 🔧 Nivel scripts/
- 🆕 2 archivos NUEVOS (diagnose_gpio.py, test_zones_quick.py)
- Resto sin cambios

### 📄 Documentación Generada
1. `RESUMEN_SOLUCION_GPIO.md` - Resumen ejecutivo
2. `ACTUALIZACION_GPIO_v1.0.md` - Guía de actualización
3. `SOLUCION_GPIO_ZONAS.md` - Documentación técnica
4. `CHECKLIST_IMPLEMENTACION_GPIO.md` - Checklist

---

## Guía de Uso de Archivos

### Para el Usuario Final
- **`RESUMEN_SOLUCION_GPIO.md`** ← Lee esto primero
- **`ACTUALIZACION_GPIO_v1.0.md`** ← Para implementar
- **`scripts/test_zones_quick.py`** ← Para verificar

### Para el Desarrollador
- **`SOLUCION_GPIO_ZONAS.md`** ← Detalles técnicos
- **`app/hardware_manager.py`** ← Punto de entrada
- **`app/hardware.py`** ← Implementación GPIO
- **`scripts/diagnose_gpio.py`** ← Para debugging

### Para Auditoría
- **`CHECKLIST_IMPLEMENTACION_GPIO.md`** ← Verificación completa
- Todos los archivos `.md` generados

---

## Dependencias Entre Archivos

```
hardware_manager.py
├── importa hardware.py (cuando HARDWARE_MODE='GPIO')
├── importa hardware_lora.py (cuando HARDWARE_MODE='LORA')
└── proporciona interfaz a:
    ├── routes.py
    ├── scheduler.py
    ├── irrigation.py
    └── __init__.py

config.py
└── HARDWARE_MODE define qué módulo se carga

hardware.py
└── implementa GPIO directo en Raspberry Pi

hardware_lora.py
└── implementa comunicación LoRa con ESP32
```

---

## Checklist de Archivos

### Archivos que DEBEN estar presentes
- [x] `app/hardware_manager.py` - Central
- [x] `app/hardware.py` - Modificado
- [x] `app/config.py` - Modificado
- [x] `scripts/diagnose_gpio.py` - Test completo
- [x] `scripts/test_zones_quick.py` - Test rápido

### Archivos que NO deben ser modificados
- ✅ `app/gpio.py` - Se ignora (no importar directamente)
- ✅ `app/hardware_lora.py` - Se importa a través de hardware_manager

### Archivos documentación
- [x] `RESUMEN_SOLUCION_GPIO.md`
- [x] `ACTUALIZACION_GPIO_v1.0.md`
- [x] `SOLUCION_GPIO_ZONAS.md`
- [x] `CHECKLIST_IMPLEMENTACION_GPIO.md`

---

## Importaciones Válidas

### ✅ CORRECTO (úsalo)
```python
from app.hardware_manager import zone_on, zone_off, zone_state
from app.hardware_manager import pump_on, pump_off
from app.hardware_manager import ZONE_PINS, PUMP_PIN
```

### ❌ INCORRECTO (NO usar)
```python
from app.hardware import zone_on  # No directo
from app.gpio import relay_on     # No usar
from app.hardware_lora import zone_on  # No directo
```

---

## Modo de Hardware

El modo se define en `app/config.py`:

```python
# Opción 1: GPIO directo (ACTUAL)
HARDWARE_MODE = 'GPIO'

# Opción 2: LoRa con ESP32 (para futuro)
HARDWARE_MODE = 'LORA'

# Opción 3: Simulación (para testing)
HARDWARE_MODE = 'SIMULATION'
```

Para cambiar:
1. Edita `app/config.py`
2. Cambia `HARDWARE_MODE`
3. Reinicia la aplicación

Automáticamente se cargará el módulo correcto.

---

## Totales de Cambios

- **Archivos modificados**: 5
- **Archivos nuevos**: 6
- **Líneas agregadas**: ~500
- **Líneas modificadas**: ~50
- **Documentación generada**: 4 archivos

---

**Actualización**: Marzo 2026  
**Versión**: 1.0  
**Estado**: ✅ Completa

