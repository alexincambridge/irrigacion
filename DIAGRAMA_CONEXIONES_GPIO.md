# 📐 Diagrama de Conexiones GPIO — Raspberry Pi

> **Sistema de Irrigación Inteligente**  
> Fecha: 2026-03-24  
> Hardware: Raspberry Pi 4B + DHT22 + Módulo Relé 4CH

---

## 📋 Resumen de GPIOs Asignados

| Dispositivo | GPIO (BCM) | Pin Físico | Dirección | Descripción |
|---|---|---|---|---|
| **Relé Zona 1** (Jardín) | GPIO 16 | Pin 36 | OUTPUT | Electroválvula solenoide |
| **Relé Zona 2** (Huerta) | GPIO 23 | Pin 16 | OUTPUT | Electroválvula solenoide |
| **Relé Zona 3** (Césped) | GPIO 24 | Pin 18 | OUTPUT | Electroválvula solenoide |
| **Relé Zona 4** (Árboles) | GPIO 26 | Pin 37 | OUTPUT | Electroválvula solenoide |
| **DHT22** (Temp/Humedad) | GPIO 4 | Pin 7 | INPUT | Sensor temperatura y humedad |
| **Bomba Peristáltica** | GPIO 17 | Pin 11 | OUTPUT | Fertilización |
| **Contador Fertilizante** | GPIO 18 | Pin 12 | INPUT | Pulsos caudal |
| **LoRa EBYTE TXD** | GPIO 14 | Pin 8 | UART TX | RPi TX → LoRa RXD |
| **LoRa EBYTE RXD** | GPIO 15 | Pin 10 | UART RX | RPi RX ← LoRa TXD |
| **LoRa EBYTE M0** | GPIO 5 | Pin 29 | OUTPUT | Modo operación M0 |
| **LoRa EBYTE M1** | GPIO 6 | Pin 31 | OUTPUT | Modo operación M1 |
| **LoRa EBYTE AUX** | GPIO 13 | Pin 33 | INPUT | Estado del módulo |

---

## 🔌 1. Módulo Relé 4 Canales

El módulo relé controla las 4 electroválvulas solenoides de riego.

### Conexión Relé ↔ Raspberry Pi

```
┌─────────────────────┐          ┌──────────────────┐
│   MÓDULO RELÉ 4CH   │          │  RASPBERRY PI 4  │
│                      │          │                  │
│  VCC ───────────────────────── 5V   (Pin 2)       │
│  GND ───────────────────────── GND  (Pin 6)       │
│  IN1 ───────────────────────── GPIO 16 (Pin 36)   │  → Zona 1 (Jardín)
│  IN2 ───────────────────────── GPIO 23 (Pin 16)   │  → Zona 2 (Huerta)
│  IN3 ───────────────────────── GPIO 24 (Pin 18)   │  → Zona 3 (Césped)
│  IN4 ───────────────────────── GPIO 26 (Pin 37)   │  → Zona 4 (Árboles)
│                      │          │                  │
└─────────────────────┘          └──────────────────┘
```

### Conexión Electroválvulas al Relé

```
┌──────────┐     ┌──────────────────┐     ┌──────────────┐
│  FUENTE  │     │  MÓDULO RELÉ     │     │ ELECTROVÁLV. │
│  24V AC  │     │                  │     │  SOLENOIDE   │
│          │     │                  │     │              │
│  L ──────────── COM (CH1) ───────────── Terminal 1    │
│          │     │  NC/NO (CH1) ───────── Terminal 2    │
│  N ──────────────────────────────────── (común)       │
└──────────┘     └──────────────────┘     └──────────────┘

⚠️  Usar NO (Normally Open) para que la válvula esté cerrada por defecto
⚠️  Repetir para cada canal (CH1-CH4 → Zonas 1-4)
```

### Tabla de relés

| Canal Relé | GPIO | Zona | Tipo de Riego |
|---|---|---|---|
| CH1 (IN1) | 16 | Zona 1 | Jardín - Goteo |
| CH2 (IN2) | 23 | Zona 2 | Huerta - Goteo |
| CH3 (IN3) | 24 | Zona 3 | Césped - Aspersores |
| CH4 (IN4) | 26 | Zona 4 | Árboles - Goteo |

