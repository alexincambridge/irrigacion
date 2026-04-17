#!/usr/bin/env python3
"""
Prueba LoRa — ENVIAR desde RPi
Envía "Hola Mac" cada 2s por UART.
Usage: python3 scripts/prueba_lora_enviar.py
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

print(f"📡 EMISOR — Enviando por {PORT} @ {BAUD} baud")
print("   Ctrl+C para salir\n")

count = 0
try:
    while True:
        count += 1
        msg = "Hola Mac\n"
        ser.write(msg.encode())
        print(f"  TX #{count:04d} → Hola Mac")
        time.sleep(2)
except KeyboardInterrupt:
    print(f"\n👋 Total enviados: {count}")
finally:
    ser.close()

