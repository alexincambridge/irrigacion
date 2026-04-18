# ESP32 LoRa Irrigation - Installation Checklist

Print this checklist and check off items as you complete them.

## Phase 1: Hardware Acquisition

### ESP32 Components
- [ ] ESP32 Development Board (any variant)
- [ ] RFM95/RFM96 LoRa module for ESP32
- [ ] Antenna for ESP32 LoRa (u.FL or SMA)
- [ ] 4-Channel Relay Module (5V)
- [ ] 4× Solenoid Valves (12V or 24V)
- [ ] 12V/24V Power Supply (5A minimum) for valves
- [ ] Buck Converter 12V→5V (3A minimum) OR separate 5V supply
- [ ] Micro USB cable for ESP32 programming

### Raspberry Pi Components
- [ ] RFM95/RFM96 LoRa module for RPI (same frequency as ESP32!)
- [ ] Antenna for RPI LoRa (u.FL or SMA)
- [ ] Female-Female jumper wires (at least 8)

### Additional Materials
- [ ] Male-Male jumper wires (at least 20)
- [ ] Breadboard (optional, for testing)
- [ ] Weatherproof enclosure(s)
- [ ] 18 AWG wire for valve connections
- [ ] 22 AWG wire for signal connections
- [ ] Flyback diodes 1N4007 (4 pieces)
- [ ] Fuses and fuse holders (2A and 5A)
- [ ] Heat shrink tubing
- [ ] Cable glands for enclosure
- [ ] Mounting hardware (screws, standoffs)
- [ ] Multimeter (for testing)
- [ ] Wire strippers and crimpers

## Phase 2: Software Installation

### Raspberry Pi
- [ ] Python 3 installed (should be already)
- [ ] SPI enabled (`sudo raspi-config` → Interface Options → SPI → Enable)
- [ ] Reboot after enabling SPI
- [ ] Git installed (`sudo apt-get install git`)
- [ ] Updated requirements.txt dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### ESP32 Development Environment
- [ ] Arduino IDE downloaded and installed
- [ ] ESP32 board support added to Arduino IDE:
  - [ ] Added board manager URL to preferences
  - [ ] Installed ESP32 boards from Board Manager
- [ ] LoRa library installed (by Sandeep Mistry)
- [ ] Correct ESP32 board selected in Tools → Board
- [ ] Serial Monitor tested (Tools → Serial Monitor, 115200 baud)

## Phase 3: Wiring - ESP32

### ESP32 to LoRa Module
- [ ] 3.3V connected to LoRa VCC
- [ ] GND connected to LoRa GND
- [ ] GPIO23 connected to LoRa MOSI
- [ ] GPIO19 connected to LoRa MISO
- [ ] GPIO18 connected to LoRa SCK
- [ ] GPIO5 connected to LoRa NSS
- [ ] GPIO14 connected to LoRa RST
- [ ] GPIO2 connected to LoRa DIO0
- [ ] Antenna connected to LoRa module
- [ ] **VERIFIED: Using 3.3V, NOT 5V!**

### ESP32 to Relay Module
- [ ] GPIO13 connected to Relay IN1
- [ ] GPIO12 connected to Relay IN2
- [ ] GPIO27 connected to Relay IN3
- [ ] GPIO26 connected to Relay IN4
- [ ] 5V connected to Relay VCC
- [ ] GND connected to Relay GND
- [ ] Relay module LED lights up when powered

### Relay Module to Solenoid Valves
- [ ] Valve 1: +12V/24V → Valve (+), Relay1 NO → Valve (-), Relay1 COM → GND
- [ ] Valve 2: +12V/24V → Valve (+), Relay2 NO → Valve (-), Relay2 COM → GND
- [ ] Valve 3: +12V/24V → Valve (+), Relay3 NO → Valve (-), Relay3 COM → GND
- [ ] Valve 4: +12V/24V → Valve (+), Relay4 NO → Valve (-), Relay4 COM → GND
- [ ] Flyback diode added to each valve (cathode to +)
- [ ] Fuses added to power lines
- [ ] All grounds connected together (common ground)

