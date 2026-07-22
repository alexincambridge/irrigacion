#!/usr/bin/env python3
"""
Script para migrar la base de datos a la nueva estructura
sin perder datos existentes.
"""

import sqlite3
import os

DB_PATH = "instance/irrigation.db"

def migrate_database():
    if not os.path.exists(DB_PATH):
        print("❌ Base de datos no encontrada. Ejecuta init_db.py primero.")
        return False

    print("🔄 Migrando base de datos...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Verificar columnas existentes en irrigation_schedule
        cur.execute("PRAGMA table_info(irrigation_schedule)")
        columns = [row[1] for row in cur.fetchall()]

        print(f"📋 Columnas actuales en irrigation_schedule: {columns}")

        # Agregar columnas faltantes a irrigation_schedule
        if 'end_time' not in columns:
            print("  ➕ Agregando columna 'end_time'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN end_time TEXT")
            # Actualizar registros existentes con end_time = start_time + 30 min
            cur.execute("""
                UPDATE irrigation_schedule 
                SET end_time = time(start_time, '+30 minutes')
                WHERE end_time IS NULL
            """)

        if 'duration_minutes' not in columns:
            print("  ➕ Agregando columna 'duration_minutes'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN duration_minutes INTEGER DEFAULT 30")

        if 'priority' not in columns:
            print("  ➕ Agregando columna 'priority'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN priority INTEGER DEFAULT 0")

        if 'status' not in columns:
            print("  ➕ Agregando columna 'status'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN status TEXT DEFAULT 'en espera'")

        if 'created_at' not in columns:
            print("  ➕ Agregando columna 'created_at'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN created_at TIMESTAMP")

        # Verificar columnas existentes en irrigation_log
        cur.execute("PRAGMA table_info(irrigation_log)")
        columns = [row[1] for row in cur.fetchall()]

        print(f"📋 Columnas actuales en irrigation_log: {columns}")

        # Agregar columnas faltantes a irrigation_log
        if 'scheduled_id' not in columns:
            print("  ➕ Agregando columna 'scheduled_id'...")
            cur.execute("ALTER TABLE irrigation_log ADD COLUMN scheduled_id INTEGER")

        if 'duration_minutes' not in columns:
            print("  ➕ Agregando columna 'duration_minutes'...")
            cur.execute("ALTER TABLE irrigation_log ADD COLUMN duration_minutes INTEGER")

        if 'status' not in columns:
            print("  ➕ Agregando columna 'status'...")
            cur.execute("ALTER TABLE irrigation_log ADD COLUMN status TEXT")

        if 'created_at' not in columns:
            print("  ➕ Agregando columna 'created_at'...")
            cur.execute("ALTER TABLE irrigation_log ADD COLUMN created_at TIMESTAMP")

        # Crear tabla lora_readings si no existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lora_readings'")
        if not cur.fetchone():
            print("  ➕ Creando tabla 'lora_readings' para satélites LoRa...")
            cur.execute("""
                CREATE TABLE lora_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    device_name TEXT DEFAULT '',
                    counter INTEGER DEFAULT 0,
                    s1_temp REAL,
                    s2_temp REAL,
                    s3_temp REAL,
                    rele INTEGER DEFAULT 0,
                    raw_packet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        conn.commit()
        print("✅ Migración completada exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MIGRACIÓN DE BASE DE DATOS - SISTEMA DE IRRIGACIÓN")
    print("=" * 60)
    print()

    success = migrate_database()

    print()
    if success:
        print("🎉 Base de datos migrada correctamente!")
        print("   Puedes reiniciar el servidor con: python run.py")
    else:
        print("❌ La migración falló.")
        print("   Si persiste el problema, respalda tus datos y ejecuta:")
        print("   python scripts/init_db.py")
    print()

