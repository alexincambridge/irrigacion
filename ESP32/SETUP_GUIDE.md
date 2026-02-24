# LoRa Irrigation System - Complete Setup Guide

This guide will help you set up communication between your Raspberry Pi and ESP32 using LoRa to control 4 irrigation solenoid valves.

## 📋 Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Hardware Assembly](#hardware-assembly)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Usage](#usage)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Hardware Requirements

### Raspberry Pi Side
- Raspberry Pi (any model with GPIO)
- LoRa Module: RFM95/RFM96/SX1276 (915 MHz or 868 MHz)
- Jumper wires
- Optional: External antenna for better range

### ESP32 Side
- ESP32 Development Board
- LoRa Module: RFM95/RFM96/SX1276 (same frequency as RPI)
- 4-Channel Relay Module (active LOW or HIGH)
- 4 x Solenoid Valves (12V or 24V)
- Power Supply:
  - 12V/24V DC for solenoid valves
  - 5V DC for ESP32 and relay module
- Jumper wires
- Optional: External antenna for better range

### Additional Materials
- Weatherproof enclosures
- Power cables
- Water-resistant connectors
- Mounting hardware

---

## 🔌 Hardware Assembly

### Step 1: Raspberry Pi LoRa Module Connections

```
Raspberry Pi GPIO    →    LoRa Module
─────────────────────────────────────
Pin 1  (3.3V)       →    VCC
Pin 6  (GND)        →    GND
Pin 24 (GPIO8)      →    NSS (CS)
Pin 22 (GPIO25)     →    RST
Pin 18 (GPIO24)     →    DIO0
Pin 23 (GPIO11)     →    SCK
Pin 21 (GPIO9)      →    MISO
Pin 19 (GPIO10)     →    MOSI
```

**Important Notes:**
- Use 3.3V, NOT 5V for LoRa modules
- Keep wires as short as possible
- Connect antenna before powering on

### Step 2: ESP32 LoRa Module Connections

```
ESP32 Pin           →    LoRa Module
─────────────────────────────────────
3.3V                →    VCC
GND                 →    GND
GPIO5               →    NSS (CS)
GPIO14              →    RST
GPIO2               →    DIO0
GPIO18              →    SCK
GPIO19              →    MISO
GPIO23              →    MOSI
```

### Step 3: ESP32 Relay Module Connections

```
ESP32 Pin           →    Relay Module
─────────────────────────────────────
GPIO13              →    IN1 (Valve 1)
GPIO12              →    IN2 (Valve 2)
GPIO27              →    IN3 (Valve 3)
GPIO26              →    IN4 (Valve 4)
5V                  →    VCC
GND                 →    GND
```

### Step 4: Relay to Solenoid Valve Connections

For each valve:
```
Power Supply (+)  →  Valve (+)
Valve (-)         →  Relay NO (Normally Open)
Relay COM         →  Power Supply (-)
```

**Safety Tips:**
- Use appropriate wire gauge for current
- Add fuses for protection
- Ensure all connections are waterproof
- Test relays before connecting valves

---

## 💻 Software Installation

### Raspberry Pi Setup

#### 1. Enable SPI Interface
```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
# Reboot: sudo reboot
```

#### 2. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev git
```

#### 3. Install Python LoRa Library
```bash
# Install pyLoRa
cd ~
git clone https://github.com/mayeranalytics/pySX127x.git
cd pySX127x
sudo python3 setup.py install

# Or use pip (if available)
pip install pyLoRa
```

#### 4. Install Project Dependencies
```bash
cd /path/to/irrigacion
pip install -r requirements.txt
```

### ESP32 Setup

#### 1. Install Arduino IDE
Download from: https://www.arduino.cc/en/software

#### 2. Add ESP32 Board Support
1. Open Arduino IDE
2. Go to: File → Preferences
3. Add to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Go to: Tools → Board → Boards Manager
5. Search "ESP32" and install "ESP32 by Espressif Systems"

#### 3. Install LoRa Library
1. Go to: Sketch → Include Library → Manage Libraries
2. Search "LoRa" by Sandeep Mistry
3. Click Install

#### 4. Upload ESP32 Code
1. Open `ESP32/esp32_lora_irrigation.ino`
2. Select your ESP32 board: Tools → Board → ESP32 Arduino → (Your Board)
3. Select COM port: Tools → Port → (Your ESP32 Port)
4. Verify frequency setting in code (line 14):
   - `915E6` for US/Americas/Australia
   - `868E6` for Europe/Asia/Africa
5. Click Upload (→)

---

## ⚙️ Configuration

### Configure Raspberry Pi

Edit `app/config.py`:

```python
# Set hardware mode to LoRa
HARDWARE_MODE = 'LORA'  # Options: 'GPIO', 'LORA', 'SIMULATION'

