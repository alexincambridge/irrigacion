# 📊 Loggers de Sensores - Sistema de Irrigación v4.0

> Guía de uso de los diferentes scripts de logging de sensores

---

## 📋 Resumen de Scripts

| Script | Función | GPIO | Intervalo | Estado |
|---|---|---|---|---|
| **`dht_logger.py`** | Temperatura y Humedad (DHT22) | GPIO 4 | 2s | ✅ **PRODUCCIÓN** |
| **`sensor_data_logger.py`** | Presión, Solar, pH, EC | — | 10s | ⚠️ Simulación |
| **`fertilizer_counter.py`** | Pulsos de bomba peristáltica | GPIO 18 | 10s | ⚠️ Simulación |
| **`dht11.py`** | Generador de datos simulados | — | 5s | 🎲 PRUEBAS |

---

## 🌡️ 1. DHT22 Logger (PRODUCCIÓN)

**Script:** `scripts/dht_logger.py`

**Función:** Lee temperatura y humedad en tiempo real e inserta en `dht_readings`

**Hardware:**
- Sensor: DHT22
- Pin: GPIO 4 (board.D4)
- Resistencia pull-up: 4.7kΩ entre VCC y DATA

**Parámetro crítico:**
```python
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)  # ← OBLIGATORIO
```

**Características:**
- ✅ Manejo robusto de errores (RuntimeError normal en DHT22)
- ✅ Limpieza de recursos (`dht.exit()`)
- ✅ Intervalo mínimo 2 segundos
- ✅ Datos reales en base de datos

**Ejecutar:**
```bash
python3 scripts/dht_logger.py
```

**Salida esperada:**
```
🌡️ DHT22 Logger iniciado
============================================================
Pin: GPIO 4 (board.D4)
Intervalo: 2s
BD: /home/alexdev/Documents/irrigacion/instance/irrigation.db
============================================================
[✅ OK] T=24.5°C  H=65.3%  @ 14:32:15
[✅ OK] T=24.5°C  H=65.2%  @ 14:32:17
[✅ OK] T=24.6°C  H=65.4%  @ 14:32:19
```

---

## 📈 2. Sensor Data Logger

**Script:** `scripts/sensor_data_logger.py`

**Función:** Lee sensores adicionales (presión, radiación solar, pH, EC) e inserta en `sensor_data`

**Sensores (con placeholders para reales):**
- 🔴 `read_pressure()` — Presión del agua (hPa)
- ☀️ `read_solar()` — Radiación solar (W/m²)
- 🧪 `read_ph()` — pH del agua
- ⚡ `read_ec()` — Conductividad eléctrica (mS/cm)

**Estado actual:** 
- ⚠️ Datos simulados (random)
- 📝 TODO: Conectar sensores reales

**Cómo conectar un sensor real:**

Ejemplo con sensor de presión en ADC MCP3008:
```python
def read_pressure():
    """Lee presión analógica del MCP3008"""
    import Adafruit_MCP3008
    
    mcp = Adafruit_MCP3008.MCP3008(channel=0)
    raw = mcp.read()
    voltage = raw * 3.3 / 1023
    pressure_hpa = voltage * 243  # Calibración según sensor
    return round(pressure_hpa, 1)
```

**Ejecutar:**
```bash
python3 scripts/sensor_data_logger.py
```

**Salida:**
```
📊 Sensor Data Logger iniciado
============================================================
Sensores: Presión, Radiación Solar, pH, EC
Intervalo: 10s
BD: .../irrigation.db
============================================================
⚠️  NOTA: Datos simulados. Reemplaza read_* con sensores reales.
============================================================
[✅ OK] T=24.5°C | H=65.1% | P=1012.3hPa | S=847W/m² | pH=6.85 | EC=1.23mS/cm
```

---

## 💊 3. Fertilizer Counter

**Script:** `scripts/fertilizer_counter.py`

**Función:** Cuenta pulsos de la bomba peristáltica e inserta en `water_consumption`

**Hardware:**
- Contador: Sensor de pulsos
- Pin: GPIO 18 (entrada con pull-up)
- Calibración: 0.5 mL por pulso (ajusta en `PULSE_TO_ML`)

**Características:**
- ✅ Detección de flancos descendentes
- ✅ Acumulación de pulsos por periodo
- ✅ Conversión a volumen (mL → litros)
- ⚠️ Simulación por defecto

**Calibración del sensor:**
1. Mide cuánto volumen entrega un número conocido de pulsos
2. Calcula: `mL_por_pulso = volumen_total / num_pulsos`
3. Actualiza `PULSE_TO_ML = valor_calculado`

