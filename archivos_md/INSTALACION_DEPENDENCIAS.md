# 📦 Instalación de Dependencias - Sistema de Sensores

> Guía para instalar las librerías necesarias para DHT22 y sensores

---

## 🐍 Python 3 y pip

**Verificar instalación:**
```bash
python3 --version
pip3 --version
```

**Instalar si falta:**
```bash
# Raspberry Pi / Debian
sudo apt update
sudo apt install -y python3 python3-pip

# macOS
brew install python3
```

---

## ⚡ Dependencias Principales

### 1. Adafruit CircuitPython DHT (CRÍTICO para DHT22)

**Instalar:**
```bash
pip3 install adafruit-circuitpython-dht
```

**Verificar instalación:**
```bash
python3 -c "import adafruit_dht; print('✅ OK')"
```

**Descripción:**
- Librería oficial de Adafruit para DHT11/DHT22
- Soporta `use_pulseio=False` (imprescindible en RPi)
- Compatible con CircuitPython

---

### 2. Adafruit CircuitPython (librerías base)

**Instalar:**
```bash
pip3 install adafruit-circuitpython-mcp3xxx
```

**Para qué sirve:**
- MCP3008 ADC (conversión analógica-digital)
- Sensores analógicos (presión, pH, EC)

---

### 3. RPi.GPIO (solo en Raspberry Pi)

**Instalar:**
```bash
pip3 install RPi.GPIO
```

**Para qué sirve:**
- Control de GPIOs en Raspberry Pi
- Lectura de contador de fertilizante (GPIO 18)

**NOTA:** En macOS/dev no es necesario (el script maneja el ImportError)

---

### 4. SpiDev (solo si usas MCP3008)

**Instalar:**
```bash
pip3 install spidev
```

**Para qué sirve:**
- Comunicación SPI con MCP3008

**Requisito previo en RPi:**
```bash
sudo raspi-config nonint do_spi 0  # Habilitar SPI
```

---

## 📋 Script de Instalación Automática

Crear `setup_dependencies.sh`:

```bash
#!/bin/bash

echo "📦 Instalando dependencias del sistema de sensores..."
echo "=================================================="

# Actualizar pip
pip3 install --upgrade pip

# Librerías Python
echo "🔹 Instalando librerías Python..."
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-circuitpython-mcp3xxx

# Solo en RPi
if [ -f /etc/os-release ]; then
    if grep -q "Raspberry Pi" /etc/os-release; then
        echo "🔹 Detectada Raspberry Pi..."
        pip3 install RPi.GPIO
        pip3 install spidev
        
        echo "🔹 Habilitando SPI..."
        sudo raspi-config nonint do_spi 0
    fi
fi

echo "✅ Instalación completada"
echo "=================================================="

# Verificar
echo "🔍 Verificando instalaciones..."
python3 -c "import adafruit_dht; print('✅ adafruit_dht')" && \
python3 -c "import adafruit_circuitpython_mcp3xxx; print('✅ mcp3xxx')" || true

echo "✅ Listo para usar los loggers"
```

Hacer ejecutable y correr:
```bash
chmod +x setup_dependencies.sh
./setup_dependencies.sh
```

---

## 📥 Instalación Manual Paso a Paso

### En Raspberry Pi (Recomendado)

```bash
# 1. Actualizar sistema
sudo apt update
sudo apt upgrade -y

# 2. Instalar Python y pip
sudo apt install -y python3 python3-pip

# 3. Instalar librerías
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-circuitpython-mcp3xxx
pip3 install RPi.GPIO
pip3 install spidev

# 4. Habilitar SPI (si vas a usar MCP3008)
sudo raspi-config

# Interfaces → SPI → Enable

# 5. Verificar
python3 -c "import adafruit_dht; print('✅ DHT funciona')"
```

### En macOS (Desarrollo)

```bash
# 1. Actualizar pip
pip3 install --upgrade pip

# 2. Instalar librerías (sin RPi.GPIO)
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-circuitpython-mcp3xxx

# 3. Verificar
python3 -c "import adafruit_dht; print('✅ DHT funciona')"
```

### En Linux (Desarrollo)

```bash
# Igual a macOS
pip3 install adafruit-circuitpython-dht
pip3 install adafruit-circuitpython-mcp3xxx
```

---

## 🧪 Verificar Instalaciones

### DHT22
```bash
python3 << 'EOF'
import board
import adafruit_dht

print("✅ Librerías importadas correctamente")

# Verificar que board.D4 existe
print(f"✅ board.D4 disponible: {board.D4}")

# Crear instancia (sin hardware)
try:
    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    print("✅ DHT22 con use_pulseio=False funciona")
    dht.exit()
except Exception as e:
    print(f"⚠️  {e}")
EOF
```

### GPIO (solo RPi)
```bash
python3 << 'EOF'
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    print("✅ RPi.GPIO disponible")
    GPIO.cleanup()
except ImportError:
    print("ℹ️  RPi.GPIO no disponible (normal en desarrollo)")
EOF
```

### Base de Datos
```bash
python3 << 'EOF'
import sqlite3
from pathlib import Path

db_path = Path("instance/irrigation.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dht_readings")
    count = cur.fetchone()[0]
    conn.close()
    print(f"✅ Base de datos funciona ({count} registros DHT22)")
else:
    print(f"❌ BD no existe: {db_path}")
EOF
```

---

## 🆘 Troubleshooting

### Error: "No module named 'adafruit_dht'"
```bash
pip3 install adafruit-circuitpython-dht
```

### Error: "RuntimeError: Device is not initialized"
**Causa:** Sensor aún calentando o conexión débil
**Solución:** Normal, el script reintentar automáticamente

### Error: "ImportError: No module named RPi.GPIO"
**Causa:** No estás en Raspberry Pi
**Solución:** Normal en desarrollo, el script maneja esto

### Error: "Permission denied" al acceder GPIO
```bash
# Agregar usuario al grupo gpio
sudo usermod -a -G gpio $USER
# Reiniciar sesión
```

### Error: SPI no disponible
```bash
# Habilitar SPI
sudo raspi-config
# Interfaces → SPI → Enable

# Verificar
ls /dev/spidev*
```

---

## ✅ Checklist de Instalación

- [ ] Python 3.8+
- [ ] pip actualizado
- [ ] adafruit-circuitpython-dht
- [ ] adafruit-circuitpython-mcp3xxx
- [ ] RPi.GPIO (si es RPi)
- [ ] SPI habilitado (si usas MCP3008)
- [ ] BD `instance/irrigation.db` existe
- [ ] Tablas `dht_readings` y `sensor_data` existen

---

## 🚀 Verificación Final

Ejecutar el test:
```bash
python3 test_sensors_quick.py
```

Esperado:
```
🎉 TODAS LAS PRUEBAS PASARON (3/3)
```

---

> **Última actualización:** 2026-03-24  
> **Versión:** 4.0