---

## 🌡️ 2. Sensor DHT22 (Temperatura y Humedad)

El DHT22 es más preciso que el DHT11:
- **Temperatura**: -40°C a 80°C (±0.5°C)
- **Humedad**: 0-100% (±2-5%)
- **Frecuencia de lectura**: cada 2 segundos mínimo

### Conexión DHT22 ↔ Raspberry Pi

```
                    ┌─────────┐
                    │  DHT22  │
                    │ (vista  │
                    │ frontal)│
                    │         │
                    │ 1 2 3 4 │
                    └─┬─┬─┬─┬─┘
                      │ │ │ │
                      │ │ │ │
    3.3V (Pin 1) ─────┘ │ │ └───── GND (Pin 9)
                         │ │
    GPIO 4 (Pin 7) ──────┘ └────── NO CONECTAR
                         │
                    ┌────┴────┐
                    │  4.7kΩ  │  Resistencia pull-up
                    │         │  entre VCC y DATA
                    └────┬────┘
                         │
                    3.3V (Pin 1)
```

### Pinout detallado DHT22

| Pin DHT22 | Función | Conectar a RPi | Notas |
|---|---|---|---|
| Pin 1 (VCC) | Alimentación | 3.3V (Pin 1) | ⚡ Usar 3.3V, NO 5V |
| Pin 2 (DATA) | Datos | GPIO 4 (Pin 7) | Con resistencia 4.7kΩ pull-up a 3.3V |
| Pin 3 (NC) | No conectar | — | Dejar al aire |
| Pin 4 (GND) | Tierra | GND (Pin 9) | — |

> **⚠️ IMPORTANTE**: La resistencia pull-up de 4.7kΩ (o 10kΩ) es **obligatoria** entre VCC y DATA. Sin ella las lecturas serán erráticas.

---

## 📡 2b. Módulo LoRa EBYTE E220/E32 (UART)

Comunicación LoRa con ESP32 para control remoto de electroválvulas.

### Conexión EBYTE ↔ Raspberry Pi

```
┌──────────────────┐          ┌──────────────────┐
│  EBYTE E220/E32  │          │  RASPBERRY PI 4  │
│   LoRa Module    │          │                  │
│                  │          │                  │
│  VCC ───────────────────── 3.3V (Pin 1)       │
│  GND ───────────────────── GND  (Pin 6)       │
│  RXD ◄──────────────────── GPIO 14 (Pin 8)    │  RPi TXD → LoRa RXD
│  TXD ──────────────────── GPIO 15 (Pin 10)    │  LoRa TXD → RPi RXD
│  M0  ◄──────────────────── GPIO 5  (Pin 29)   │  Modo operación
│  M1  ◄──────────────────── GPIO 6  (Pin 31)   │  Modo operación
│  AUX ──────────────────── GPIO 13 (Pin 33)    │  Estado módulo
│                  │          │                  │
│  ANT ◄── Antena 868MHz    │                  │
└──────────────────┘          └──────────────────┘
```

### Modos de operación (M0/M1)

| M0 | M1 | Modo | Uso |
|---|---|---|---|
| LOW | LOW | **Normal** | Transmisión/Recepción UART transparente |
| HIGH | LOW | Wake-up | Despertar módulo remoto |
| LOW | HIGH | Power Save | Solo escucha, bajo consumo |
| HIGH | HIGH | **Sleep** | Configuración del módulo |

> **⚠️ IMPORTANTE**: 
> - Alimentar con **3.3V** (no 5V)
> - Habilitar UART en RPi: `sudo raspi-config` → Interface Options → Serial Port → No (login shell) → Yes (serial hardware)
> - El pin AUX indica cuando el módulo está ocupado (LOW = busy)

---

## 🗺️ 3. Diagrama General del Sistema

