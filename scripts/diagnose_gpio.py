#!/usr/bin/env python3
"""
Diagnóstico completo de GPIOs para riego
Verifica cada GPIO individualmente
"""

import RPi.GPIO as GPIO
import time
import sys

# Configuración
ZONE_PINS = {
    1: 23,  # sector 1 - Jardín
    2: 24,  # sector 2 - Huerta
    3: 25,  # sector 3 - Césped
    4: 27,  # sector 4 - Árboles
}

PUMP_PIN = 17  # Peristaltic pump

def cleanup():
    """Clean up GPIO on exit"""
    print("\n🔧 Limpiando GPIO...")
    GPIO.cleanup()
    print("✅ GPIO limpio")

def test_gpio():
    """Test each GPIO individually"""
    try:
        # Setup
        print("🔧 Configurando GPIO...")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Initialize all pins
        all_pins = list(ZONE_PINS.values()) + [PUMP_PIN]
        for pin in all_pins:
            try:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
                print(f"  ✅ GPIO {pin} inicializado correctamente")
            except Exception as e:
                print(f"  ❌ GPIO {pin} ERROR: {e}")

        print("\n" + "="*60)
        print("🧪 PRUEBAS DE FUNCIONAMIENTO")
        print("="*60 + "\n")

        # Test each zone
        for zone_id, pin in ZONE_PINS.items():
            print(f"🔍 Probando Zona {zone_id} (GPIO {pin})...")

            try:
                # Turn ON
                GPIO.output(pin, GPIO.HIGH)
                print(f"  → Activando GPIO {pin}...", end=" ")
                time.sleep(0.5)
                state = GPIO.input(pin)

                if state == GPIO.HIGH:
                    print(f"✅ GPIO {pin} está en HIGH")
                else:
                    print(f"❌ GPIO {pin} no está en HIGH (valor: {state})")

                # Turn OFF
                GPIO.output(pin, GPIO.LOW)
                print(f"  → Desactivando GPIO {pin}...", end=" ")
                time.sleep(0.5)
                state = GPIO.input(pin)

                if state == GPIO.LOW:
                    print(f"✅ GPIO {pin} está en LOW")
                else:
                    print(f"❌ GPIO {pin} no está en LOW (valor: {state})")

            except Exception as e:
                print(f"\n  ❌ ERROR en zona {zone_id}: {e}")

            print()

        # Test pump
        print(f"🔍 Probando Bomba Peristáltica (GPIO {PUMP_PIN})...")
        try:
            GPIO.output(PUMP_PIN, GPIO.HIGH)
            print(f"  → Activando GPIO {PUMP_PIN}...", end=" ")
            time.sleep(0.5)
            state = GPIO.input(PUMP_PIN)

            if state == GPIO.HIGH:
                print(f"✅ GPIO {PUMP_PIN} está en HIGH")
            else:
                print(f"❌ GPIO {PUMP_PIN} no está en HIGH")

            GPIO.output(PUMP_PIN, GPIO.LOW)
            print(f"  → Desactivando GPIO {PUMP_PIN}...", end=" ")
            time.sleep(0.5)
            state = GPIO.input(PUMP_PIN)

            if state == GPIO.LOW:
                print(f"✅ GPIO {PUMP_PIN} está en LOW")
            else:
                print(f"❌ GPIO {PUMP_PIN} no está en LOW")

        except Exception as e:
            print(f"❌ ERROR en bomba: {e}")

        print("\n" + "="*60)
        print("📊 RESUMEN")
        print("="*60)

        # Verify all pins are LOW
        all_pins_ok = True
        for zone_id, pin in ZONE_PINS.items():
            state = GPIO.input(pin)
            if state == GPIO.LOW:
                print(f"✅ Zona {zone_id} (GPIO {pin}): OK")
            else:
                print(f"❌ Zona {zone_id} (GPIO {pin}): FAIL")
                all_pins_ok = False

        pump_state = GPIO.input(PUMP_PIN)
        if pump_state == GPIO.LOW:
            print(f"✅ Bomba (GPIO {PUMP_PIN}): OK")
        else:
            print(f"❌ Bomba (GPIO {PUMP_PIN}): FAIL")
            all_pins_ok = False

        if all_pins_ok:
            print("\n✅ TODOS LOS GPIO FUNCIONAN CORRECTAMENTE")
            return 0
        else:
            print("\n❌ ALGUNOS GPIO NO FUNCIONAN")
            return 1

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return 2

    finally:
        cleanup()

if __name__ == '__main__':
    print("="*60)
    print("🌱 DIAGNÓSTICO DE GPIO PARA SISTEMA DE RIEGO")
    print("="*60 + "\n")

    sys.exit(test_gpio())

