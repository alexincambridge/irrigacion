#!/usr/bin/env python3
"""
Prueba LoRa — ENVIAR desde RPi
Envía "Hola Mac" cada 2s por UART.
Usage: python3 scripts/prueba_lora_enviar.py
"""

import serial
import time
import sys
import glob

BAUD = 9600
PORTS = ["/dev/serial0", "/dev/ttyAMA0", "/dev/ttyS0", "/dev/ttyUSB0", "/dev/ttyACM0"]

def find_port():
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
    sys.exit(1)

print(f"📡 EMISOR — Enviando @ {BAUD} baud")
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

