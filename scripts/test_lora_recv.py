#!/usr/bin/env python3
"""
Test LoRa UART Receiver — Raspberry Pi
Listens on /dev/serial0 at 9600 baud for messages from the Pico emitter.

Pinout RPi (EBYTE module):
  GPIO 14 (TXD) → RXD módulo LoRa
  GPIO 15 (RXD) → TXD módulo LoRa
  3.3V           → VCC
  GND            → GND
  (M0 y M1 a GND para modo normal/transparente)

Usage:  python3 scripts/test_lora_recv.py
Stop:   Ctrl+C
"""

import serial
import sys
import time
from datetime import datetime

PORT = "/dev/serial0"
BAUD = 9600

print("=" * 55)
print("  📡 LoRa UART Receiver — Raspberry Pi")
print("=" * 55)
print(f"  Puerto : {PORT}")
print(f"  Baud   : {BAUD}")
print(f"  M0/M1  : ambos a GND (modo transparente)")
print("=" * 55)
print("  Esperando mensajes del Pico…  (Ctrl+C para salir)")
print()

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1,
    )
except Exception as e:
    print(f"❌ No se pudo abrir {PORT}: {e}")
    print("   → ¿Está habilitado UART? sudo raspi-config → Interface → Serial Port")
    print("   → ¿Está instalado pyserial? pip install pyserial")
    sys.exit(1)

count = 0
try:
    while True:
        line = ser.readline()
        if line:
            count += 1
            ts = datetime.now().strftime("%H:%M:%S")
            msg = line.decode("utf-8", errors="replace").strip()
            print(f"  [{ts}] #{count:04d}  ✅ {msg}")
        # else: timeout, no data — just loop
except KeyboardInterrupt:
    print(f"\n\n  Recibidos: {count} mensajes")
    print("  👋 Adiós")
finally:
    ser.close()

