# 📚 Índice Completo - DHT22 & Sensores v4.0

## 🎯 ¿Qué Necesito Hacer?

### ⚡ Empezar Ahora (2 minutos)
1. Lee: [`QUICK_START_SENSORES.md`](QUICK_START_SENSORES.md)
2. Ejecuta: `python3 scripts/dht_logger.py`
3. Verifica: `sqlite3 instance/irrigation.db "SELECT * FROM dht_readings;"`

### 🔧 Instalar Dependencias
- Archivo: [`INSTALACION_DEPENDENCIAS.md`](INSTALACION_DEPENDENCIAS.md)
- Comando rápido: `pip3 install adafruit-circuitpython-dht`

### 📖 Entender Todo
- Archivo: [`SENSORES_LOGGERS_GUIDE.md`](SENSORES_LOGGERS_GUIDE.md) (Completo)
- Archivo: [`DHT22_SENSORES_RESUMEN.md`](DHT22_SENSORES_RESUMEN.md) (Técnico)

### 🚀 Referencia Rápida
- Archivo: [`CHEATSHEET_SENSORES.md`](CHEATSHEET_SENSORES.md)

### 🧪 Probar Sistema
- Script: `python3 test_sensors_quick.py`

---

## 📂 Scripts/Loggers (Cuál Usar)

### ✅ DHT22 - USAR ESTO
```bash
python3 scripts/dht_logger.py
```
- **Estado:** Datos reales ✅
- **Tabla:** `dht_readings`
- **Intervalo:** 2 segundos
- **GPIO:** 4

**Descripción:** Lectura de temperatura y humedad. Inserta datos reales en BD cada 2 segundos.

**Cuándo usar:** Siempre que quieras datos reales del DHT22.

---

### ⚠️ Sensor Data Logger (Simulado)
```bash
python3 scripts/sensor_data_logger.py
```
- **Estado:** Datos simulados ⚠️ (TODO: conectar reales)
- **Tabla:** `sensor_data`
- **Intervalo:** 10 segundos
- **Sensores:** Presión, Solar, pH, EC

**Descripción:** Placeholder para sensores adicionales. Actualmente datos aleatorios.

**Cuándo usar:** Cuando conectes sensores reales (edita `read_*()` functions).

---

### ⚠️ Fertilizer Counter (Simulado)
```bash
python3 scripts/fertilizer_counter.py
```
- **Estado:** Datos simulados ⚠️
- **Tabla:** `water_consumption`
- **Intervalo:** 10 segundos
- **GPIO:** 18

**Descripción:** Cuenta pulsos del contador de fertilizante. Actualmente simulado.

**Cuándo usar:** Cuando tengas el contador físico conectado.

---

### 🎲 Simulador de Datos (Pruebas)
```bash
python3 scripts/dht11.py
```
- **Estado:** Datos random 🎲
- **Tabla:** `sensor_data`
- **Intervalo:** 5 segundos

**Descripción:** Generador de datos para testing sin hardware.

**Cuándo usar:** Para pruebas del dashboard sin sensores reales.

---

## 📄 Archivos de Código Modificados

| Archivo | Cambio | Por Qué | Impacto |
|---|---|---|---|
| `app/sensors/dht_reader.py` | + `use_pulseio=False` | Obligatorio en RPi | DHT22 funciona |
| `scripts/dht_logger.py` | + `use_pulseio=False` | Obligatorio en RPi | DHT22 funciona |
| `scripts/dht11.py` | Refactorizado | Mejor estructura | Simulador mejorado |

---

## 🆕 Archivos Nuevos Creados

### Scripts
| Archivo | Función | Archivo |
|---|---|---|
| `sensor_data_logger.py` | Sensores adicionales | scripts/ |
| `fertilizer_counter.py` | Contador fertilizante | scripts/ |

### Documentación
| Archivo | Contenido | Comienzo |
|---|---|---|
| `QUICK_START_SENSORES.md` | 30 segundos | **👈 EMPEZAR AQUÍ** |
| `CHEATSHEET_SENSORES.md` | Referencia rápida | Línea 1 |
| `SENSORES_LOGGERS_GUIDE.md` | Guía completa | 📚 Estudio |
| `INSTALACION_DEPENDENCIAS.md` | Instalación | pip3 |
| `DHT22_SENSORES_RESUMEN.md` | Técnico | 🔧 Detalles |