```
                                    ┌─────────────────────┐
                                    │   RASPBERRY PI 4B   │
                                    │                     │
              ┌─────────────────────┤ 3.3V (Pin 1)       │
              │  ┌──────────────────┤ 5V   (Pin 2, 4)    │
              │  │  ┌───────────────┤ GND  (Pin 6,9,14)  │
              │  │  │               │                     │
              │  │  │  ┌────────────┤ GPIO 4  (Pin 7)    │──── DHT22 (DATA)
              │  │  │  │  ┌─────────┤ GPIO 17 (Pin 11)   │──── Bomba Peristáltica
              │  │  │  │  │  ┌──────┤ GPIO 18 (Pin 12)   │──── Contador Fertilizante
              │  │  │  │  │  │      │                     │
              │  │  │  │  │  │  ┌───┤ GPIO 23 (Pin 16)   │──── Relé CH1 (Zona 1)
              │  │  │  │  │  │  │ ┌─┤ GPIO 24 (Pin 18)   │──── Relé CH2 (Zona 2)
              │  │  │  │  │  │  │ │┌┤ GPIO 25 (Pin 22)   │──── Relé CH3 (Zona 3)
              │  │  │  │  │  │  │ ││└┤GPIO 27 (Pin 13)   │──── Relé CH4 (Zona 4)
              │  │  │  │  │  │  │ ││ │                    │
              │  │  │  │  │  │  │ ││ └────────────────────┘
              │  │  │  │  │  │  │ ││
    ┌─────────┴──┴──┴──┘  │  │  │ │└─────────────────────────┐
    │  DHT22              │  │  │ │   MÓDULO RELÉ 4CH        │
    │  ┌───┐  4.7kΩ      │  │  │ │   ┌──┬──┬──┬──┐          │
    │  │   ├──/\/\/──3.3V │  │  │ │   │  │  │  │  │          │
    │  │   │              │  │  │ └───┤IN1│IN2│IN3│IN4│       │
    │  └───┘              │  │  │     │  │  │  │  │          │
    │                     │  │  │     │VCC│GND│  │  │         │
    │                     │  │  │     └──┴──┴──┴──┘          │
    │                     │  │  │       │   │                 │
    │                     │  │  │      5V  GND               │
    └─────────────────────┘  │  │                             │
                             │  │     ┌───────────────┐      │
                             │  │     │ ELECTROVÁLVULA│×4    │
                             │  │     │  SOLENOIDE    │      │
                             │  │     │  24V AC/DC    │      │
                             │  │     └───────────────┘      │
                             │  │                             │
                             │  │     ┌───────────────┐      │
                             │  └─────│BOMBA PERISTÁLT│      │
                             │        │  GPIO 17      │      │
                             │        └───────────────┘      │
                             │                                │
                             └────────────────────────────────┘
```

---

## 📌 4. Mapa de Pines Raspberry Pi (BCM)

```
                    ┌──────────┐
           3.3V  1 ─┤●        ●├─ 2   5V          ← Relé VCC
    (SDA)  GPIO2 3 ─┤○        ●├─ 4   5V
    (SCL)  GPIO3 5 ─┤○        ●├─ 6   GND         ← Relé GND / LoRa GND
  ★ DHT22  GPIO4 7 ─┤●        ●├─ 8   GPIO14 (TX) ← LoRa RXD
           GND   9 ─┤●        ●├─ 10  GPIO15 (RX) ← LoRa TXD
  ★ PUMP  GPIO17 11 ─┤●        ●├─ 12  GPIO18     ← Contador Fertiliz.
         GPIO27  13 ─┤○        ○├─ 14  GND
         GPIO22  15 ─┤○        ●├─ 16  GPIO23     ← Relé CH2 (Zona 2)
           3.3V  17 ─┤●        ●├─ 18  GPIO24     ← Relé CH3 (Zona 3)
    (MOSI)GPIO10 19 ─┤○        ○├─ 20  GND
    (MISO) GPIO9 21 ─┤○        ○├─ 22  GPIO25
    (SCLK)GPIO11 23 ─┤○        ○├─ 24  GPIO8 (CE0)
           GND   25 ─┤○        ○├─ 26  GPIO7 (CE1)
          GPIO0  27 ─┤○        ○├─ 28  GPIO1
  ★ LoRa M0 GPIO5 29 ─┤●      ○├─ 30  GND
  ★ LoRa M1 GPIO6 31 ─┤●      ○├─ 32  GPIO12
  ★ LoRa AUX GPIO13 33 ─┤●    ○├─ 34  GND
         GPIO19  35 ─┤○        ●├─ 36  GPIO16     ← Relé CH1 (Zona 1)
  ★ RELÉ4 GPIO26 37 ─┤●       ○├─ 38  GPIO20
           GND   39 ─┤○        ○├─ 40  GPIO21
                    └──────────┘
         ★ = Pines usados por el sistema
```

