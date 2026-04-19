# 🚀 INSTRUCCIONES DE ACTUALIZACIÓN - Problema GPIO Solucionado

## Resumen de Cambios
Se ha identificado y solucionado el problema por el cual solo funcionaba el GPIO 24 (Zona 2). 

**El problema era:** Conflicto entre múltiples módulos de hardware y modo de hardware incorrecto.

**La solución:** Centralización de hardware + corrección de configuración + mejora de inicialización.

## Pasos para Aplicar los Cambios

### 1. Actualiza el archivo de configuración
Asegúrate de que `app/config.py` tenga:
```python
HARDWARE_MODE = 'GPIO'  # ← IMPORTANTE: Debe ser 'GPIO', no 'LORA'
```

### 2. Verifica los nuevos archivos
Los siguientes archivos nuevos deben existir:
- ✅ `app/hardware_manager.py` - Gestor centralizado
- ✅ `scripts/diagnose_gpio.py` - Diagnóstico completo
- ✅ `scripts/test_zones_quick.py` - Test rápido

### 3. Prueba los GPIOs

**Opción A: Test Completo (Recomendado)**
```bash
cd /Users/alexg/Sites/irrigacion
sudo python3 scripts/diagnose_gpio.py
```

**Opción B: Test Rápido**
```bash
sudo python3 scripts/test_zones_quick.py
```

### 4. Reinicia la aplicación
```bash
# Si usas systemd
sudo systemctl restart irrigacion

# O si ejecutas manualmente
python3 run.py
```

## ✅ Verifica que Funciona

### En la Interfaz Web
1. Ve a `/irrigation`
2. Abre "Control Manual de Zonas"
3. Haz clic en "Iniciar" para cada zona
4. Deberías ver que TODOS los LEDs del relé se encienden

### En los Logs
Deberías ver mensajes como:
```
[HW] ✅ Zona 1 ON (GPIO 23)
[HW] ✅ Zona 2 ON (GPIO 24)
[HW] ✅ Zona 3 ON (GPIO 25)
[HW] ✅ Zona 4 ON (GPIO 27)
```

## 📋 Listado de Cambios Realizados

### Archivos Modificados:
```
app/config.py
  - Cambió: HARDWARE_MODE = 'LORA' → HARDWARE_MODE = 'GPIO'

app/hardware.py
  - Añadida función _init_gpio() para inicialización segura
  - Mejorado manejo de excepciones en zone_on/zone_off/pump_on/pump_off
  - Añadido flag _gpio_initialized para evitar reinicializaciones

app/__init__.py
  - Cambió: from app.hardware import → from app.hardware_manager import

app/routes.py
  - Cambió: 7 importaciones de app.hardware → app.hardware_manager

app/scheduler.py
  - Cambió: from app.hardware import → from app.hardware_manager import

app/irrigation.py
  - Cambió: from app.hardware import → from app.hardware_manager import
```

### Archivos Nuevos:
```
app/hardware_manager.py
  - Gestor centralizado que importa el módulo correcto basado en HARDWARE_MODE
  - Soporta modos: 'GPIO', 'LORA', 'SIMULATION'

scripts/diagnose_gpio.py
  - Script de diagnóstico completo para cada GPIO
  - Prueba cada pin individualmente

scripts/test_zones_quick.py
  - Test rápido sin necesidad de Flask
  - Ideal para verificación rápida
```

## 🔍 Si Algo Sigue Fallando

### Paso 1: Verifica la configuración
```bash
grep HARDWARE_MODE app/config.py
# Debe mostrar: HARDWARE_MODE = 'GPIO'
```

### Paso 2: Ejecuta el diagnóstico
```bash
sudo python3 scripts/diagnose_gpio.py
# Verifica que TODOS los GPIOs muestren OK
```

### Paso 3: Revisa los logs
```bash
# Si usas systemd
journalctl -u irrigacion -f

# O si ejecutas manualmente
python3 run.py 2>&1 | grep -i "HW\|GPIO"
```

### Paso 4: Verifica conexiones físicas
- Asegúrate de que los relés estén conectados a los GPIOs correctos
- Verifica que haya voltaje en los pines cuando se activan
- Usa un multímetro para medir voltaje en los pines

## 📚 Referencias Rápidas

### Mapeo GPIO ↔ Zonas
| Zona | GPIO | Función |
|------|------|---------|
| 1 | 23 | Jardín |
| 2 | 24 | Huerta |
| 3 | 25 | Césped |
| 4 | 27 | Árboles |
| Bomba | 17 | Fertilización |

### Modos de Hardware Disponibles
```python
# En app/config.py
HARDWARE_MODE = 'GPIO'        # Control directo GPIO (Raspberry Pi)
HARDWARE_MODE = 'LORA'        # Control vía ESP32 con LoRa
HARDWARE_MODE = 'SIMULATION'  # Modo simulación (testing)
```

## 💡 Próximas Mejoras Posibles

1. **Monitoreo de GPIOs**: Agregarse página de estado de hardware
2. **Logging mejorado**: Registrar cada cambio de estado
3. **Alertas**: Notificar si un GPIO falla
4. **Redundancia**: Soporte para múltiples Raspberry Pi

## 📞 Soporte

Si encuentras problemas:
1. Ejecuta el script de diagnóstico
2. Revisa los logs de la aplicación
3. Verifica las conexiones físicas
4. Reinicia la aplicación

---

**Fecha de actualización**: Marzo 2026  
**Versión**: 1.0

