#!/usr/bin/env python3
"""
Script para migrar/reparar la tabla dht_readings
Agrega la columna created_at si falta
"""

import sqlite3
import os

DB_PATH = "/home/alexdev/Documents/irrigacion/instance/irrigation.db"

def migrate_dht_readings():
    """Reparar tabla dht_readings agregando columna created_at"""

    if not os.path.exists(DB_PATH):
        print(f"❌ BD no existe: {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cur = conn.cursor()

        print("🔧 Verificando tabla dht_readings...")

        # Obtener información de la tabla
        cur.execute("PRAGMA table_info(dht_readings)")
        columns = [row[1] for row in cur.fetchall()]

        print(f"   Columnas actuales: {columns}")

        # Verificar si created_at existe
        if 'created_at' not in columns:
            print("   ⚠️  Columna 'created_at' NO existe, agregando...")

            # Agregar columna con timestamp actual como default
            cur.execute("""
                ALTER TABLE dht_readings 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("   ✅ Columna 'created_at' agregada")
        else:
            print("   ✅ Columna 'created_at' ya existe")

        # Verificar las columnas ahora
        cur.execute("PRAGMA table_info(dht_readings)")
        columns = [row[1] for row in cur.fetchall()]
        print(f"   Columnas finales: {columns}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 MIGRACIÓN: Reparar tabla dht_readings")
    print("=" * 60)

    if migrate_dht_readings():
        print("=" * 60)
        print("✅ Migración completada")
        print("=" * 60)
        print("\nAhora puedes ejecutar:")
        print("  python3 scripts/dht_logger.py")
    else:
        print("❌ La migración falló")
        exit(1)

