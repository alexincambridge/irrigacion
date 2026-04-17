#!/usr/bin/env python3
"""
Prueba LoRa — RECIBIR en RPi
Escucha por UART y muestra lo que llega.
Usage: python3 scripts/prueba_lora_recibir.py
"""

import serial
import sys
from datetime import datetime

PORT = "/dev/serial0"
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except Exception as e:
    print(f"❌ No se pudo abrir {PORT}: {e}")
    sys.exit(1)

print(f"📡 RECEPTOR — Escuchando en {PORT} @ {BAUD} baud")
print("   Ctrl+C para salir\n")

count = 0
try:
    while True:
        line = ser.readline()
        if line:
            count += 1
            ts = datetime.now().strftime("%H:%M:%S")
            msg = line.decode("utf-8", errors="replace").strip()
            print(f"  RX [{ts}] #{count:04d} ✅ {msg}")
except KeyboardInterrupt:
    print(f"\n👋 Total recibidos: {count}")
finally:
    ser.close()

