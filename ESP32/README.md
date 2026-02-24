# ESP32 LoRa Irrigation System

## Hardware Requirements

### ESP32 Module
- ESP32 Development Board (any variant)
- LoRa Module: SX1276/RFM95/RFM96 (915 MHz for Americas, 868 MHz for Europe)
- 4-Channel Relay Module (5V or 3.3V compatible)
- 4 Solenoid Valves (12V/24V depending on your system)
- Power Supply (12V/24V for solenoids, 5V for ESP32)

### Raspberry Pi Module
- Raspberry Pi (any model)
- LoRa Module: SX1276/RFM95/RFM96 (same frequency as ESP32)

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

