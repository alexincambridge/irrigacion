#!/usr/bin/env python3
"""
Test LoRa UART Sender — Raspberry Pi
Envía "Hola Mac" cada 2s por /dev/serial0 a 9600 baud.

Pinout RPi (EBYTE):
  GPIO 14 (TXD) → RXD módulo LoRa
  GPIO 15 (RXD) → TXD módulo LoRa
  M0, M1 → GND (modo transparente)

Usage:  python3 scripts/test_lora_send.py
"""

import serial
import time
import sys

PORT = "/dev/serial0"
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception as e:
    print(f"❌ No se pudo abrir {PORT}: {e}")
    sys.exit(1)

print(f"📡 Enviando por {PORT} @ {BAUD} baud  (Ctrl+C para salir)")

count = 0
try:
    while True:
        count += 1
        msg = "Hola Mac\n"
        ser.write(msg.encode())
        print(f"  #{count:04d} → {msg.strip()}")
        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n👋 Enviados: {count} mensajes")
finally:
    ser.close()

