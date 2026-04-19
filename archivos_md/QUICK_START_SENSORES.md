# 🚀 Quick Start - DHT22 & Sensores

> Guía rápida para empezar a usar los loggers de sensores

---

## ⚡ 30 segundos para empezar

### 1. Instalar dependencias
```bash
pip3 install adafruit-circuitpython-dht
```

### 2. Ejecutar DHT22 Logger
```bash
python3 scripts/dht_logger.py
```

### 3. Verificar datos en BD
```bash
sqlite3 instance/irrigation.db "SELECT * FROM dht_readings ORDER BY id DESC LIMIT 5;"
```

**Listo ✅**

---

## 📊 Qué Se Guardará

Cada 2 segundos:
```
ID | Temperatura (°C) | Humedad (%) | Timestamp
---|---|---|---
1  | 24.5             | 65.1        | 2026-03-24 14:32:15
2  | 24.6             | 65.2        | 2026-03-24 14:32:17
```

---

## 🎯 Casos de Uso

### Caso 1: Solo temperatura y humedad
```bash
python3 scripts/dht_logger.py
```
✅ Datos reales cada 2 segundos

### Caso 2: Con sensores adicionales (simulados)
```bash
# Terminal 1
python3 scripts/dht_logger.py

# Terminal 2
python3 scripts/sensor_data_logger.py

# Terminal 3
python3 scripts/fertilizer_counter.py
```
✅ Múltiples sensores en paralelo

### Caso 3: Pruebas sin hardware
```bash
python3 scripts/dht11.py
```
✅ Datos simulados cada 5 segundos

---

## 🐛 Si no funciona

### DHT22 muestra errores
```python
# ❌ INCORRECTO
dht = adafruit_dht.DHT22(board.D4)

# ✅ CORRECTO (USAMOS ESTO)
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
```

### No se guardan datos
1. Verificar BD existe:
   ```bash
   ls instance/irrigation.db
   ```

2. Verificar tabla existe:
   ```bash
   sqlite3 instance/irrigation.db ".tables"
   ```

3. Ver últimos registros:
   ```bash
   sqlite3 instance/irrigation.db "SELECT COUNT(*) FROM dht_readings;"
   ```

---

## 📂 Archivos Principales

```
irrigacion/
├── scripts/
│   ├── dht_logger.py              ← DHT22 (USAR ESTO)
│   ├── sensor_data_logger.py       ← Sensores adicionales
│   ├── fertilizer_counter.py       ← Contador fertilizante
│   └── dht11.py                    ← Simulador de datos
│
├── app/sensors/
│   ├── dht_reader.py               ← Módulo DHT22
│   └── routes.py                   ← Endpoints API
│
├── SENSORES_LOGGERS_GUIDE.md       ← Guía completa
├── INSTALACION_DEPENDENCIAS.md     ← Cómo instalar
└── test_sensors_quick.py           ← Prueba rápida
```

---

## 🔌 Hardware Necesario

### Mínimo (DHT22)
- Raspberry Pi 4
- DHT22
- Resistencia 4.7kΩ
- Cables

### Completo (todos los sensores)
- Raspberry Pi 4
- DHT22
- Sensor de presión (MCP3008 + sensor analógico)
- Sensor solar (MCP3008 + fotodiodo)
- Sensor de pH (MCP3008 + sonda)
- Sensor EC (MCP3008 + sonda)
- Contador de pulsos (GPIO 18)
- Cables, resistencias, capacitores

---

## 🔄 Actualizaciones Automáticas

### Opción 1: Cron job
```bash
crontab -e

# Agregar esta línea para iniciar al boot:
@reboot /usr/bin/python3 /home/pi/irrigacion/scripts/dht_logger.py &
```

### Opción 2: Systemd service
```bash
# Ver: SENSORES_LOGGERS_GUIDE.md sección "Configuración Systemd"
sudo systemctl start irrigation-dht.service
sudo systemctl status irrigation-dht.service
```

---

## 📊 Dashboard Integration

Los datos se guardan automáticamente en BD.
El dashboard los mostrará en:
- Dashboard principal (gauges de temperatura/humedad)
- Página de sensores (tabla histórica)
- Gráficos históricos (si están implementados)

**No requiere configuración adicional ✅**

---

## 🧪 Probar Todo

```bash
# Test rápido
python3 test_sensors_quick.py

# Salida esperada:
# DHT22................................ ✅ PASS
# Base de Datos........................ ✅ PASS
# Insertar............................ ✅ PASS
# 🎉 TODAS LAS PRUEBAS PASARON (3/3)
```

---

## 📞 Soporte

| Problema | Solución |
|---|---|
| DHT22 no responde | Ver `SENSORES_LOGGERS_GUIDE.md` → Troubleshooting |
| Errores de importación | Ejecutar: `INSTALACION_DEPENDENCIAS.md` |
| Datos no se guardan | Verificar BD existe: `ls instance/irrigation.db` |
| GPIO no disponible | Normal en desarrollo, el script lo maneja |

---

## ✅ Checklist

- [ ] ✅ Instalar `pip3 install adafruit-circuitpython-dht`
- [ ] ✅ Conectar DHT22 en GPIO 4
- [ ] ✅ Ejecutar `python3 scripts/dht_logger.py`
- [ ] ✅ Ver datos en `instance/irrigation.db`
- [ ] ✅ Datos aparecen en dashboard

---

> **Ready to use!** 🚀  
> Para más detalles, ver `SENSORES_LOGGERS_GUIDE.md`