### Testing
| Archivo | Función |
|---|---|
| `test_sensors_quick.py` | Prueba DHT22 + BD + inserción |

---

## 🗂️ Estructura de BD

### Tabla: `dht_readings` (DHT22 Real)
```sql
CREATE TABLE dht_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabla: `sensor_data` (Sensores Adicionales)
```sql
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    solar REAL,
    pressure REAL,
    ec REAL,
    ph REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Tabla: `water_consumption` (Fertilizante)
```sql
CREATE TABLE water_consumption (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    irrigation_id INTEGER,
    liters REAL,
    cost REAL,
    timestamp TEXT
)
```

---

## 🚀 Comandos Rápidos

### Instalar
```bash
pip3 install adafruit-circuitpython-dht
```

### Ejecutar
```bash
# Opción 1: Solo DHT22
python3 scripts/dht_logger.py

# Opción 2: Todo
python3 scripts/dht_logger.py & \
python3 scripts/sensor_data_logger.py & \
python3 scripts/fertilizer_counter.py

# Opción 3: Simulador
python3 scripts/dht11.py
```

### Verificar
```bash
# Test todo
python3 test_sensors_quick.py

# Ver datos
sqlite3 instance/irrigation.db "SELECT * FROM dht_readings LIMIT 5;"

# Contar registros
sqlite3 instance/irrigation.db "SELECT COUNT(*) FROM dht_readings;"
```

---

## 📊 Tablas Comparativa de Opciones

| Opción | Comando | Datos | Sensores | Para |
|---|---|---|---|---|
| **1** | `python3 scripts/dht_logger.py` | Reales ✅ | DHT22 | Producción |
| **2** | Opción 1 + 2 + 3 en paralelo | Reales ✅ | Todos | Completo |
| **3** | `python3 scripts/dht11.py` | Random 🎲 | Varios | Testing |

---

## 🎓 Aprendiste

- ✅ **Parámetro crítico:** `use_pulseio=False` en DHT22
- ✅ **Arquitectura:** Sensores desacoplados
- ✅ **Base de datos:** Múltiples tablas para datos diferentes
- ✅ **Testing:** Cómo validar sensores
- ✅ **Documentación:** Cómo hacer docs técnicas

---

## 🔗 Enlaces Internos

- [Quick Start (30s)](QUICK_START_SENSORES.md)
- [Instalación](INSTALACION_DEPENDENCIAS.md)
- [Guía Completa](SENSORES_LOGGERS_GUIDE.md)
- [CheatSheet](CHEATSHEET_SENSORES.md)
- [Resumen Técnico](DHT22_SENSORES_RESUMEN.md)

---

## 🆘 Solución Rápida de Problemas

| Problema | Solución |
|---|---|
| DHT22 no funciona | Ver: `SENSORES_LOGGERS_GUIDE.md` → Troubleshooting |
| Falta librería | Ver: `INSTALACION_DEPENDENCIAS.md` |
| Datos no se guardan | Ejecutar: `test_sensors_quick.py` |
| No entiendo qué hacer | Leer: `QUICK_START_SENSORES.md` |

---

## 📈 Roadmap

- [x] DHT22 funciona con `use_pulseio=False`
- [x] Datos reales en BD
- [x] Sensores separados
- [x] Documentación completa
- [ ] Conectar sensores reales (cuando tengas hardware)
- [ ] Configurar autostart
- [ ] Integrar con dashboard
- [ ] Alertas cuando salen de rango
- [ ] Exportar datos a CSV

---

## 💡 Pro Tips

1. **Usa `QUICK_START_SENSORES.md` para empezar**
2. **DHT22 requiere GPIO 4 + resistencia 4.7kΩ**
3. **Intervalo mínimo: 2 segundos**
4. **RuntimeError es normal (el script lo maneja)**
5. **Datos se guardan automáticamente**
6. **Dashboard los mostrará sin configuración extra**

---

## 📞 Contacto / Soporte

Para cada tema:
- **Instalación:** `INSTALACION_DEPENDENCIAS.md`
- **Uso:** `QUICK_START_SENSORES.md`
- **Detalles técnicos:** `SENSORES_LOGGERS_GUIDE.md`
- **Referencia:** `CHEATSHEET_SENSORES.md`
- **Testing:** `test_sensors_quick.py`

---

> **Versión:** 4.0  
> **Estado:** ✅ Listo para producción  
> **Última actualización:** 2026-03-24

