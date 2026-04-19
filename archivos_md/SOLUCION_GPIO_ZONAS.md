# 🔧 SOLUCIÓN: Problema de GPIOs en Sistema de Riego

## 📋 Problema Identificado

Solo el GPIO 24 (Zona 2 - Huerta) estaba funcionando, mientras que los otros GPIOs (23, 25, 27) no respondían.

### Causas Raíz
1. **Conflicto de módulos**: Había múltiples módulos de hardware (`hardware.py`, `gpio.py`, `hardware_lora.py`) intentando inicializar GPIO simultáneamente
2. **Inicialización múltiple**: `GPIO.setmode()` se llamaba desde diferentes lugares, lo que puede causar conflictos
3. **Modo de hardware incorrecto**: La configuración estaba en modo `LORA` cuando debería estar en `GPIO`
4. **Falta de manejo de errores**: Los pines no se validaban correctamente antes de usar

## ✅ Solución Implementada

### 1. **Centralización de Hardware (hardware_manager.py)**
Se creó un nuevo módulo `hardware_manager.py` que:
- Importa automáticamente el módulo correcto según `HARDWARE_MODE` en `config.py`
- Evita importaciones múltiples de GPIO
- Proporciona un punto único de entrada para todas las operaciones de hardware

### 2. **Mejora de hardware.py**
- Añadida inicialización segura con función `_init_gpio()`
- Validación de si el GPIO ya está configurado antes de setup
- Manejo robusto de excepciones en cada operación
- Flag `_gpio_initialized` para evitar reinicializaciones

### 3. **Cambio de Configuración**
En `app/config.py`:
```python
HARDWARE_MODE = 'GPIO'  # Cambiado de 'LORA' a 'GPIO'
```

### 4. **Actualización de Importaciones**
Se cambiaron todas las importaciones en:
- `app/routes.py` - 7 cambios
- `app/__init__.py` - 1 cambio
- `app/scheduler.py` - 1 cambio
- `app/irrigation.py` - 1 cambio

Todas ahora usan `from app.hardware_manager import ...`

## 🧪 Cómo Verificar que Funciona

### Opción 1: Script de Diagnóstico
Se creó `/scripts/diagnose_gpio.py` que prueba cada GPIO individualmente:

```bash
cd /Users/alexg/Sites/irrigacion
python3 scripts/diagnose_gpio.py
```

**Salida esperada:**
```
============================================================
🌱 DIAGNÓSTICO DE GPIO PARA SISTEMA DE RIEGO
============================================================

🔧 Configurando GPIO...
  ✅ GPIO 23 inicializado correctamente
  ✅ GPIO 24 inicializado correctamente
  ✅ GPIO 25 inicializado correctamente
  ✅ GPIO 27 inicializado correctamente
  ✅ GPIO 17 inicializado correctamente

============================================================
🧪 PRUEBAS DE FUNCIONAMIENTO
============================================================

🔍 Probando Zona 1 (GPIO 23)...
  → Activando GPIO 23... ✅ GPIO 23 está en HIGH
  → Desactivando GPIO 23... ✅ GPIO 23 está en LOW

🔍 Probando Zona 2 (GPIO 24)...
  → Activando GPIO 24... ✅ GPIO 24 está en HIGH
  → Desactivando GPIO 24... ✅ GPIO 24 está en LOW

🔍 Probando Zona 3 (GPIO 25)...
  → Activando GPIO 25... ✅ GPIO 25 está en HIGH
  → Desactivando GPIO 25... ✅ GPIO 25 está en LOW

🔍 Probando Zona 4 (GPIO 27)...
  → Activando GPIO 27... ✅ GPIO 27 está en HIGH
  → Desactivando GPIO 27... ✅ GPIO 27 está en LOW

🔍 Probando Bomba Peristáltica (GPIO 17)...
  → Activando GPIO 17... ✅ GPIO 17 está en HIGH
  → Desactivando GPIO 17... ✅ GPIO 17 está en LOW

============================================================
📊 RESUMEN
============================================================
✅ Zona 1 (GPIO 23): OK
✅ Zona 2 (GPIO 24): OK
✅ Zona 3 (GPIO 25): OK
✅ Zona 4 (GPIO 27): OK
✅ Bomba (GPIO 17): OK

✅ TODOS LOS GPIO FUNCIONAN CORRECTAMENTE
```

### Opción 2: Desde la Interfaz Web
1. Ir a la página de Riego (`/irrigation`)
2. Ir a "Control Manual de Zonas"
3. Hacer clic en "Iniciar" para cada zona
4. Deberías ver que el LED del relé se enciende para TODAS las zonas

### Opción 3: En Logs de la Aplicación
Revisa los logs y deberías ver mensajes como:
```
[HW] ✅ Zona 1 ON (GPIO 23)
[HW] ✅ Zona 2 ON (GPIO 24)
[HW] ✅ Zona 3 ON (GPIO 25)
[HW] ✅ Zona 4 ON (GPIO 27)
```

## 📊 Mapeo de Zonas a GPIOs

| Zona | Nombre | GPIO | Función |
|------|--------|------|---------|
| 1 | Jardín Principal | 23 | Riego zona 1 |
| 2 | Huerta | 24 | Riego zona 2 |
| 3 | Césped | 25 | Riego zona 3 |
| 4 | Árboles | 27 | Riego zona 4 |
| - | Bomba Peristáltica | 17 | Fertilización |

## 🔍 Troubleshooting

### Si siguen sin funcionar algunos GPIOs:

**1. Verifica que los relés estén conectados correctamente:**
```bash
# Ver voltaje en los pines
gpio readall  # Si tienes gpio-admin instalado
```

**2. Revisa los logs de la aplicación:**
```bash
# Si usas systemd
journalctl -u irrigacion -f

# O si ejecutas directamente
python3 run.py 2>&1 | grep -i "HW\|gpio"
```

**3. Prueba reiniciar la aplicación:**
```bash
# Esto ejecutará all_off() automáticamente en el __init__
```

**4. Si un pin específico falla, verifica:**
- Que el pin no esté siendo usado por otro proceso
- Que el relé esté conectado correctamente
- Que haya suficiente corriente disponible

## 📝 Archivos Modificados

```
✅ app/config.py              - Cambio HARDWARE_MODE a 'GPIO'
✅ app/hardware.py            - Mejoras de inicialización segura
✅ app/hardware_manager.py    - NUEVO: gestor centralizado de hardware
✅ app/__init__.py            - Importación desde hardware_manager
✅ app/routes.py              - 7 cambios de importación
✅ app/scheduler.py           - Importación desde hardware_manager
✅ app/irrigation.py          - Importación desde hardware_manager
✅ scripts/diagnose_gpio.py   - NUEVO: script de diagnóstico
```

## 🚀 Próximos Pasos Recomendados

1. **Ejecutar el diagnóstico** para confirmar que todo funciona
2. **Revisar los logs** mientras haces pruebas manuales
3. **Probar los riegos programados** para asegurar que también funcionan
4. **Verificar la bomba peristáltica** de fertilización

## ⚠️ Notas Importantes

- Si quieres usar LoRa con ESP32 en el futuro, simplemente cambia `HARDWARE_MODE = 'LORA'` en `config.py`
- El sistema ahora es modular y soporta fácilmente cambios de hardware
- Todos los cambios son retrocompatibles con el resto del sistema