---

## ⚡ 5. Alimentación y Precauciones

### Alimentación

| Componente | Voltaje | Corriente típica | Notas |
|---|---|---|---|
| Raspberry Pi 4 | 5V / 3A | 1-2.5A | Fuente USB-C 5.1V 3A mínimo |
| Módulo Relé 4CH | 5V | 70-80mA/canal | Alimentar desde RPi 5V o fuente externa |
| DHT22 | 3.3V | ~1.5mA | Desde 3.3V del RPi |
| Bomba Peristáltica | 12V | 200-500mA | Fuente externa, controlar con relé |

### ⚠️ Precauciones

1. **DHT22**: 
   - **Obligatoria** resistencia pull-up de **4.7kΩ** entre DATA y VCC
   - Espera mínimo **2 segundos** entre lecturas
   - Usar **3.3V** (no 5V) en Raspberry Pi

2. **Relés**: 
   - Los relés se activan en **LOW** en algunos módulos (active-low). Verificar el tuyo.
   - Este sistema usa **HIGH = ON** (active-high)

3. **Electroválvulas**: 
   - Nunca conectar electroválvulas directamente al GPIO
   - Siempre usar relés como intermediarios
   - Incluir **diodo flyback** si no está en el módulo relé


---

## 🛠️ 6. Configuración Software

### Instalar librerías necesarias

```bash
# Instalar librerías
pip install adafruit-circuitpython-dht
```

### Archivos de configuración del proyecto

- **`app/config.py`** → Definición de pines GPIO
- **`app/gpio.py`** → Control de relés y bomba
- **`app/sensors/dht_reader.py`** → Lectura del DHT22
- **`scripts/health_check.py`** → Verificación de periféricos

### GPIOs libres disponibles

| GPIO | Pin Físico | Disponible para |
|---|---|---|
| GPIO 8 | Pin 24 | SPI CE0 / Sensor |
| GPIO 9 | Pin 21 | SPI MISO / Sensor |
| GPIO 10 | Pin 19 | SPI MOSI / Sensor |
| GPIO 11 | Pin 23 | SPI SCLK / Sensor |
| GPIO 12 | Pin 32 | PWM / Sensor |
| GPIO 19 | Pin 35 | Sensor adicional |
| GPIO 20 | Pin 38 | Sensor adicional |
| GPIO 21 | Pin 40 | Sensor adicional |
| GPIO 22 | Pin 15 | Sensor adicional |
| GPIO 25 | Pin 22 | Sensor adicional |
| GPIO 27 | Pin 13 | Sensor adicional |

---

## 📷 7. Lista de Materiales

| Componente | Cantidad | Descripción |
|---|---|---|
| Raspberry Pi 4B | 1 | Controlador principal |
| DHT22 | 1 | Sensor temperatura/humedad |
| Módulo Relé 4CH | 1 | Control de electroválvulas |
| EBYTE E220/E32 LoRa | 1 | Comunicación UART con ESP32 |
| Antena 868 MHz | 1 | Para módulo LoRa |
| Resistencia 4.7kΩ | 1 | Pull-up para DHT22 |
| Electroválvula solenoide | 4 | 24V AC, una por zona |
| Bomba peristáltica | 1 | Para fertilización |
| Cables Dupont | ~25 | Macho-Hembra y Hembra-Hembra |
| Fuente 5V 3A | 1 | Para Raspberry Pi |
| Fuente 24V | 1 | Para electroválvulas |

---

> **📝 Última actualización**: 2026-03-24  
> **🔧 Configurado por**: Sistema de Irrigación v4.0

