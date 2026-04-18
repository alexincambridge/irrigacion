# 🔧 COMANDOS RÁPIDOS - Referencia Rápida

## 🚀 Uso Inmediato

### Test Rápido (1 minuto)
```bash
cd /Users/alexg/Sites/irrigacion && sudo python3 scripts/test_zones_quick.py
```
✅ Resultado esperado: "TODAS LAS ZONAS FUNCIONAN CORRECTAMENTE"

### Test Completo (5 minutos)
```bash
cd /Users/alexg/Sites/irrigacion && sudo python3 scripts/diagnose_gpio.py
```
✅ Resultado esperado: Todos los GPIOs muestran OK

### Ver Logs en Vivo
```bash
journalctl -u irrigacion -f
```
🔍 Busca: [HW] para ver activaciones de GPIO

### Reiniciar Aplicación
```bash
sudo systemctl restart irrigacion
```
⏱️ Tarda ~5 segundos

### Validar Sintaxis Python
```bash
python3 -m py_compile app/hardware_manager.py
```
✅ Sin salida = Sin errores

---

## 📊 Archivos Clave

### Para Verificar Rápido
```bash
less GUIA_RAPIDA_5_MIN.md
```

### Para Implementar
```bash
less ACTUALIZACION_GPIO_v1.0.md
```

### Para Troubleshooting
```bash
less SOLUCION_GPIO_ZONAS.md | grep -i "troubleshooting" -A 50
```

### Para QA
```bash
less CHECKLIST_IMPLEMENTACION_GPIO.md
```

---

## 🧪 Secuencia de Pruebas

### 1. Validación (1 min)
```bash
python3 -m py_compile app/hardware_manager.py app/hardware.py
echo "✅ Sintaxis OK"
```

### 2. Test Rápido (1 min)
```bash
sudo python3 scripts/test_zones_quick.py
```

### 3. Test Completo (5 min)
```bash
sudo python3 scripts/diagnose_gpio.py
```

### 4. Web (5 min)
```bash
# Abre navegador
# http://localhost:5000/irrigation
# Prueba cada zona manualmente
```

### 5. Logs (2 min)
```bash
journalctl -u irrigacion -f --no-pager | head -20
```

---

## 🔍 Troubleshooting Rápido

### Si test_zones_quick.py falla
```bash
# Ver detalles
sudo python3 scripts/diagnose_gpio.py
```

### Si un GPIO específico falla
```bash
# Revisar logs
journalctl -u irrigacion -f | grep "GPIO XX"
```

### Si la app no inicia
```bash
# Validar sintaxis
python3 -m py_compile app/hardware_manager.py

# Ver error completo
python3 run.py 2>&1 | tail -20
```

### Si todo falla
```bash
# Reiniciar el servicio
sudo systemctl restart irrigacion

# Esperar 5 segundos
sleep 5

# Verificar estado
sudo systemctl status irrigacion
```

---

## 📱 Acceso Web

### Página de Riego
```
http://tu-ip-rpi:5000/irrigation
```

### Panel de Control
```
http://tu-ip-rpi:5000/dashboard
```

### Sistema (Health Check)
```
http://tu-ip-rpi:5000/system
```

---

## 📝 Configuración Rápida

### Cambiar Modo Hardware
**Archivo**: `app/config.py`

```python
# Opción 1: GPIO Directo (ACTUAL)
HARDWARE_MODE = 'GPIO'

# Opción 2: LoRa con ESP32
HARDWARE_MODE = 'LORA'

# Opción 3: Simulación
HARDWARE_MODE = 'SIMULATION'
```

Después de cambiar:
```bash
sudo systemctl restart irrigacion
```

---

## 🎯 Estado de Zonas

### Ver Estado en Web
```
GET /irrigation/zones/status
```

### Ver en Logs
```bash
journalctl -u irrigacion -f | grep "Zona"
```

### Verificar Manualmente
```bash
# Cada zona debería encender/apagar
cd /Users/alexg/Sites/irrigacion
sudo python3 scripts/test_zones_quick.py
```

---

## 📊 Información Rápida

### Mapeo GPIO
| GPIO | Zona | Nombre |
|------|------|--------|
| 23 | 1 | Jardín |
| 24 | 2 | Huerta |
| 25 | 3 | Césped |
| 27 | 4 | Árboles |
| 17 | - | Bomba |

### Comandos por Acción
| Acción | Comando |
|--------|---------|
| Verificar | `sudo python3 scripts/test_zones_quick.py` |
| Diagnosticar | `sudo python3 scripts/diagnose_gpio.py` |
| Ver logs | `journalctl -u irrigacion -f` |
| Reiniciar | `sudo systemctl restart irrigacion` |
| Validar | `python3 -m py_compile app/hardware_manager.py` |

---

## 🚨 Emergency Stop

### Detener Todos los GPIOs Ahora
```python
from app.hardware_manager import all_off
all_off()
```

O en web:
```
POST /irrigation/emergency-stop
```

---

## 🔐 Seguridad

### Permisos Requeridos
```bash
# Para ejecutar scripts GPIO
sudo python3 scripts/...

# Para reiniciar servicio
sudo systemctl restart irrigacion
```

### Usuario Recomendado
```bash
# Ejecutar como: pi o root
# NO como usuario regular
```

---

## 📚 Documentación Rápida

| Necesitas... | Comando |
|-------------|---------|
| Leer todo | `less GUIA_RAPIDA_5_MIN.md` |
| Implementar | `less ACTUALIZACION_GPIO_v1.0.md` |
| Detalles | `less SOLUCION_GPIO_ZONAS.md` |
| QA | `less CHECKLIST_IMPLEMENTACION_GPIO.md` |
| Índice | `less INDICE_DOCUMENTACION_GPIO.md` |

---

## 🎓 Atajos Útiles

### Ver solo errores en logs
```bash
journalctl -u irrigacion -f | grep -i "error\|fail\|❌"
```

### Ver solo GPIO en logs
```bash
journalctl -u irrigacion -f | grep "\[HW\]"
```

### Test específico del GPIO 23
```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH)  # ON
GPIO.output(23, GPIO.LOW)   # OFF
GPIO.cleanup()
```

### Obtener estado de todos los GPIOs
```bash
curl http://localhost:5000/irrigation/zones/status | python3 -m json.tool
```

---

## ⏱️ Timeline Rápido

| Acción | Tiempo |
|--------|--------|
| Test Rápido | 1 min |
| Test Completo | 5 min |
| Verificar Web | 5 min |
| Revisar Logs | 2 min |
| **Total** | **13 min** |

---

## 🔗 Enlaces Rápidos

```
Guía Rápida:           GUIA_RAPIDA_5_MIN.md
Implementación:        ACTUALIZACION_GPIO_v1.0.md
Técnico:               SOLUCION_GPIO_ZONAS.md
QA:                    CHECKLIST_IMPLEMENTACION_GPIO.md
Índice:                INDICE_DOCUMENTACION_GPIO.md
Resumen:               RESUMEN_FINAL.md
Cierre:                CIERRE_SOLUCION_GPIO.md
```

---

## ✅ Checklist Rápido

- [ ] Ejecuté test_zones_quick.py
- [ ] Todos los GPIOs muestran OK
- [ ] Probé en la interfaz web
- [ ] Todos los botones funcionan
- [ ] Los logs muestran activaciones
- [ ] Sin errores en la consola
- [ ] Sistema completamente funcional

Si todos están marcados: ✅ **¡Sistema Listo!**

---

**Referencia Rápida**: Marzo 2026
**Versión**: 1.0
**Actualización**: Completa

