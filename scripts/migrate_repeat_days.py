#!/usr/bin/env python3
"""
Script para agregar campos de repetición semanal a la BD existente
"""

import sqlite3
import os

DB_PATH = "instance/irrigation.db"

def migrate_repeat_fields():
    if not os.path.exists(DB_PATH):
        print("❌ Base de datos no encontrada.")
        return False

    print("🔄 Agregando campos de repetición semanal...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Verificar columnas existentes
        cur.execute("PRAGMA table_info(irrigation_schedule)")
        columns = [row[1] for row in cur.fetchall()]

        # Agregar repeat_days
        if 'repeat_days' not in columns:
            print("  ➕ Agregando columna 'repeat_days'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN repeat_days TEXT DEFAULT ''")

        # Agregar repeat_enabled
        if 'repeat_enabled' not in columns:
            print("  ➕ Agregando columna 'repeat_enabled'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN repeat_enabled INTEGER DEFAULT 0")

        # Agregar origin
        if 'origin' not in columns:
            print("  ➕ Agregando columna 'origin'...")
            cur.execute("ALTER TABLE irrigation_schedule ADD COLUMN origin TEXT DEFAULT 'manual'")

        conn.commit()
        print("✅ Campos agregados exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MIGRACIÓN - REPETICIÓN SEMANAL DE RIEGOS")
    print("=" * 60)
    print()

    success = migrate_repeat_fields()

    print()
    if success:
        print("🎉 Base de datos actualizada!")
    else:
        print("❌ La migración falló.")
    print()