### Power Supply
- [ ] 12V/24V supply for solenoid valves
- [ ] Buck converter (12V→5V) for ESP32 and relay, OR separate 5V supply
- [ ] All power connections secure and insulated
- [ ] Polarity verified with multimeter before powering on

## Phase 4: Wiring - Raspberry Pi

### Raspberry Pi to LoRa Module
- [ ] Pin 1 (3.3V) to LoRa VCC
- [ ] Pin 6 (GND) to LoRa GND
- [ ] Pin 19 (GPIO10/MOSI) to LoRa MOSI
- [ ] Pin 21 (GPIO9/MISO) to LoRa MISO
- [ ] Pin 23 (GPIO11/SCK) to LoRa SCK
- [ ] Pin 24 (GPIO8/CE0) to LoRa NSS
- [ ] Pin 22 (GPIO25) to LoRa RST
- [ ] Pin 18 (GPIO24) to LoRa DIO0
- [ ] Antenna connected to LoRa module
- [ ] **VERIFIED: Using 3.3V, NOT 5V!**

## Phase 5: ESP32 Software Configuration

### Code Configuration
- [ ] Opened `ESP32/esp32_lora_irrigation.ino` in Arduino IDE
- [ ] Set frequency (line 14):
  - [ ] `915E6` for US/Americas/Australia
  - [ ] `868E6` for Europe/Asia/Africa
- [ ] Verified valve GPIO pins (lines 17-18) match your wiring
- [ ] Set unique device ID (line 21) if using multiple ESP32s
- [ ] Saved changes

### Upload and Test
- [ ] ESP32 connected to computer via USB
- [ ] Correct COM port selected (Tools → Port)
- [ ] Code compiled successfully (✓ button)
- [ ] Code uploaded successfully (→ button)
- [ ] Serial Monitor opened (115200 baud)
- [ ] Serial Monitor shows:
  ```
  ESP32 LoRa Irrigation Controller
  LoRa initialized successfully
  Frequency: 915.0 MHz (or 868.0)
  Waiting for commands...
  ```

## Phase 6: Raspberry Pi Software Configuration

### Configuration File
- [ ] Edited `app/config.py`
- [ ] Set `HARDWARE_MODE = 'LORA'`
- [ ] Set `LORA_FREQUENCY = 915E6` (or `868E6`) to match ESP32
- [ ] Saved changes

### Dependencies
- [ ] Installed Python LoRa library:
  ```bash
  pip install pyLoRa spidev
  ```
  OR
  ```bash
  cd ~
  git clone https://github.com/mayeranalytics/pySX127x.git
  cd pySX127x
  sudo python3 setup.py install
  ```

## Phase 7: Testing

### Pre-Power Test
- [ ] Visual inspection of all connections
- [ ] No short circuits visible
- [ ] All antennas connected
- [ ] Multimeter verification of voltages (before connecting devices)

### Power On Test
- [ ] ESP32 powered on
- [ ] ESP32 LED lit
- [ ] Relay module LED lit
- [ ] Serial Monitor shows initialization
- [ ] No smoke, burning smell, or unusual heat

### Communication Test
- [ ] ESP32 and RPI within 2 meters for initial test
- [ ] Ran test script on RPI:
  ```bash
  python3 scripts/test_lora.py
  ```
- [ ] Test results:
  - [ ] Test 1: Ping - PASS
  - [ ] Test 2: Status Query - PASS
  - [ ] Test 3: Valve Control - PASS
  - [ ] Test 4: Signal Quality - PASS
  - [ ] Test 5: Emergency Stop - PASS

### Signal Quality Check
- [ ] RSSI: _______ dBm (should be > -110 dBm)
- [ ] SNR: _______ dB
- [ ] Quality: _______ % (should be > 30%)

### Valve Test
- [ ] Valve 1: Relay clicks when turned on/off
- [ ] Valve 2: Relay clicks when turned on/off
- [ ] Valve 3: Relay clicks when turned on/off
- [ ] Valve 4: Relay clicks when turned on/off

