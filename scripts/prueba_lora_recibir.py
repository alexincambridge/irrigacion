#!/usr/bin/env python3
"""
Prueba LoRa — RECIBIR en RPi
Escucha por UART y muestra lo que llega.
Usage: python3 scripts/prueba_lora_recibir.py
"""

import serial
import sys
import glob
from datetime import datetime

BAUD = 9600

# Intentar varios puertos comunes
PORTS = ["/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0", "/dev/ttyUSB0", "/dev/ttyACM0"]

def find_port():
    # Primero mostrar qué puertos existen
    available = glob.glob("/dev/tty*")
    serial_ports = [p for p in available if any(x in p for x in ["USB", "ACM", "AMA", "S0", "serial"])]
    if serial_ports:
        print(f"  Puertos serie detectados: {', '.join(serial_ports)}")

    for port in PORTS:
        try:
            s = serial.Serial(port, BAUD, timeout=1)
            print(f"  ✅ Usando puerto: {port}")
            return s
        except Exception:
            continue
    return None

ser = find_port()
if not ser:
    print("❌ No se encontró ningún puerto serie")
    print("\n   Para habilitar UART en la RPi:")
    print("   1. sudo raspi-config")
    print("   2. Interface Options → Serial Port")
    print("   3. Login shell over serial: NO")
    print("   4. Serial port hardware enabled: YES")
    print("   5. sudo reboot")
    print("\n   Después verifica: ls -l /dev/serial0 /dev/ttyAMA0")
    sys.exit(1)

print(f"📡 RECEPTOR — Escuchando @ {BAUD} baud")
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

