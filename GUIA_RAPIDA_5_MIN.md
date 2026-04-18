# 🚀 GUÍA RÁPIDA - Verificación en 5 Minutos

## El Problema ❌
Solo GPIO 24 funcionaba, los otros 3 GPIOs de zona + bomba no respondían.

## La Solución ✅
Se centralizó el control de hardware y se corrigió la configuración.

---

## 🧪 PRUEBA RÁPIDA (5 MINUTOS)

### Paso 1: Ejecutar Test (2 min)
```bash
cd /Users/alexg/Sites/irrigacion
sudo python3 scripts/test_zones_quick.py
```

**Resultado esperado:**
```
▶ Zona 1 - Jardín Principal (GPIO 23)
  Encendiendo... ✅ ON
  Apagando... ✅ OFF

▶ Zona 2 - Huerta (GPIO 24)
  Encendiendo... ✅ ON
  Apagando... ✅ OFF

▶ Zona 3 - Césped (GPIO 25)
  Encendiendo... ✅ ON
  Apagando... ✅ OFF

▶ Zona 4 - Árboles (GPIO 27)
  Encendiendo... ✅ ON
  Apagando... ✅ OFF

▶ Bomba Peristáltica (GPIO 17)
  Encendiendo... ✅ ON
  Apagando... ✅ OFF

✅ TODAS LAS ZONAS FUNCIONAN CORRECTAMENTE
```

### Paso 2: Verificar en Web (2 min)
1. Abre el navegador
2. Ve a `http://localhost:5000/irrigation` (o tu dirección)
3. Scroll a "Control Manual de Zonas"
4. Haz clic en "Iniciar" para cada zona
5. Verifica que los LEDs del relé se encienden

### Paso 3: Revisar Logs (1 min)
```bash
journalctl -u irrigacion -f
# O si ejecutas directamente: python3 run.py
```

Busca mensajes como:
```
[HW] ✅ Zona 1 ON (GPIO 23)
[HW] ✅ Zona 2 ON (GPIO 24)
[HW] ✅ Zona 3 ON (GPIO 25)
[HW] ✅ Zona 4 ON (GPIO 27)
[HW] ✅ Bomba peristáltica ON (GPIO 17)
```

---

## 📋 CHECKLIST RÁPIDO

- [ ] Script `test_zones_quick.py` muestra OK para todos
- [ ] LEDs del relé se encienden en la interfaz web
- [ ] Los logs muestran activación de todos los GPIOs
- [ ] No hay errores en la consola

Si todos están ✅, **¡El sistema está funcionando correctamente!**

---

## 🔧 CONFIGURACIÓN

**Archivo**: `app/config.py`

Debe tener:
```python
HARDWARE_MODE = 'GPIO'  # ← IMPORTANTE
```

Si lo cambias, reinicia la aplicación:
```bash
sudo systemctl restart irrigacion
```

---

## 📊 ESTADO DE GPIOs

| GPIO | Zona | Nombre | Esperado | Test |
|------|------|--------|----------|------|
| 23 | 1 | Jardín | ✅ | ? |
| 24 | 2 | Huerta | ✅ | ? |
| 25 | 3 | Césped | ✅ | ? |
| 27 | 4 | Árboles | ✅ | ? |
| 17 | - | Bomba | ✅ | ? |

Ejecuta el test y completa la columna "Test" con ✅ o ❌

---

## 🆘 SI ALGO FALLA

### Si el test muestra ❌
```bash
# Opción 1: Test completo
sudo python3 scripts/diagnose_gpio.py

# Opción 2: Revisar logs
journalctl -u irrigacion -f

# Opción 3: Verificar configuración
grep HARDWARE_MODE app/config.py
```

### Si un GPIO específico falla
1. Verifica la conexión física
2. Comprueba que el relé tenga alimentación
3. Revisa si otro proceso está usando el GPIO

### Si todo falla
```bash
# Reinicia la aplicación
sudo systemctl restart irrigacion

# O si ejecutas manualmente
python3 run.py
```

---

## 📱 EN MOBILE

Si accedes desde móvil a la interfaz web:
1. Abre `http://tu-ip-rpi:5000/irrigation`
2. Ve a "Control Manual de Zonas"
3. Todos los botones deben funcionar

---

## 🎯 PRÓXIMAS ACCIONES

1. ✅ Confirmar con test rápido
2. ✅ Probar control manual en web
3. ✅ Crear un riego programado de prueba
4. ✅ Verificar que se ejecuta correctamente
5. ✅ Disfrutar del sistema funcionando 😊

---

## 📚 DOCUMENTACIÓN DISPONIBLE

- `RESUMEN_SOLUCION_GPIO.md` - Qué se hizo y por qué
- `ACTUALIZACION_GPIO_v1.0.md` - Instrucciones detalladas
- `SOLUCION_GPIO_ZONAS.md` - Detalles técnicos
- `CHECKLIST_IMPLEMENTACION_GPIO.md` - Verificación completa

---

## 🔗 COMANDOS ÚTILES

```bash
# Test rápido
sudo python3 scripts/test_zones_quick.py

# Test completo
sudo python3 scripts/diagnose_gpio.py

# Ver logs en vivo
journalctl -u irrigacion -f

# Reiniciar aplicación
sudo systemctl restart irrigacion

# Validar sintaxis Python
python3 -m py_compile app/hardware_manager.py
```

---

## ✨ CONCLUSIÓN

Si el test muestra "TODAS LAS ZONAS FUNCIONAN CORRECTAMENTE", ¡la solución está implementada correctamente y el sistema está listo para usar!

**¡Disfruta de tu sistema de riego completamente funcional!** 🌱💧

---

**Última actualización**: Marzo 2026
**Versión**: 1.0