### Auto-Shutoff Test
- [ ] Turned on valve 1 with 10-second timer
- [ ] Valve turned off automatically after ~10 seconds
- [ ] ESP32 Serial Monitor showed "AUTO_OFF:VALVE_1"

### Range Test (Optional)
- [ ] Tested at 10 meters: Signal Quality _______% 
- [ ] Tested at 50 meters: Signal Quality _______% 
- [ ] Tested at 100 meters: Signal Quality _______% 
- [ ] Tested at installation distance: Signal Quality _______% 
- [ ] Maximum reliable range: _______ meters

## Phase 8: Integration

### Web Application
- [ ] Started Flask app: `python run.py`
- [ ] Opened web interface in browser
- [ ] Tested valve control from web interface
- [ ] Hardware status endpoint working: `/hardware/status`
- [ ] Signal quality displayed correctly

### Scheduler Integration
- [ ] Scheduled irrigation tested
- [ ] Auto-shutoff timers working
- [ ] Database logging working

## Phase 9: Installation

### Enclosure
- [ ] ESP32, relay, and buck converter mounted in weatherproof enclosure
- [ ] LoRa module antenna positioned outside enclosure
- [ ] Cable glands installed for:
  - [ ] Power input
  - [ ] Valve wires (4×)
  - [ ] Antenna cable
- [ ] Enclosure sealed and waterproof tested
- [ ] Ventilation holes added (if needed, with waterproof vent)

### Mounting
- [ ] Enclosure mounted in final location
- [ ] Antenna positioned for best signal (vertical, high up)
- [ ] Power cables routed safely
- [ ] Valve connections weatherproofed

### Final Test at Installation Site
- [ ] Power on system at final location
- [ ] Test communication from RPI to ESP32
- [ ] Signal quality acceptable: RSSI _______ dBm, Quality _______% 
- [ ] Test each valve at installation site
- [ ] Verify water flow from each valve
- [ ] Test emergency stop

## Phase 10: Documentation

### Record Configuration
- [ ] Document final ESP32 pin assignments
- [ ] Document LoRa frequency used: _______ MHz
- [ ] Document ESP32 location
- [ ] Document valve locations (1, 2, 3, 4)
- [ ] Take photos of installation
- [ ] Create wiring diagram specific to your installation

### User Training
- [ ] Demonstrated web interface to users
- [ ] Explained emergency stop procedure
- [ ] Explained auto-shutoff feature
- [ ] Demonstrated manual valve control
- [ ] Provided contact for support

## Phase 11: Monitoring

### First Week
- [ ] Day 1: System operational, no issues
- [ ] Day 3: Check signal quality, log RSSI: _______
- [ ] Day 7: Full system test, all valves working

### First Month
- [ ] Week 2: System check
- [ ] Week 4: System check, review logs

### Maintenance Schedule Created
- [ ] Weekly: Check signal quality
- [ ] Monthly: Test all valves
- [ ] Quarterly: Inspect enclosure seal
- [ ] Annually: Replace batteries (if using battery power)

## Phase 12: Backup and Recovery

### Configuration Backup
- [ ] Backed up `app/config.py`
- [ ] Backed up ESP32 sketch
- [ ] Backed up database
- [ ] Documented all settings in notebook

### Recovery Procedure Documented
- [ ] How to restart RPI software
- [ ] How to restart ESP32
- [ ] How to manually control valves (bypass electronics)
- [ ] Emergency contact information posted

---

## Sign-Off

Installation completed by: ________________________

Date: _______________

Signature: ________________________

Verified by: ________________________

Date: _______________

Signature: ________________________

---

## Notes / Issues Encountered

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

________________________________________________________________________

---

## Post-Installation Support

If you encounter issues after installation:

1. Check troubleshooting section in `ESP32/SETUP_GUIDE.md`
2. Review ESP32 Serial Monitor for error messages
3. Run `python3 scripts/test_lora.py` to diagnose
4. Check signal quality at different times of day
5. Verify all power connections are secure

---

**System Status: [ ] OPERATIONAL [ ] TESTING [ ] ISSUES**

Last Updated: _______________

