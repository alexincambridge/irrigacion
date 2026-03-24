#!/usr/bin/env python3
"""
Script de prueba rápida para verificar DHT22 y sensores
Ejecutar: python3 test_sensors_quick.py
"""

import sys
import time
from pathlib import Path

# Agregar ruta del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "app"))

def test_dht22():
    """Probar DHT22 con use_pulseio=False"""
    print("\n" + "="*60)
    print("🌡️  TEST: DHT22 (GPIO 4)")
    print("="*60)

    try:
        import board
        import adafruit_dht

        print("[ℹ️  INFO] Inicializando DHT22 con use_pulseio=False...")
        dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

        print("[✅ OK] Sensor inicializado")
        print("[ℹ️  INFO] Tomando 5 lecturas (intervalo 2s)...")

        success = 0
        for i in range(5):
            try:
                temp = dht.temperature
                humidity = dht.humidity

                if temp is not None and humidity is not None:
                    print(f"  [{i+1}/5] ✅ T={temp:.1f}°C | H={humidity:.1f}%")
                    success += 1
                else:
                    print(f"  [{i+1}/5] ⚠️  Lectura None (calentando...)")

                time.sleep(2)

            except RuntimeError as e:
                print(f"  [{i+1}/5] ⚠️  RuntimeError: {e.args[0]}")
                time.sleep(2)

        dht.exit()

        if success >= 3:
            print(f"\n✅ RESULTADO: {success}/5 lecturas exitosas")
            return True
        else:
            print(f"\n❌ RESULTADO: Solo {success}/5 lecturas exitosas")
            return False

    except ImportError as e:
        print(f"❌ ERROR: {e}")
        print("   Instalar: pip install adafruit-circuitpython-dht")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_database():
    """Probar conexión a base de datos"""
    print("\n" + "="*60)
    print("💾 TEST: Base de Datos")
    print("="*60)

    try:
        import sqlite3

        db_path = PROJECT_ROOT / "instance" / "irrigation.db"
        print(f"[ℹ️  INFO] Conectando a: {db_path}")

        if not db_path.exists():
            print(f"❌ ERROR: BD no existe en {db_path}")
            return False

        conn = sqlite3.connect(db_path, timeout=5)
        cur = conn.cursor()

        # Verificar tabla dht_readings
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dht_readings'")
        if cur.fetchone():
            print("✅ Tabla 'dht_readings' existe")
        else:
            print("❌ Tabla 'dht_readings' NO existe")
            conn.close()
            return False

        # Verificar tabla sensor_data
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sensor_data'")
        if cur.fetchone():
            print("✅ Tabla 'sensor_data' existe")
        else:
            print("❌ Tabla 'sensor_data' NO existe")
            conn.close()
            return False

        # Contar registros
        cur.execute("SELECT COUNT(*) FROM dht_readings")
        count_dht = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM sensor_data")
        count_sensor = cur.fetchone()[0]

        print(f"✅ Registros en dht_readings: {count_dht}")
        print(f"✅ Registros en sensor_data: {count_sensor}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_insert_sample():
    """Insertar un registro de prueba"""
    print("\n" + "="*60)
    print("📝 TEST: Insertar registro de prueba")
    print("="*60)

    try:
        import sqlite3
        from datetime import datetime

        db_path = PROJECT_ROOT / "instance" / "irrigation.db"
        conn = sqlite3.connect(db_path, timeout=5)
        cur = conn.cursor()

        # Insertar registro de prueba
        temp_test = 25.5
        hum_test = 60.0

        cur.execute(
            "INSERT INTO dht_readings (temperature, humidity, created_at) VALUES (?, ?, ?)",
            (temp_test, hum_test, datetime.now())
        )
        conn.commit()

        # Verificar que se insertó
        cur.execute("SELECT * FROM dht_readings ORDER BY id DESC LIMIT 1")
        last = cur.fetchone()

        if last:
            print(f"✅ Registro insertado: ID={last[0]}, T={last[1]:.1f}°C, H={last[2]:.1f}%")
            conn.close()
            return True
        else:
            print("❌ Fallo al insertar")
            conn.close()
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "█"*60)
    print("█  PRUEBA RÁPIDA - Sistema de Sensores v4.0")
    print("█"*60)

    results = {
        "DHT22": False,
        "Base de Datos": False,
        "Insertar": False,
    }

    # Pruebas
    results["Base de Datos"] = test_database()
    results["Insertar"] = test_insert_sample()
    results["DHT22"] = test_dht22()

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print("="*60)
    if passed == total:
        print(f"🎉 TODAS LAS PRUEBAS PASARON ({passed}/{total})")
        return 0
    else:
        print(f"⚠️  {passed}/{total} pruebas pasaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

