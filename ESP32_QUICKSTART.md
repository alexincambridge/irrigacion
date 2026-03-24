# 🚀 ESP32 LoRa Irrigation System - Quick Start

## What Is This?

A complete system to control 4 irrigation solenoid valves wirelessly using LoRa communication between your Raspberry Pi and an ESP32. Range: up to 2km!

## 📂 Where to Start

All ESP32-related files are in the `ESP32/` folder:

1. **`ESP32/IMPLEMENTATION_SUMMARY.md`** - Start here! Complete overview of what's been created
2. **`ESP32/SETUP_GUIDE.md`** - Step-by-step installation instructions
3. **`ESP32/WIRING_DIAGRAMS.md`** - Detailed wiring schematics
4. **`ESP32/README.md`** - Quick reference guide
5. **`ESP32/esp32_lora_irrigation.ino`** - Arduino code to upload to ESP32

## 🎯 What You Need

### Hardware
- ESP32 Development Board
- RFM95/RFM96 LoRa module for ESP32 (915 MHz or 868 MHz)
- RFM95/RFM96 LoRa module for Raspberry Pi (same frequency)
- 4-Channel Relay Module
- 4× Solenoid Valves (12V or 24V)
- Power supplies
- Jumper wires

### Software
- Arduino IDE (for ESP32)
- Python 3 (already on your RPI)

## ⚡ Quick Setup (3 Steps)

### Step 1: Hardware
Connect everything following the diagrams in `ESP32/WIRING_DIAGRAMS.md`

### Step 2: Upload ESP32 Code
1. Open `ESP32/esp32_lora_irrigation.ino` in Arduino IDE
2. Set frequency to match your region (line 14):
   - `915E6` for Americas
   - `868E6` for Europe
3. Upload to ESP32

### Step 3: Configure Raspberry Pi
Edit `app/config.py`:
```python
HARDWARE_MODE = 'LORA'
LORA_FREQUENCY = 915E6  # Match ESP32
```

## 🧪 Test It

```bash
# Install dependencies
pip install -r requirements.txt

# Run test
python3 scripts/test_lora.py
```

If all 5 tests pass ✅, you're ready to go!

## 💻 Use It

```python
from app.hardware_lora import zone_on, zone_off

# Turn on valve 1 for 5 minutes (auto-shutoff)
zone_on(1, duration=300)

# Turn off valve 2
zone_off(2)
```

Your existing web interface will automatically use LoRa!

## 📚 Full Documentation

- **Complete Guide**: `ESP32/SETUP_GUIDE.md`
- **Wiring Help**: `ESP32/WIRING_DIAGRAMS.md`
- **Full Overview**: `ESP32/IMPLEMENTATION_SUMMARY.md`

## 🆘 Having Issues?

1. Check that both devices use the **same frequency** (915 MHz or 868 MHz)
2. Verify all wiring connections
3. Ensure SPI is enabled on RPI: `sudo raspi-config` → Interface Options → SPI → Enable
4. Check antennas are connected
5. Read troubleshooting sections in documentation

## 🎉 What's Included

✅ ESP32 Arduino firmware  
✅ Raspberry Pi LoRa driver  
✅ Hardware abstraction layer  
✅ Complete documentation  
✅ Wiring diagrams  
✅ Test suite  
✅ Integration examples  
✅ Auto-shutoff timers  
✅ Signal quality monitoring  
✅ Emergency stop  

## 🌟 Key Features

- **Long Range**: Up to 2km line-of-sight
- **Low Power**: Can run on battery
- **Safe**: Auto-shutoff prevents stuck valves
- **Reliable**: Command acknowledgment and retry logic
- **Easy**: Drop-in replacement for GPIO control

---

**Start here**: `ESP32/IMPLEMENTATION_SUMMARY.md`

**Need help?**: Check the troubleshooting sections

**Ready to install?**: Follow `ESP32/SETUP_GUIDE.md`

Happy irrigating! 💧🌱

