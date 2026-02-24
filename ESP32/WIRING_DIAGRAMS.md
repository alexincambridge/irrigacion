# ESP32 + LoRa + 4 Solenoid Valves - Wiring Diagrams

## Complete System Overview

```
┌─────────────────┐                LoRa Radio              ┌─────────────────┐
│  Raspberry Pi   │◄─────────── (915/868 MHz) ────────────►│     ESP32       │
│   + LoRa RFM95  │                                         │   + LoRa RFM95  │
└─────────────────┘                                         └────────┬────────┘
                                                                     │
                                                            ┌────────▼────────┐
                                                            │  4-CH Relay     │
                                                            │     Module      │
                                                            └─┬──┬──┬──┬─────┘
                                                              │  │  │  │
                                        ┌─────────────────────┘  │  │  └─────────────────────┐
                                        │                        │  │                        │
                                   ┌────▼────┐            ┌─────▼──▼─────┐            ┌─────▼─────┐
                                   │ Valve 1 │            │ Valve 2 & 3  │            │  Valve 4  │
                                   │12V/24V  │            │   12V/24V    │            │  12V/24V  │
                                   └─────────┘            └──────────────┘            └───────────┘
```

---

## 1. Raspberry Pi to LoRa Module

### Pin Connections

```
    Raspberry Pi                          RFM95/RFM96
    GPIO Header                           LoRa Module
    
     ┌─────┐                               ┌────────┐
     │  ●  │ 1  - 3.3V  ────────────────► │  VCC   │
     │  ●  │ 2  - 5V                       │        │
     │  ○  │ 3                             │  GND   │◄─┐
     │  ○  │ 4  - 5V                       │        │  │
     │  ○  │ 5                             │  MISO  │◄─┤
     │  ●  │ 6  - GND  ──────────────────► │        │  │
     │  ○  │ 7                             │  MOSI  │◄─┤
     │  ○  │ 8                             │        │  │
     │  ○  │ 9  - MISO  ──────────────────► │  SCK   │◄─┤
     │  ○  │ 10 - MOSI  ──────────────────► │        │  │
     │  ○  │ 11 - SCK   ──────────────────► │  NSS   │◄─┤
     │  ○  │ 12                             │        │  │
     │  ○  │ 13                             │  RST   │◄─┤
     │  ○  │ 14 - GND                       │        │  │
     │  ○  │ 15                             │  DIO0  │◄─┘
     │  ○  │ 16                             └────────┘
     │  ○  │ 17 - 3.3V                       
     │  ○  │ 18 - GPIO24 ──► DIO0           Connection Legend:
     │  ○  │ 19 - MOSI                      ────►  Wire connection
     │  ○  │ 20 - GND                       ●  Connected pin
     │  ○  │ 21 - MISO                      ○  Unused pin
     │  ○  │ 22 - GPIO25 ──► RST
     │  ○  │ 23 - SCK
     │  ○  │ 24 - GPIO8  ──► NSS
     │  ○  │ 25 - GND
     └─────┘
```

### Connection Table

| Raspberry Pi Pin | Function | RFM95 Pin |
|-----------------|----------|-----------|
| Pin 1 (3.3V)    | Power    | VCC       |
| Pin 6 (GND)     | Ground   | GND       |
| Pin 19 (GPIO10) | MOSI     | MOSI      |
| Pin 21 (GPIO9)  | MISO     | MISO      |
| Pin 23 (GPIO11) | SCK      | SCK       |
| Pin 24 (GPIO8)  | CS/NSS   | NSS       |
| Pin 22 (GPIO25) | Reset    | RST       |
| Pin 18 (GPIO24) | Interrupt| DIO0      |

---

## 2. ESP32 to LoRa Module

### VSPI Connections