# LoRa Frequency (MUST match ESP32)
LORA_FREQUENCY = 915E6  # or 868E6 for Europe

# Number of irrigation zones
NUM_ZONES = 4
```

### Configure ESP32

Edit `ESP32/esp32_lora_irrigation.ino`:

```cpp
// Line 14: Set frequency to match Raspberry Pi
#define LORA_FREQUENCY 915E6  // or 868E6

// Lines 17-18: Adjust relay pins if needed
const int VALVE_PINS[4] = {13, 12, 27, 26};

// Line 21: Set unique device ID
const String DEVICE_ID = "ESP32_IRR_001";
```

**Important:** Both devices MUST use the same frequency!

---

## 🧪 Testing

### Step 1: Test ESP32 Standalone

1. Open Arduino IDE Serial Monitor (115200 baud)
2. Power on ESP32
3. You should see:
   ```
   ESP32 LoRa Irrigation Controller
   ================================
   LoRa initialized successfully
   Frequency: 915.0 MHz
   
   Waiting for commands...
   ```

### Step 2: Test Raspberry Pi LoRa

Run the test script:
```bash
cd /path/to/irrigacion
python3 scripts/test_lora.py
```

Expected output:
```
✅ PASS  Ping
✅ PASS  Status Query
✅ PASS  Valve Control
✅ PASS  Signal Quality
✅ PASS  Emergency Stop

5/5 tests passed
```

### Step 3: Monitor ESP32 Serial Output

While running RPI test, watch ESP32 Serial Monitor for:
```
📡 Received: PING
   RSSI: -45 dBm, SNR: 9.5 dB
📤 Sent: PONG:ESP32_IRR_001

📡 Received: ON:1:5
✅ Valve 1 ON (auto-off in 5 seconds)
📤 Sent: OK:VALVE_1_ON
```

### Step 4: Test in Web Interface

1. Start Flask application:
   ```bash
   python run.py
   ```

2. Open browser: http://localhost:5000

3. Check hardware status:
   - Navigate to Settings or Dashboard
   - Look for "Hardware Status" widget
   - Should show: Connected, Signal Quality, etc.

---

## 🚀 Usage

### Python API

```python
from app.hardware_lora import zone_on, zone_off, get_all_zones_status

# Turn on zone 1 for 300 seconds (5 minutes)
zone_on(1, duration=300)

# Turn off zone 2
zone_off(2)

# Get status of all zones
status = get_all_zones_status()
# Returns: {1: True, 2: False, 3: False, 4: False}
```

### Web Interface

The existing web interface will automatically use LoRa when configured:

1. **Dashboard**: View system status and active zones
2. **Irrigation**: Control zones manually or schedule
3. **Settings**: Check LoRa connection and signal quality

### Command Line

Test individual commands:
```python
python3 -c "from app.lora_controller import get_lora_controller; \
            c = get_lora_controller(); \
            c.valve_on(1, 60); \
            import time; time.sleep(5); \
            c.get_status()"
```

---

## 🔍 Troubleshooting

### No Communication Between Devices

**Check Frequency Match:**
```python
# Raspberry Pi
grep LORA_FREQUENCY app/config.py

