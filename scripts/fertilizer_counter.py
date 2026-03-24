"""
Logger del Contador de Fertilizante
Lee pulsos GPIO del contador para medir volumen inyectado

Conexión: GPIO 18 (contador = entrada con pull-up)
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "instance" / "irrigation.db"
COUNTER_PIN = 18
PULSE_TO_ML = 0.5  # Ajusta según tu contador (mL por pulso)

# Intentar cargar RPi.GPIO
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    print("⚠️  RPi.GPIO no disponible (no es Raspberry Pi)")
    GPIO_AVAILABLE = False

def setup_gpio():
    """Configurar GPIO 18 como entrada con pull-up"""
    if not GPIO_AVAILABLE:
        return False

    try:
        GPIO.setup(COUNTER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"[✅ OK] GPIO {COUNTER_PIN} configurado como entrada")
        return True
    except Exception as e:
        print(f"[❌ ERROR] Configurando GPIO: {e}")
        return False

def insert_fertilizer_reading(pulses, volume_ml):
    """Insertar lectura de fertilizante"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO water_consumption 
        (liters, timestamp)
        VALUES (?, ?)
        """,
        (volume_ml / 1000.0, datetime.now())  # Convertir a litros
    )
    conn.commit()
    conn.close()

def count_pulses(duration_seconds=10):
    """
    Contar pulsos en un periodo de tiempo

    Args:
        duration_seconds: Tiempo de muestreo

    Returns:
        Número de pulsos detectados
    """
    if not GPIO_AVAILABLE:
        # Simulación
        import random
        return random.randint(0, 5)

    try:
        pulse_count = 0
        last_state = GPIO.input(COUNTER_PIN)
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            current_state = GPIO.input(COUNTER_PIN)

            # Detectar transición de HIGH a LOW (flanco descendente)
            if last_state == 1 and current_state == 0:
                pulse_count += 1

            last_state = current_state
            time.sleep(0.01)  # Pequeño delay para no saturar CPU

        return pulse_count

    except Exception as e:
        print(f"[❌ ERROR] Contando pulsos: {e}")
        return 0

def main():
    print("💊 Fertilizer Counter Logger iniciado")
    print("=" * 60)
    print(f"Pin: GPIO {COUNTER_PIN}")
    print(f"Calibración: {PULSE_TO_ML} mL/pulso")
    print(f"DB: {DB_PATH}")
    print("=" * 60)

    if GPIO_AVAILABLE:
        if not setup_gpio():
            print("[⚠️  WARN] GPIO no disponible, usando simulación")
    else:
        print("[ℹ️  INFO] Usando modo simulación (no es RPi)")

    print()

    try:
        while True:
            # Contar pulsos durante 10 segundos
            pulses = count_pulses(duration_seconds=10)
            volume_ml = pulses * PULSE_TO_ML

            if pulses > 0:
                insert_fertilizer_reading(pulses, volume_ml)
                print(
                    f"[✅ OK] {pulses} pulsos | {volume_ml:.1f}mL | "
                    f"@ {datetime.now().strftime('%H:%M:%S')}"
                )
            else:
                print(
                    f"[ℹ️  INFO] 0 pulsos | 0.0mL | "
                    f"@ {datetime.now().strftime('%H:%M:%S')}"
                )

    except KeyboardInterrupt:
        print("\n[⛔ STOP] Detenido por usuario")
    finally:
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("[✅] GPIO limpiado")

if __name__ == "__main__":
    main()