```
        ESP32 DevKit                      RFM95/RFM96
        
     ┌───────────────┐                   ┌────────┐
     │ USB           │                   │        │
     │               │                   │  VCC   │◄─── 3.3V
     │           3V3 │─────────────────► │        │
     │           GND │─────────────────► │  GND   │
     │               │                   │        │
     │          IO23 │─────────────────► │  MOSI  │
     │          IO19 │─────────────────► │  MISO  │
     │          IO18 │─────────────────► │  SCK   │
     │          IO5  │─────────────────► │  NSS   │
     │          IO14 │─────────────────► │  RST   │
     │          IO2  │─────────────────► │  DIO0  │
     │               │                   │        │
     │          IO13 │──► Relay 1        │  ANT   │◄─── Antenna
     │          IO12 │──► Relay 2        └────────┘
     │          IO27 │──► Relay 3
     │          IO26 │──► Relay 4
     │               │
     │           5V  │──► Relay Module VCC
     │           GND │──► Relay Module GND
     └───────────────┘
```

### Connection Table

| ESP32 Pin | Function      | Connects To    |
|-----------|---------------|----------------|
| 3.3V      | Power         | LoRa VCC       |
| GND       | Ground        | LoRa GND       |
| GPIO23    | MOSI          | LoRa MOSI      |
| GPIO19    | MISO          | LoRa MISO      |
| GPIO18    | SCK           | LoRa SCK       |
| GPIO5     | CS/NSS        | LoRa NSS       |
| GPIO14    | Reset         | LoRa RST       |
| GPIO2     | Interrupt     | LoRa DIO0      |
| GPIO13    | Relay Control | Relay IN1      |
| GPIO12    | Relay Control | Relay IN2      |
| GPIO27    | Relay Control | Relay IN3      |
| GPIO26    | Relay Control | Relay IN4      |
| 5V        | Relay Power   | Relay VCC      |
| GND       | Common Ground | Relay GND      |

---

## 3. Relay Module to Solenoid Valves

### Power Distribution

```
                12V/24V DC Power Supply
                         │
         ┌───────────────┴───────────────┐
         │                               │
         │  (+) Positive                 │  (-) Negative
         │                               │
         ▼                               │
    ┌────────┐                          │
    │Valve 1 │(+)                       │
    │Solenoid│                          │
    │   12V  │(-)                       │
    └────┬───┘                          │
         │                               │
         │       ┌──────────────┐        │
         └──────►│ Relay 1  NO  │        │
                 │          COM │◄───────┘
                 │              │
                 │ Relay 2  NO  │◄─── Similar for Valve 2
                 │          COM │
                 │              │
                 │ Relay 3  NO  │◄─── Similar for Valve 3
                 │          COM │
                 │              │
                 │ Relay 4  NO  │◄─── Similar for Valve 4
                 │          COM │
                 └──────────────┘
                         ▲
                    Control from ESP32
```

### Single Valve Wiring Detail

```
   Power Supply          Relay Module              Solenoid Valve
   
      (+12V)                  ┌─────┐                   ┌────┐
        │                     │ NO  │──────────────────►│ +  │
        └────────────────────►│     │                   │    │
                              │ COM │◄──┐               │ -  │
      (-GND)                  └─────┘   │               └──┬─┘
        │                               │                  │
        └───────────────────────────────┴──────────────────┘
                                        
   NO  = Normally Open (used for valves)
   COM = Common (connects to ground)
   NC  = Normally Closed (not used)
```

### For 4 Valves

| Relay | ESP32 Control | Valve Connection           |
|-------|---------------|----------------------------|
| 1     | GPIO13 → IN1  | Valve 1: +12V → NO, COM → GND |
| 2     | GPIO12 → IN2  | Valve 2: +12V → NO, COM → GND |
| 3     | GPIO27 → IN3  | Valve 3: +12V → NO, COM → GND |
| 4     | GPIO26 → IN4  | Valve 4: +12V → NO, COM → GND |

---

## 4. Power Supply Wiring

### Option A: Single Power Supply (Recommended)

