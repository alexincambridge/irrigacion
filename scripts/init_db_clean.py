#!/usr/bin/env python3
"""
Script para inicializar/recrear la base de datos de riego
Ejecutar: python3 init_db.py
"""

import sqlite3
import os

# Ruta de la base de datos
DB_PATH = "instance/irrigation.db"

def init_database():
    """Crear todas las tablas necesarias para el sistema de riego"""

    # Crear carpeta instance si no existe
    os.makedirs("instance", exist_ok=True)

    # Eliminar BD existente si la quieres recrear desde cero
    if os.path.exists(DB_PATH):
        print(f"⚠️  Eliminando BD existente: {DB_PATH}")
        os.remove(DB_PATH)

    # Conectar a BD (se crea automáticamente si no existe)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("🛠️  Creando tablas de la base de datos...")
    print("=" * 60)

    # ═══════════════════════════════════════════════════════════════
    # 1. ZONAS DE RIEGO
    # ═══════════════════════════════════════════════════════════════
    print("📍 Tabla: irrigation_zones (Zonas de riego)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_zones (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            gpio_pin INTEGER NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    # Insertar 4 zonas estándar
    cur.execute("DELETE FROM irrigation_zones")
    cur.executemany("""
        INSERT INTO irrigation_zones (id, name, gpio_pin, enabled)
        VALUES (?, ?, ?, 1)
    """, [
        (1, "Jardín", 23),
        (2, "Huerta", 24),
        (3, "Césped", 25),
        (4, "Árboles", 27),
    ])
    print("   ✅ 4 zonas creadas: Jardín, Huerta, Césped, Árboles")

    # ═══════════════════════════════════════════════════════════════
    # 2. PROGRAMACIÓN DE RIEGOS
    # ═══════════════════════════════════════════════════════════════
    print("⏰ Tabla: irrigation_schedule (Riegos programados)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector INTEGER NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            duration_minutes INTEGER,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'en espera',
            repeat_days TEXT DEFAULT '',
            repeat_enabled INTEGER DEFAULT 0,
            origin TEXT DEFAULT 'manual',
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Tabla creada para programación de riegos")

    # ═══════════════════════════════════════════════════════════════
    # 3. LOG DE RIEGOS
    # ═══════════════════════════════════════════════════════════════
    print("📋 Tabla: irrigation_log (Historial de riegos)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector INTEGER,
            start_time TEXT,
            end_time TEXT,
            type TEXT,
            scheduled_id INTEGER,
            duration_minutes INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Tabla creada para historial de riegos")

    # ═══════════════════════════════════════════════════════════════
    # 4. CONSUMO DE AGUA
    # ═══════════════════════════════════════════════════════════════
    print("💧 Tabla: water_consumption (Consumo de agua)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS water_consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            irrigation_id INTEGER,
            liters REAL,
            cost REAL,
            timestamp TEXT
        )
    """)
    print("   ✅ Tabla creada para consumo de agua")

    # ═══════════════════════════════════════════════════════════════
    # 5. DATOS DE SENSORES GENERALES
    # ═══════════════════════════════════════════════════════════════
    print("📊 Tabla: sensor_data (Datos de sensores adicionales)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            solar REAL,
            pressure REAL,
            ec REAL,
            ph REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Tabla creada: temperatura, humedad, solar, presión, EC, pH")

    # ═══════════════════════════════════════════════════════════════
    # 6. LECTURAS DHT22
    # ═══════════════════════════════════════════════════════════════
    print("🌡️  Tabla: dht_readings (DHT22 - Temperatura/Humedad)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dht_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Tabla creada para DHT22")

    # ═══════════════════════════════════════════════════════════════
    # 7. REGISTROS DE RIEGOS (HISTÓRICO DETALLADO)
    # ═══════════════════════════════════════════════════════════════
    print("📈 Tabla: irrigation_records (Registros detallados)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector INTEGER NOT NULL,
            start_datetime TEXT NOT NULL,
            end_datetime TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('manual','programado'))
        )
    """)
    print("   ✅ Tabla creada para registros de riegos")

    # ═══════════════════════════════════════════════════════════════
    # GUARDAR CAMBIOS
    # ═══════════════════════════════════════════════════════════════
    conn.commit()
    conn.close()

    print("=" * 60)
    print("✅ Base de datos inicializada correctamente")
    print(f"📁 Ubicación: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        init_database()
        print("\n🎉 Listo para usar")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)