**Ejecutar:**
```bash
python3 scripts/fertilizer_counter.py
```

**Salida:**
```
💊 Fertilizer Counter Logger iniciado
============================================================
Pin: GPIO 18
Calibración: 0.5 mL/pulso
============================================================
[✅ OK] 3 pulsos | 1.5mL | @ 14:32:25
[ℹ️  INFO] 0 pulsos | 0.0mL | @ 14:32:35
[✅ OK] 5 pulsos | 2.5mL | @ 14:32:45
```

---

## 🎲 4. Simulador de Datos (PRUEBAS)

**Script:** `scripts/dht11.py`

**Función:** Genera datos simulados para pruebas del dashboard

**Uso:**
- 🎓 Pruebas sin hardware real
- 📊 Llenar histórico rápidamente
- 🖼️ Validar gráficos y gauges

**Datos simulados:**
- Temperatura: 15-35°C
- Humedad: 30-80%
- Radiación Solar: 200-1000 W/m²
- Presión: 980-1030 hPa
- EC: 0.5-3.5 mS/cm
- pH: 5.5-7.5

**Ejecutar:**
```bash
python3 scripts/dht11.py
```

**Salida:**
```
🎲 SIMULADOR DE DATOS - Pruebas solamente
============================================================
BD: .../irrigation.db
Insertando datos cada 5 segundos...
Presiona Ctrl+C para detener
============================================================

[✅] T=27.3°C | H=52.1% | S=645W/m² | P=1015.2hPa | pH=6.42 | EC=1.87mS/cm
[✅] T=18.9°C | H=71.4% | S=312W/m² | P=998.7hPa | pH=6.58 | EC=2.15mS/cm
```

---

## 🚀 Ejecutar Todo Automáticamente

Crear script `scripts/start_all_loggers.sh`:

```bash
#!/bin/bash

echo "🚀 Iniciando todos los loggers..."

# En diferentes terminales o con & para background
python3 scripts/dht_logger.py &
python3 scripts/sensor_data_logger.py &
python3 scripts/fertilizer_counter.py &

wait
```

Hacer ejecutable:
```bash
chmod +x scripts/start_all_loggers.sh
./scripts/start_all_loggers.sh
```

---

## 🔧 Configuración de Systemd (Para autostart)

Crear `/etc/systemd/system/irrigation-dht.service`:

```ini
[Unit]
Description=DHT22 Logger - Irrigation System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/irrigacion
ExecStart=/usr/bin/python3 /home/pi/irrigacion/scripts/dht_logger.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable irrigation-dht.service
sudo systemctl start irrigation-dht.service
sudo systemctl status irrigation-dht.service
```

---

## 📊 Tablas de Base de Datos

### `dht_readings` (DHT22)
```
id | temperature | humidity | created_at
---|---|---|---
1  | 24.5        | 65.1     | 2026-03-24 14:32:15
2  | 24.6        | 65.2     | 2026-03-24 14:32:17
```

### `sensor_data` (Presión, Solar, pH, EC)
```
id | temperature | humidity | solar | pressure | ec   | ph  | created_at
---|---|---|---|---|---|---|---
1  | 24.5        | 65.1     | 847   | 1012.3   | 1.23 | 6.85| 2026-03-24 14:32:25
```

### `water_consumption` (Contador fertilizante)
```
id | irrigation_id | liters | cost | timestamp
---|---|---|---|---
1  | NULL          | 0.0015 | NULL | 2026-03-24 14:32:35
```

---

## 🐛 Troubleshooting

### DHT22 no funciona
✅ **Solución:**
```python
# ❌ INCORRECTO (pulseio genera problemas en RPi)
dht = adafruit_dht.DHT22(board.D4)

# ✅ CORRECTO
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
```

### RuntimeError: Device is not initialized
❌ Significa que el sensor aún se está calentando o hay conexión débil
✅ El script automáticamente reintentar — es normal

### Datos None
❌ El sensor no está respondiendo
✅ Verificar:
- Resistencia pull-up 4.7kΩ presente
- Voltaje correcto (3.3V)
- Conexión física GPIO 4

### GPIO no disponible
⚠️ No es RPi o GPIO no configurado
✅ Verifica con: `ls /dev/gpiomem`

---

## 📝 Próximas Mejoras

- [ ] Integrar sensores reales (presión, pH, EC)
- [ ] Dashboard en tiempo real con WebSocket
- [ ] Alertas cuando valores salen de rango
- [ ] Exportar datos a CSV/JSON
- [ ] Gráficos históricos por fecha

---

> **Última actualización:** 2026-03-24  
> **Versión:** 4.0

