# ESP32 LoRa Irrigation Control System

## 🎯 Project Overview

This system enables wireless control of 4 irrigation solenoid valves using LoRa communication between a Raspberry Pi and ESP32. It provides long-range (up to 2km), low-power wireless control that's perfect for remote irrigation installations.

## 📁 Files in This Directory

### Arduino Code
- **`esp32_lora_irrigation.ino`** - Main ESP32 sketch for valve control

### Documentation
- **`README.md`** - This file (quick reference)
- **`SETUP_GUIDE.md`** - Complete step-by-step setup instructions
- **`WIRING_DIAGRAMS.md`** - Detailed wiring schematics and pin connections

### Python Integration
- **`integration_example.py`** - Example code showing how to integrate with Flask app

## 🚀 Quick Start

### 1. Hardware Setup
1. Connect LoRa module to ESP32 (see WIRING_DIAGRAMS.md)
2. Connect relay module to ESP32
3. Connect solenoid valves to relay module
4. Connect LoRa module to Raspberry Pi

### 2. Upload ESP32 Code
```bash
# Using Arduino IDE:
# 1. Open esp32_lora_irrigation.ino
# 2. Select Board: Tools → Board → ESP32 Dev Module
# 3. Set frequency (915MHz or 868MHz) in code
# 4. Upload
```

### 3. Install RPI Dependencies
```bash
cd /path/to/irrigacion
pip install -r requirements.txt
```

### 4. Configure System
Edit `app/config.py`:
```python
HARDWARE_MODE = 'LORA'  # Enable LoRa mode
LORA_FREQUENCY = 915E6  # Must match ESP32
```

### 5. Test Communication
```bash
python3 scripts/test_lora.py
```

## 🔧 Hardware Requirements

### ESP32 Side
- ESP32 Dev Board
- RFM95/RFM96 LoRa module (915MHz or 868MHz)
- 4-Channel Relay Module
- 4× Solenoid Valves (12V/24V)
- Power supplies (12V for valves, 5V for ESP32)

### Raspberry Pi Side  
- Raspberry Pi (any model)
- RFM95/RFM96 LoRa module (same frequency as ESP32)
- Antenna (recommended for both sides)

## 📡 Communication Protocol

### Commands (RPI → ESP32)
```
ON:valve:duration   - Turn on valve (e.g., "ON:1:300" = valve 1 for 5 min)
OFF:valve          - Turn off valve (e.g., "OFF:1")
ALL_OFF            - Turn off all valves
STATUS             - Get status of all valves
PING               - Check if ESP32 is alive
```

### Responses (ESP32 → RPI)
```
OK:VALVE_X_ON      - Valve turned on successfully
OK:VALVE_X_OFF     - Valve turned off successfully
STATUS:1=ON,2=OFF  - Current valve states
PONG:device_id     - Response to ping
ERROR:message      - Command failed
```

## 💻 Python Usage

### Basic Control
```python
from app.hardware_lora import zone_on, zone_off, get_all_zones_status

# Turn on valve 1 for 5 minutes (auto-shutoff)
zone_on(1, duration=300)

# Turn off valve 2
zone_off(2)

# Get status of all valves
status = get_all_zones_status()
# Returns: {1: True, 2: False, 3: False, 4: False}
```

### Check Connection
```python
from app.hardware_lora import check_connection
from app.lora_controller import get_lora_controller

# Check if ESP32 is responding
if check_connection():
    print("ESP32 is online")

# Get signal quality
lora = get_lora_controller()
quality = lora.get_signal_quality()
print(f"Signal: {quality['rssi']} dBm, Quality: {quality['quality']}%")
```

## 🔍 Testing

### Test LoRa Communication
```bash
# Run comprehensive test suite
python3 scripts/test_lora.py

# Monitor ESP32 Serial (Arduino IDE)
# Tools → Serial Monitor (115200 baud)
```

## 🛠️ Troubleshooting

### No Communication
1. Check both devices use same frequency (915MHz or 868MHz)
2. Verify LoRa module connections
3. Ensure SPI is enabled on RPI: `sudo raspi-config`
4. Check antenna connections

### Poor Signal
1. Add external antennas (improves range 5-10x)
2. Check for physical obstructions
3. Verify RSSI: should be > -110 dBm

### Valves Not Working
1. Check relay module power (5V)
2. Verify solenoid power (12V/24V)
3. Test relays manually (should click)
4. Check GPIO pin assignments

## 📏 Range Expectations

| Environment | Expected Range |
|-------------|---------------|
| Clear line-of-sight | 1-2 km |
| Urban/Suburban | 500-1000 m |
| Indoor | 100-300 m |
| Through walls | 50-100 m |

**Tip:** Use external antennas for best range!

## ✅ Pre-Installation Checklist

Before deploying to field:

- [ ] Both devices use same frequency
- [ ] All tests pass (test_lora.py)
- [ ] Relays click when activated
- [ ] Solenoids physically tested
- [ ] Auto-shutoff timer verified
- [ ] Emergency stop tested
- [ ] Range tested at site
- [ ] Antennas properly connected
- [ ] Weatherproof enclosures ready
- [ ] Power supplies tested

