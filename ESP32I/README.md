# 📡 ESP32I - Integración LoRa con ESP32

Esta carpeta contiene todos los archivos y configuraciones para la comunicación LoRa entre la Raspberry Pi (servidor) y los dispositivos ESP32 (esclavos).

## 📁 Estructura de la Carpeta

```
ESP32I/
├── README.md                    # Este archivo
├── SETUP.md                     # Guía de instalación
├── WIRING.md                    # Esquemas de cableado
├── ARCHITECTURE.md              # Diagrama de arquitectura
├── esp32_lora_firmware.ino      # Código Arduino para ESP32
├── lora_gateway.py              # Script gateway en Raspberry Pi
├── lora_protocol.py             # Protocolos de comunicación
├── config.json                  # Configuración LoRa
└── examples/                    # Ejemplos de uso
    ├── basic_communication.py
    ├── multi_zone_control.py
    └── data_logging.py
```

## 🎯 Objetivos de la Integración

1. **Comunicación Bidireccional** 
   - RPi → ESP32: Comandos de control de solenoides
   - ESP32 → RPi: Telemetría y estado de sensores

2. **Control de Riegos**
   - Activar/desactivar zonas de riego remotamente
   - Recibir confirmación de ejecución

3. **Monitoreo de Sensores**
   - Temperatura y humedad local (DHT22)
   - Flujo de agua
   - Presión de agua

4. **Sincronización de Programación**
   - Enviar riegos programados al ESP32
   - El ESP32 ejecuta localmente si hay conexión
   - Fallback a ejecución local en RPi

## 🔧 Requisitos Hardware

### Para ESP32:
- 1x ESP32 (con soporte LoRa)
- 1x Módulo LoRa (e.g., SX1276)
- 4x Relés de estado sólido o electromecánicos
- 4x Solenoides (válvulas)
- 1x DHT22 (temperatura/humedad)
- 1x Sensor de flujo de agua
- 1x Sensor de presión

### Para Raspberry Pi:
- 1x Módulo LoRa (igual que ESP32)
- Cables de conexión SPI/UART

## 📋 Configuración Rápida

### 1. Hardware LoRa (ESP32)
```
ESP32 PIN      | LoRa MODULE
GPIO 5 (SS)    | CS
GPIO 18 (SCK)  | SCK
GPIO 23 (MOSI) | MOSI
GPIO 19 (MISO) | MISO
GPIO 14        | DIO0
GPIO 26        | RST
GND            | GND
3.3V           | VCC
```

### 2. Solenoides (ESP32)
```
GPIO 25 → Relé 1 → Solenoide Sector 1 (Árboles)
GPIO 26 → Relé 2 → Solenoide Sector 2 (Jardín)
GPIO 27 → Relé 3 → Solenoide Sector 3 (Huerta)
GPIO 32 → Relé 4 → Solenoide Sector 4 (Césped)
```

### 3. Sensores (ESP32)
```
GPIO 4 (ADC)   → Sensor de presión (0-10V)
GPIO 36 (ADC)  → Sensor de flujo (0-5V)
GPIO 22 (I2C)  → DHT22 (temperatura/humedad)
```

## 📡 Protocolo de Comunicación

### Frame LoRa:
```
[1 byte: HEADER] [1 byte: CMD] [2 bytes: DATA] [1 byte: CHECKSUM]
```

### Comandos:
```
0x01: ZONE_ON     - Activar zona (DATA: 1-4)
0x02: ZONE_OFF    - Desactivar zona (DATA: 1-4)
0x03: STATUS      - Solicitar estado
0x04: TELEMETRY   - Enviar datos de sensores
0x05: PING        - Verificar conexión
```

### Ejemplo:
```
Activar Zona 1: [0xAA][0x01][0x0001][0x??]
Desactivar Zona 3: [0xAA][0x02][0x0003][0x??]
```

## 🚀 Instalación y Uso

### Paso 1: Subir código a ESP32
```bash
# Abre Arduino IDE
# Instala librerías:
#   - LoRa by Sandeep Mistry
#   - DHT by Adafruit
#   - Adafruit Unified Sensor

# Copia esp32_lora_firmware.ino a Arduino
# Compila y carga en tu placa ESP32
```

### Paso 2: Instalar en Raspberry Pi
```bash
# Instala dependencias
pip install lora spidev RPi.GPIO

# Copia archivos a /app/lora_gateway/
cp lora_gateway.py /app/lora_gateway.py
cp lora_protocol.py /app/lora_protocol.py

# Configura permisos SPI
sudo usermod -a -G spi $USER
```

### Paso 3: Integración con Flask
```python
# En app/__init__.py
from app.lora_gateway import LoRaGateway

lora = LoRaGateway()
lora.start()  # Inicia listener en background
```

### Paso 4: Controlar desde API
```python
# En app/routes.py
@routes.route("/irrigation/lora/<int:zone_id>/on", methods=["POST"])
@login_required
def irrigation_lora_on(zone_id):
    lora.send_command("ZONE_ON", zone_id)
    return jsonify({"success": True})
```

## 📊 Monitoreo de Conexión

Ver estado de conexión LoRa en `/system`:
```
ESP32 #1 - Sectores 1-4
├─ Estado: Online
├─ Señal: -85 dBm
├─ Última comunicación: Hace 2s
└─ Solenoides: 1(ON) 2(OFF) 3(ON) 4(OFF)
```

## 🔍 Debugging

### Habilitar logs LoRa:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitorear puerto serial del ESP32:
```bash
# Usa Arduino IDE > Serial Monitor
# Baud rate: 115200
# Verás: [LORA] Waiting for command...
```

## 📚 Referencias

- [LoRa Basics](https://www.thethingsnetwork.org/docs/lorawan/)
- [Arduino LoRa Library](https://github.com/sandeepmistry/arduino-LoRa)
- [ESP32 Pinout](https://en.wikipedia.org/wiki/ESP32)

## ⚠️ Notas Importantes

1. **Rango LoRa:** Hasta 2 km en línea recta (depende del ambiente)
2. **Potencia:** El ESP32 drena ~80mA en transmisión, usa fuente estable
3. **Interferencia:** Alejar de WiFi/Bluetooth, pueden interferir
4. **Sincronización:** Implementa timeout para desconexiones

---

**Estado:** 🟡 EN DESARROLLO
**Versión:** 0.1 (Estructura base)
**Próximo paso:** Implementar lora_gateway.py

