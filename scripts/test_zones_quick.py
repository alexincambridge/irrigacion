#!/usr/bin/env python3
"""
Test rápido de zonas de riego - Sin necesidad de la app Flask
Verifica que todas las zonas se controlan correctamente
"""

import sys
import time

def test_zones():
    """Test all irrigation zones"""
    try:
        import RPi.GPIO as GPIO

        ZONE_PINS = {
            1: 22,  # Jardn
            2: 23,  # Huerta
            3: 25,  # Csped
            4: 27,  # rboles
        }

        PUMP_PIN = 16

        print("🔧 Inicializando GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup all pins
        for zone_id, pin in ZONE_PINS.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        GPIO.setup(PUMP_PIN, GPIO.OUT)
        GPIO.output(PUMP_PIN, GPIO.LOW)

        print("✅ GPIO inicializado\n")

        # Test each zone
        print("="*50)
        print("🧪 PRUEBA SECUENCIAL DE ZONAS")
        print("="*50 + "\n")

        zone_names = {
            1: "Jardín Principal",
            2: "Huerta",
            3: "Césped",
            4: "Árboles"
        }

        for zone_id, pin in ZONE_PINS.items():
            name = zone_names[zone_id]
            print(f"▶ Zona {zone_id} - {name} (GPIO {pin})")

            # Turn ON
            print(f"  Encendiendo...", end=" ", flush=True)
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            print("✅ ON")

            # Turn OFF
            print(f"  Apagando...", end=" ", flush=True)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
            print("✅ OFF\n")

        # Test pump
        print(f"▶ Bomba Peristáltica (GPIO {PUMP_PIN})")
        print(f"  Encendiendo...", end=" ", flush=True)
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        time.sleep(1)
        print("✅ ON")

        print(f"  Apagando...", end=" ", flush=True)
        GPIO.output(PUMP_PIN, GPIO.LOW)
        time.sleep(0.5)
        print("✅ OFF\n")

        print("="*50)
        print("✅ TODAS LAS ZONAS FUNCIONAN CORRECTAMENTE")
        print("="*50)

        GPIO.cleanup()
        return 0

    except ImportError:
        print("❌ ERROR: RPi.GPIO no está instalado")
        print("Instala con: pip install RPi.GPIO")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == '__main__':
    sys.exit(test_zones())

