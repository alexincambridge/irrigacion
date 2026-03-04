#!/usr/bin/env python3
"""
Health Check Script - Irrigation System
Checks all peripherals: relays, DHT11, pump, ESP32 LoRa, DB
Run: python scripts/health_check.py
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "instance", "irrigation.db")

ZONE_PINS = {1: 23, 2: 24, 3: 25, 4: 27}
PUMP_PIN = 17
DHT_PIN = 22
FERTILIZER_PIN = 18

results = []
errors = 0


def check(name, device_type, detail=""):
    """Decorator-like function to run a check"""
    def wrapper(func):
        global errors
        try:
            status, message = func()
            results.append({
                "device": name,
                "type": device_type,
                "status": status,
                "message": message,
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            })
            if status == "error":
                errors += 1
        except Exception as e:
            results.append({
                "device": name,
                "type": device_type,
                "status": "error",
                "message": str(e),
                "detail": detail,
                "timestamp": datetime.now().isoformat()
            })
            errors += 1
    return wrapper


def main():
    global errors
    print("=" * 60)
    print("🔍 HEALTH CHECK - Sistema de Irrigación")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # ---- 1. Check GPIO / Relays ----
    print("📡 Comprobando GPIO / Relés...")
    gpio_available = False
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        gpio_available = True

        for zone_id, pin in ZONE_PINS.items():
            try:
                GPIO.setup(pin, GPIO.OUT)
                state = GPIO.input(pin)
                status = "ok" if state == 0 else "active"
                msg = f"GPIO {pin} = {'HIGH (ON)' if state else 'LOW (OFF)'}"
                results.append({
                    "device": f"Relé Zona {zone_id}",
                    "type": "relay",
                    "status": status,
                    "message": msg,
                    "detail": f"GPIO {pin}",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"   ✅ Zona {zone_id} (GPIO {pin}): {'ON' if state else 'OFF'}")
            except Exception as e:
                results.append({
                    "device": f"Relé Zona {zone_id}",
                    "type": "relay",
                    "status": "error",
                    "message": str(e),
                    "detail": f"GPIO {pin}",
                    "timestamp": datetime.now().isoformat()
                })
                errors += 1
                print(f"   ❌ Zona {zone_id} (GPIO {pin}): ERROR - {e}")

    except ImportError:
        print("   ⚠️  RPi.GPIO no disponible (no es Raspberry Pi)")
        for zone_id, pin in ZONE_PINS.items():
            results.append({
                "device": f"Relé Zona {zone_id}",
                "type": "relay",
                "status": "idle",
                "message": "GPIO no disponible (modo simulación)",
                "detail": f"GPIO {pin}",
                "timestamp": datetime.now().isoformat()
            })
    print()

    # ---- 2. Check Peristaltic Pump ----
    print("💉 Comprobando Bomba Peristáltica...")
    if gpio_available:
        try:
            GPIO.setup(PUMP_PIN, GPIO.OUT)
            state = GPIO.input(PUMP_PIN)
            pump_status = "active" if state else "ok"
            results.append({
                "device": "Bomba Peristáltica",
                "type": "actuator",
                "status": pump_status,
                "message": f"GPIO {PUMP_PIN} = {'HIGH (ON)' if state else 'LOW (OFF)'}",
                "detail": f"GPIO {PUMP_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ✅ Bomba (GPIO {PUMP_PIN}): {'ON' if state else 'OFF'}")
        except Exception as e:
            results.append({
                "device": "Bomba Peristáltica",
                "type": "actuator",
                "status": "error",
                "message": str(e),
                "detail": f"GPIO {PUMP_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            errors += 1
            print(f"   ❌ Bomba: ERROR - {e}")
    else:
        results.append({
            "device": "Bomba Peristáltica",
            "type": "actuator",
            "status": "idle",
            "message": "GPIO no disponible",
            "detail": f"GPIO {PUMP_PIN}",
            "timestamp": datetime.now().isoformat()
        })
        print("   ⚠️  GPIO no disponible")
    print()

    # ---- 3. Check DHT11 ----
    print("🌡️  Comprobando DHT11...")
    try:
        import Adafruit_DHT
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
        if humidity is not None and temperature is not None:
            results.append({
                "device": "DHT11 Temp/Humedad",
                "type": "sensor",
                "status": "ok",
                "message": f"T: {temperature:.1f}°C | H: {humidity:.1f}%",
                "detail": f"GPIO {DHT_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ✅ DHT11: T={temperature:.1f}°C  H={humidity:.1f}%")
        else:
            results.append({
                "device": "DHT11 Temp/Humedad",
                "type": "sensor",
                "status": "error",
                "message": "Lectura inválida (None)",
                "detail": f"GPIO {DHT_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            errors += 1
            print("   ❌ DHT11: Lectura inválida")
    except ImportError:
        # Fallback: check DB for recent readings
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT temperature, humidity, timestamp FROM dht_readings ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            conn.close()
            if row:
                results.append({
                    "device": "DHT11 Temp/Humedad",
                    "type": "sensor",
                    "status": "ok",
                    "message": f"T: {row[0]}°C | H: {row[1]}% (última lectura BD)",
                    "detail": f"GPIO {DHT_PIN} | Último: {row[2]}",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"   ✅ DHT11 (vía BD): T={row[0]}°C H={row[1]}%  ({row[2]})")
            else:
                results.append({
                    "device": "DHT11 Temp/Humedad",
                    "type": "sensor",
                    "status": "idle",
                    "message": "Sin lecturas en BD. Adafruit_DHT no instalado.",
                    "detail": f"GPIO {DHT_PIN}",
                    "timestamp": datetime.now().isoformat()
                })
                print("   ⚠️  Sin lecturas y librería no disponible")
        except Exception as e:
            results.append({
                "device": "DHT11 Temp/Humedad",
                "type": "sensor",
                "status": "error",
                "message": str(e),
                "detail": f"GPIO {DHT_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            errors += 1
            print(f"   ❌ DHT11: {e}")
    except Exception as e:
        results.append({
            "device": "DHT11 Temp/Humedad",
            "type": "sensor",
            "status": "error",
            "message": str(e),
            "detail": f"GPIO {DHT_PIN}",
            "timestamp": datetime.now().isoformat()
        })
        errors += 1
        print(f"   ❌ DHT11: {e}")
    print()

    # ---- 4. Check Fertilizer Counter ----
    print("🧪 Comprobando Contador de Fertilizante...")
    if gpio_available:
        try:
            GPIO.setup(FERTILIZER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            results.append({
                "device": "Contador Fertilizante",
                "type": "sensor",
                "status": "ok",
                "message": "Pin configurado correctamente",
                "detail": f"GPIO {FERTILIZER_PIN} (INPUT)",
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ✅ Contador (GPIO {FERTILIZER_PIN}): OK")
        except Exception as e:
            results.append({
                "device": "Contador Fertilizante",
                "type": "sensor",
                "status": "error",
                "message": str(e),
                "detail": f"GPIO {FERTILIZER_PIN}",
                "timestamp": datetime.now().isoformat()
            })
            errors += 1
            print(f"   ❌ Contador: {e}")
    else:
        results.append({
            "device": "Contador Fertilizante",
            "type": "sensor",
            "status": "idle",
            "message": "GPIO no disponible",
            "detail": f"GPIO {FERTILIZER_PIN}",
            "timestamp": datetime.now().isoformat()
        })
        print("   ⚠️  GPIO no disponible")
    print()

    # ---- 5. Check ESP32 LoRa ----
    print("📡 Comprobando ESP32 LoRa...")
    try:
        # Read HARDWARE_MODE directly to avoid triggering GPIO imports
        try:
            from app.config import HARDWARE_MODE
        except Exception:
            HARDWARE_MODE = 'SIMULATION'

        if HARDWARE_MODE == 'LORA':
            try:
                from app.lora_controller import get_lora_controller
                lora = get_lora_controller()
                if lora and lora.ping():
                    quality = lora.get_signal_quality()
                    rssi = quality.get('rssi', '?') if quality else '?'
                    results.append({
                        "device": "ESP32 LoRa (Tensiómetro)",
                        "type": "esp32",
                        "status": "ok",
                        "message": f"Conectado vía LoRa (RSSI: {rssi} dBm)",
                        "detail": "LoRa 868MHz",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"   ✅ ESP32 LoRa: Conectado (RSSI: {rssi} dBm)")
                else:
                    results.append({
                        "device": "ESP32 LoRa (Tensiómetro)",
                        "type": "esp32",
                        "status": "error",
                        "message": "Sin respuesta al ping",
                        "detail": "LoRa",
                        "timestamp": datetime.now().isoformat()
                    })
                    errors += 1
                    print("   ❌ ESP32 LoRa: Sin respuesta")
            except ImportError as ie:
                results.append({
                    "device": "ESP32 LoRa (Tensiómetro)",
                    "type": "esp32",
                    "status": "idle",
                    "message": f"Librería LoRa no disponible ({ie})",
                    "detail": "LoRa",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"   ⚠️  LoRa no disponible: {ie}")
        else:
            results.append({
                "device": "ESP32 LoRa (Tensiómetro)",
                "type": "esp32",
                "status": "idle",
                "message": f"Modo {HARDWARE_MODE} (LoRa no activo)",
                "detail": "",
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ⚠️  Modo {HARDWARE_MODE} - LoRa no activo")
    except Exception as e:
        results.append({
            "device": "ESP32 LoRa (Tensiómetro)",
            "type": "esp32",
            "status": "error",
            "message": str(e)[:80],
            "detail": "LoRa",
            "timestamp": datetime.now().isoformat()
        })
        errors += 1
        print(f"   ❌ ESP32 LoRa: {e}")
    print()

    # ---- 6. Check Database ----
    print("💾 Comprobando Base de Datos...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()

        results.append({
            "device": "Base de Datos SQLite",
            "type": "system",
            "status": "ok",
            "message": f"{len(tables)} tablas: {', '.join(tables[:6])}{'...' if len(tables)>6 else ''}",
            "detail": DB_PATH,
            "timestamp": datetime.now().isoformat()
        })
        print(f"   ✅ SQLite: {len(tables)} tablas encontradas")
        for t in tables:
            print(f"       - {t}")
    except Exception as e:
        results.append({
            "device": "Base de Datos SQLite",
            "type": "system",
            "status": "error",
            "message": str(e),
            "detail": DB_PATH,
            "timestamp": datetime.now().isoformat()
        })
        errors += 1
        print(f"   ❌ BD: {e}")
    print()

    # ---- Summary ----
    print("=" * 60)
    total = len(results)
    ok_count = sum(1 for r in results if r["status"] in ("ok", "active"))
    idle_count = sum(1 for r in results if r["status"] == "idle")
    error_count = sum(1 for r in results if r["status"] == "error")

    print(f"📊 RESUMEN: {total} dispositivos comprobados")
    print(f"   ✅ Operativos: {ok_count}")
    print(f"   ⚠️  En reposo:  {idle_count}")
    print(f"   ❌ Con error:  {error_count}")
    print()

    if errors == 0:
        print("🎉 Todos los periféricos están OK")
    else:
        print(f"⚠️  Se encontraron {errors} error(es)")

    print("=" * 60)

    # Output JSON if --json flag
    if "--json" in sys.argv:
        print("\n📋 JSON Output:")
        print(json.dumps(results, indent=2, ensure_ascii=False))

    # Save results to file
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "instance", "health_check.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": total,
            "ok": ok_count,
            "idle": idle_count,
            "errors": error_count,
            "devices": results
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Resultados guardados en: {output_path}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