---

**Ready to get started?** → Read `SETUP_GUIDE.md` for detailed instructions!

**Need wiring help?** → Check `WIRING_DIAGRAMS.md` for schematics!

**Want to test?** → Run `python3 scripts/test_lora.py`!

💧 Happy irrigating! 🌱

---

## Wiring Diagram

### ESP32 LoRa Module Connections
```
ESP32        LoRa Module
-----        -----------
3.3V   --->  VCC
GND    --->  GND
GPIO5  --->  NSS (CS)
GPIO14 --->  RST
GPIO2  --->  DIO0
GPIO18 --->  SCK
GPIO19 --->  MISO
GPIO23 --->  MOSI
```

### ESP32 Relay Module Connections
```
ESP32        Relay Module
-----        ------------
GPIO13 --->  IN1 (Valve 1)
GPIO12 --->  IN2 (Valve 2)
GPIO27 --->  IN3 (Valve 3)
GPIO26 --->  IN4 (Valve 4)
5V     --->  VCC
GND    --->  GND
```

### Raspberry Pi LoRa Module Connections
```
Raspberry Pi    LoRa Module
------------    -----------
3.3V      --->  VCC
GND       --->  GND
GPIO8     --->  NSS (CE0)
GPIO25    --->  RST
GPIO24    --->  DIO0
GPIO11    --->  SCK
GPIO9     --->  MISO
GPIO10    --->  MOSI
```

## Software Setup

### ESP32 Setup

1. Install Arduino IDE
2. Add ESP32 board support:
   - File → Preferences → Additional Board Manager URLs
   - Add: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
3. Install ESP32 boards: Tools → Board → Boards Manager → Search "ESP32" → Install
4. Install LoRa library: Sketch → Include Library → Manage Libraries → Search "LoRa" by Sandeep Mistry → Install
5. Select your ESP32 board: Tools → Board → ESP32 Arduino → Select your model
6. Upload the `esp32_lora_irrigation.ino` sketch

### Raspberry Pi Setup

1. Enable SPI:
   ```bash
   sudo raspi-config
   # Interface Options → SPI → Enable
   ```

2. Install Python dependencies:
   ```bash
   pip install pyLoRa RPi.GPIO
   ```

3. Run the LoRa communication module (see `app/lora_controller.py`)

## LoRa Configuration

Both devices must use the same settings:
- **Frequency**: 915 MHz (US/Americas) or 868 MHz (Europe/Asia)
- **Spreading Factor**: 12 (longer range, slower speed)
- **Bandwidth**: 125 kHz
- **Coding Rate**: 4/5
- **TX Power**: 20 dBm (maximum)

## Command Protocol

### Commands from Raspberry Pi to ESP32

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| Turn On Valve | `ON:valve:duration` | Turn on specific valve with optional duration (seconds) | `ON:1:300` (valve 1 for 5 min) |
| Turn Off Valve | `OFF:valve` | Turn off specific valve | `OFF:1` |
| All Off | `ALL_OFF` | Turn off all valves | `ALL_OFF` |
| Status | `STATUS` | Get status of all valves | `STATUS` |
| Ping | `PING` | Check if ESP32 is alive | `PING` |

### Responses from ESP32 to Raspberry Pi

| Response | Format | Description | Example |
|----------|--------|-------------|---------|
| Success | `OK:action` | Command executed successfully | `OK:VALVE_1_ON` |
| Error | `ERROR:message` | Command failed | `ERROR:INVALID_COMMAND` |
| Status | `STATUS:states` | Current valve states | `STATUS:1=ON,2=OFF,3=OFF,4=OFF` |
| Auto-off | `AUTO_OFF:valve` | Valve turned off automatically | `AUTO_OFF:VALVE_1` |
| Pong | `PONG:device_id` | Response to ping | `PONG:ESP32_IRR_001` |

## Testing

### Test ESP32
1. Open Serial Monitor (115200 baud)
2. Power on ESP32
3. Should see: "LoRa initialized successfully"

### Test Communication
1. Run the Raspberry Pi test script
2. Send commands from RPI
3. Verify responses on both Serial Monitor and RPI console

## Troubleshooting

### No LoRa Communication
- Check all wiring connections
- Verify both devices use same frequency
- Check antenna connections
- Verify SPI is enabled on Raspberry Pi

### Valves Not Working
- Check relay module power supply
- Test relays with multimeter
- Verify GPIO pin assignments
- Check solenoid valve power supply

### Poor Range
- Add external antennas
- Reduce spreading factor (trade range for speed)
- Check for physical obstructions
- Verify TX power settings

## Safety Notes

- Always include a duration parameter for automatic shutoff
- Implement watchdog timer to prevent valve stuck open
- Add manual override switch on solenoid valves
- Monitor for communication failures
- Log all operations for debugging

## Range Expectations

With optimal settings:
- **Clear line of sight**: Up to 2 km
- **Urban environment**: 500-1000 m
- **Indoor**: 100-300 m
- **Through walls**: 50-100 m

Factors affecting range:
- Antenna quality
- Physical obstructions
- Interference from other devices
- Weather conditions