```
   ┌──────────────────────────┐
   │  12V/24V DC Power Supply │
   │    (5A minimum)          │
   └────┬──────────────────┬──┘
        │                  │
      (+12V)             (GND)
        │                  │
        ├──────────────────┼─────► Solenoid Valves (via relays)
        │                  │
   ┌────▼──────────────────▼────┐
   │  12V to 5V Buck Converter  │
   │     (3A minimum)            │
   └────┬──────────────────┬────┘
        │                  │
      (+5V)              (GND)
        │                  │
        ├──────────────────┼─────► ESP32 (VIN + GND)
        └──────────────────┴─────► Relay Module (VCC + GND)
```

### Option B: Separate Power Supplies

```
   ┌────────────────┐         ┌────────────────┐
   │ 12V/24V Supply │         │   5V Supply    │
   │  (for valves)  │         │ (for ESP32)    │
   └───┬────────┬───┘         └───┬────────┬───┘
       │        │                 │        │
     (+12V)   (GND)             (+5V)    (GND)
       │        │                 │        │
       │        │                 ├────────┼─────► ESP32
       │        │                 └────────┴─────► Relay Module
       │        │
       └────────┴─────────► Solenoid Valves (via relays)
       
   ⚠️  IMPORTANT: Connect all GND together (common ground)
```

---

## 5. Complete System Wiring

### Full Schematic

```
                        RASPBERRY PI + LORA
                        ┌──────────────────┐
                        │   RPI GPIO       │
                        │   ┌────────┐     │
                        │   │ RFM95  │     │
                        │   │  LoRa  │     │
                        │   └───┬────┘     │
                        └───────┼──────────┘
                                │ Antenna
                                │
                         ~ ~ ~ LoRa Radio ~ ~ ~
                                │
                        ┌───────┼──────────┐
                        │   ┌───▼────┐     │
                        │   │ RFM95  │     │
                        │   │  LoRa  │     │
                        │   └───┬────┘     │
                        │   ESP32 DEVKIT   │
                        │   ┌───▼─────┐    │
                        │   │GPIO Pins│    │
                        │   │13,12,27,│    │
                        │   │   26    │    │
                        │   └───┬─────┘    │
                        └───────┼──────────┘
                                │
                        ┌───────▼──────────┐
                        │  4-CH RELAY      │
                        │  MODULE          │
                        │ IN1 IN2 IN3 IN4  │
                        └─┬───┬───┬───┬───┘
                          │   │   │   │
    ┌─────────────────────┘   │   │   └──────────────────┐
    │                         │   │                      │
┌───▼───┐               ┌─────▼───▼─────┐           ┌───▼───┐
│Valve 1│               │ Valve 2 & 3   │           │Valve 4│
│ 12V   │               │     12V       │           │  12V  │
└───┬───┘               └─────┬───┬─────┘           └───┬───┘
    │                         │   │                     │
    └─────────────────────────┴───┴─────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  12V Power Supply  │
                    └────────────────────┘
```

---

## 6. Antenna Connections

### LoRa Antenna Options

```
Option 1: Wire Antenna (DIY)
┌────────┐
│ LoRa   │
│ Module │
│  ANT───┼─────► 8.2 cm wire (for 915 MHz)
└────────┘      or 8.6 cm wire (for 868 MHz)


Option 2: SMA Antenna
┌────────┐      ┌──────────┐
│ LoRa   │      │  SMA     │      Flexible
│ Module │      │ Connector│      Antenna
│  ANT───┼──────┤          ├──────────○
└────────┘      └──────────┘


Option 3: PCB Antenna (some modules have built-in)
┌────────────┐
│ LoRa Module│
│            │
│   ◠◡◠◡◠   │ ◄── PCB Antenna
│            │
└────────────┘
```

### Wire Antenna Lengths

| Frequency | Quarter Wave Length |
|-----------|---------------------|
| 868 MHz   | 8.6 cm             |
| 915 MHz   | 8.2 cm             |
| 433 MHz   | 17.3 cm            |

---

## 7. Protection Circuits (Recommended)