# ESP32 - check Serial Monitor output
# Should show: "Frequency: 915.0 MHz"
```

**Verify LoRa Module Connections:**
- Check all wire connections
- Ensure GND is connected
- Verify 3.3V power (NOT 5V!)
- Check antenna is connected

**Test SPI on Raspberry Pi:**
```bash
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1
```

### Poor Signal Quality (RSSI < -110 dBm)

**Improve Signal:**
- Add external antennas (increases range 5-10x)
- Reduce physical obstructions
- Move devices to higher locations
- Ensure antennas are oriented properly (vertical)

**Adjust LoRa Settings:**
```cpp
// In ESP32 code (around line 70):
LoRa.setSpreadingFactor(12);  // Try 10 or 11 for faster speed
```

### Valves Not Switching

**Check Relay Module:**
```python
# Test relay directly
from app.lora_controller import get_lora_controller
c = get_lora_controller()
c.valve_on(1)  # Listen for relay click
```

**Check Power:**
- Verify 12V/24V supply to solenoids
- Check fuses
- Test relay outputs with multimeter

**Verify Wiring:**
- COM and NO (Normally Open) should be used
- Ensure polarity is correct for solenoids

### ESP32 Not Responding

**Check Serial Monitor:**
- Open at 115200 baud
- Look for initialization messages
- Check for error messages

**Reset ESP32:**
- Press reset button
- Re-upload code if needed

**Verify Power:**
- Use good USB cable or external 5V supply
- Check current rating (500mA minimum)

### Auto-Off Not Working

**Verify Duration Parameter:**
```python
# Must specify duration > 0 for auto-off
zone_on(1, duration=300)  # 300 seconds = 5 minutes
```

**Check ESP32 Logs:**
- Should show: "auto-off in X seconds"
- Watch for "AUTO_OFF:VALVE_X" message

---

## 📊 Range Testing

To test range at your location:

```bash
# Terminal 1 - Run continuous status check
watch -n 5 "python3 -c 'from app.lora_controller import get_lora_controller; \
  c = get_lora_controller(); print(c.get_signal_quality())'"

# Terminal 2 - Watch ESP32 Serial Monitor
```

Walk away with ESP32 and note when:
- Signal quality drops below 50%
- Communication fails
- Mark maximum reliable range

---

## 🔒 Safety Features

The system includes several safety features:

1. **Auto-Off Timer**: Valves automatically turn off after specified duration
2. **Emergency Stop**: `ALL_OFF` command turns off all valves
3. **Connection Monitoring**: System detects lost communication
4. **Response Verification**: Commands confirmed before logging

### Add Watchdog (Recommended)

Create a watchdog script to ensure valves don't get stuck:

```python
# scripts/watchdog.py
from app.lora_controller import get_lora_controller
import time

controller = get_lora_controller()
MAX_RUNTIME = 3600  # 1 hour max

while True:
    status = controller.get_status()
    # Add logic to track valve runtime
    # Turn off if exceeded MAX_RUNTIME
    time.sleep(60)
```

---

## 📱 Next Steps

1. **Add Monitoring**: Log all valve operations to database
2. **Add Alerts**: Email/SMS when valves are on too long
3. **Add Scheduling**: Integrate with existing scheduler
4. **Add Sensors**: Connect soil moisture sensors to ESP32
5. **Add Web Dashboard**: Show real-time LoRa signal quality

---

## 📞 Support

If you encounter issues:

1. Check ESP32 Serial Monitor for errors
2. Run test script with verbose logging
3. Verify all connections with multimeter
4. Check LoRa frequency regulations in your country
5. Review wiring diagrams carefully

---

## 📝 Notes

- **LoRa vs WiFi**: LoRa has much longer range but slower data rate
- **Frequency Regulations**: Use 915 MHz in Americas, 868 MHz in Europe
- **Power Consumption**: ESP32 can run on battery with sleep modes
- **Expandability**: Can add more ESP32 nodes with different IDs

---

## ✅ Checklist

Before going live:

- [ ] Both devices use same frequency
- [ ] All antennas connected
- [ ] Test script passes all tests
- [ ] Relays click when commanded
- [ ] Solenoids physically tested
- [ ] Auto-off timer verified
- [ ] Emergency stop tested
- [ ] Range tested at installation site
- [ ] Weatherproof enclosures installed
- [ ] Power supplies stable
- [ ] Backup power considered

---

**Happy Irrigating! 💧🌱**

