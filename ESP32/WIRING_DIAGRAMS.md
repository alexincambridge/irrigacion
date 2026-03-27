# ESP32 + LoRa EBYTE UART + 4 Solenoid Valves - Wiring Diagrams

## Complete System Overview

```
┌─────────────────┐                LoRa Radio              ┌─────────────────┐
│  Raspberry Pi   │◄─────────── (868 MHz EU) ─────────────►│     ESP32       │
│ + LoRa EBYTE    │            EBYTE E220/E32              │  + LoRa EBYTE   │
│   (UART)        │                                         │    (UART)       │
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

## 1. Raspberry Pi to LoRa EBYTE Module (UART)

### Pin Connections

```
    Raspberry Pi                        EBYTE E220/E32
    GPIO Header                         LoRa Module
    
     ┌─────┐                             ┌──────────┐
     │  ●  │ 1  - 3.3V ────────────────► │   VCC    │
     │  ○  │ 2  - 5V                     │          │
     │  ○  │ 3                           │   GND    │◄──┐
     │  ○  │ 4                           │          │   │
     │  ○  │ 5                           │   RXD    │◄──┤── GPIO 14 (TXD)
     │  ●  │ 6  - GND ─────────────────► │          │   │
     │  ○  │ 7                           │   TXD    │───┤── GPIO 15 (RXD)
     │  ●  │ 8  - GPIO14 (TXD) ────────► │          │   │
     │  ○  │ 9                           │   AUX    │───┤── GPIO 13
     │  ●  │ 10 - GPIO15 (RXD) ◄──────── │          │   │
     │  ○  │ 11                           │   M0     │───┤── GPIO 5
     │  ○  │ 12                           │          │   │
     │  ○  │ 13                           │   M1     │───┤── GPIO 6
     │  ○  │ 14                           │          │   │
     │  ○  │ ...                          │  ANT     │◄─── Antenna
     │  ○  │ 29 - GPIO5  ──► M0          └──────────┘
     │  ○  │ 31 - GPIO6  ──► M1
     │  ○  │ 33 - GPIO13 ◄── AUX
     └─────┘
```

### Connection Table

| Raspberry Pi Pin | GPIO (BCM) | Function    | EBYTE Pin |
|------------------|-----------|-------------|-----------|
| Pin 1 (3.3V)     | —         | Power       | VCC       |
| Pin 6 (GND)      | —         | Ground      | GND       |
| Pin 8             | GPIO 14   | UART TX     | RXD       |
| Pin 10            | GPIO 15   | UART RX     | TXD       |
| Pin 29            | GPIO 5    | Mode M0     | M0        |
| Pin 31            | GPIO 6    | Mode M1     | M1        |
| Pin 33            | GPIO 13   | Busy signal | AUX       |

### EBYTE Modes (M0/M1)

| M0 | M1 | Mode | Description |
|----|----|------|-------------|
| LOW | LOW | Normal | Transparent UART TX/RX |
| HIGH | LOW | Wake-up | Wake-up mode |
| LOW | HIGH | Power Save | Listen only |
| HIGH | HIGH | Sleep | Configuration mode |

---

## 2. ESP32 to LoRa EBYTE Module (UART)

### UART2 Connections

```
        ESP32 DevKit                      EBYTE E220/E32
        
     ┌───────────────┐                   ┌──────────┐
     │ USB           │                   │          │
     │               │                   │   VCC    │◄─── 3.3V
     │           3V3 │─────────────────► │          │
     │           GND │─────────────────► │   GND    │
     │               │                   │          │
     │          IO16 │─────────────────► │   RXD    │  (ESP32 TX2)
     │          IO17 │◄───────────────── │   TXD    │  (ESP32 RX2)
     │          IO4  │─────────────────► │   M0     │
     │          IO2  │─────────────────► │   M1     │
     │          IO15 │◄───────────────── │   AUX    │
     │               │                   │          │
     │          IO13 │──► Relay 1        │   ANT    │◄─── Antenna
     │          IO12 │──► Relay 2        └──────────┘
     │          IO27 │──► Relay 3
     │          IO26 │──► Relay 4
     │               │
     │           5V  │──► Relay Module VCC
     │           GND │──► Relay Module GND
     └───────────────┘
```

### Connection Table

| ESP32 Pin | Function       | Connects To    |
|-----------|----------------|----------------|
| 3.3V      | Power          | LoRa VCC       |
| GND       | Ground         | LoRa GND       |
| GPIO16    | UART TX2       | LoRa RXD       |
| GPIO17    | UART RX2       | LoRa TXD       |
| GPIO4     | Mode M0        | LoRa M0        |
| GPIO2     | Mode M1        | LoRa M1        |
| GPIO15    | Busy signal    | LoRa AUX       |
| GPIO13    | Relay Control  | Relay IN1      |
| GPIO12    | Relay Control  | Relay IN2      |
| GPIO27    | Relay Control  | Relay IN3      |
| GPIO26    | Relay Control  | Relay IN4      |
| 5V        | Relay Power    | Relay VCC      |
| GND       | Common Ground  | Relay GND      |

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
                        RASPBERRY PI + LORA EBYTE
                        ┌──────────────────┐
                        │   RPI GPIO       │
                        │   ┌────────────┐ │
                        │   │ EBYTE E220 │ │
                        │   │ LoRa UART  │ │
                        │   │ GPIO14→RXD │ │
                        │   │ GPIO15←TXD │ │
                        │   │ GPIO5→M0   │ │
                        │   │ GPIO6→M1   │ │
                        │   │ GPIO13←AUX │ │
                        │   └───┬────────┘ │
                        └───────┼──────────┘
                                │ Antenna 868MHz
                                │
                         ~ ~ ~ LoRa Radio ~ ~ ~
                                │
                        ┌───────┼──────────┐
                        │   ┌───▼────────┐ │
                        │   │ EBYTE E220 │ │
                        │   │ LoRa UART  │ │
                        │   │ IO16→RXD   │ │
                        │   │ IO17←TXD   │ │
                        │   │ IO4→M0     │ │
                        │   │ IO2→M1     │ │
                        │   │ IO15←AUX   │ │
                        │   └───┬────────┘ │
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
- 1x Raspberry Pi 4B
- 1x EBYTE E220/E32 LoRa UART module (868 MHz for EU)
- 1x Antenna 868 MHz (SMA or wire 8.6 cm)
- 7x Female-Female jumper wires (VCC, GND, TXD, RXD, M0, M1, AUX)
- 1x Power supply for RPi (5V 3A USB-C)

### ESP32 Side
- 1x ESP32 Development Board
- 1x EBYTE E220/E32 LoRa UART module (same frequency as RPi)
- 1x 4-Channel Relay Module
- 4x Solenoid Valves (12V or 24V)
- 1x 12V/24V Power Supply (5A minimum)
- 1x Buck Converter (12V to 5V, 3A minimum)
- 1x Antenna 868 MHz (SMA or wire 8.6 cm)
- 20x Jumper wires (various)
- 4x Flyback diodes (1N4007)
- 2x Fuses + holders
- 1x Weatherproof enclosure
- Wire (18 AWG for valves, 22 AWG for signals)

---

**Document Version:** 2.0 (EBYTE UART)  
**Last Updated:** 2026-03-27  
**Created for:** Irrigation Control System