### Flyback Diodes for Solenoids

```
   Each Solenoid Valve should have a flyback diode:
   
        Relay NO
           │
           ▼
      ┌────────┐
   ┌──┤ Diode  ├──┐  ◄── 1N4007 or similar
   │  └────────┘  │      (Cathode to +)
   │  ┌────────┐  │
   └──┤Solenoid├──┘
      │ Valve  │
      └────────┘
```

### Fuses

```
   Power Supply → [FUSE 5A] → Solenoid Valves
   Power Supply → [FUSE 2A] → ESP32 + Relay Module
```

---

## 8. Weatherproofing

### Outdoor Installation

```
    Weatherproof Enclosure
    ┌────────────────────────┐
    │  ┌──────────┐          │
    │  │  ESP32   │          │
    │  └──────────┘          │
    │  ┌──────────┐          │
    │  │  LoRa    │          │
    │  └──────────┘          │
    │  ┌──────────┐          │
    │  │  Relay   │          │
    │  └──────────┘          │
    │  ┌──────────┐          │
    │  │ 12V→5V   │          │
    │  │ Buck Conv│          │
    │  └──────────┘          │
    │                        │
    │  Cable Glands:         │
    │  ○ Power In            │
    │  ○ Antenna Out         │
    │  ○ Valve Cables (4x)   │
    └────────────────────────┘
```

---

## 9. Testing Setup

### Bench Test Configuration

```
   ┌────────────┐      ┌────────────┐
   │    RPI     │      │   ESP32    │
   │  + LoRa    │      │  + LoRa    │
   └─────┬──────┘      └──────┬─────┘
         │                    │
    Antenna (20cm)       Antenna (20cm)
         │                    │
         └────── < 2m ────────┘
         
   For testing, keep devices close together.
   Use low TX power to avoid interference.
```

---

## 10. Troubleshooting Checklist

### Visual Inspection

- [ ] All LoRa pins connected correctly
- [ ] 3.3V to LoRa modules (NOT 5V!)
- [ ] Antennas connected
- [ ] Relay module powered (LED should be on)
- [ ] ESP32 powered (LED should be on)
- [ ] No short circuits
- [ ] All grounds connected together

### Multimeter Checks

- [ ] 3.3V present at LoRa VCC
- [ ] 5V present at ESP32 VIN
- [ ] 5V present at Relay VCC
- [ ] 12V/24V present at solenoid (+)
- [ ] Continuity on all GND connections
- [ ] Relay outputs click when activated

---

## Safety Warnings

⚠️  **IMPORTANT SAFETY NOTES:**

1. Never connect 5V to LoRa modules - they are 3.3V only!
2. Connect all grounds together (common ground)
3. Add fuses to all power lines
4. Use appropriate wire gauge for current
5. Insulate all connections properly
6. Keep water away from electronics
7. Use weatherproof enclosures for outdoor installation
8. Test thoroughly before permanent installation
9. Add flyback diodes to solenoid valves
10. Never work on powered circuits

---

## Bill of Materials

### Raspberry Pi Side
- 1x Raspberry Pi (any model)
- 1x RFM95/RFM96 LoRa module (915 or 868 MHz)
- 1x Antenna (u.FL or SMA)
- 8x Female-Female jumper wires
- 1x Power supply for RPI

### ESP32 Side
- 1x ESP32 Development Board
- 1x RFM95/RFM96 LoRa module (same frequency as RPI)
- 1x 4-Channel Relay Module
- 4x Solenoid Valves (12V or 24V)
- 1x 12V/24V Power Supply (5A minimum)
- 1x Buck Converter (12V to 5V, 3A minimum)
- 1x Antenna (u.FL or SMA)
- 20x Jumper wires (various)
- 4x Flyback diodes (1N4007)
- 2x Fuses + holders
- 1x Weatherproof enclosure
- Wire (18 AWG for valves, 22 AWG for signals)

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-24  
**Created for:** Irrigation Control System

