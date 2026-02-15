import sqlite3
import os

DB_PATH = "instance/irrigacion.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

def init_database():

    # Crear carpeta instance si no existe
    os.makedirs("instance", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("🛠 Creando tablas...")

    # -------------------------
    # ZONAS
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_zones (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            gpio_pin INTEGER NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    # Insertar zonas base si no existen
    cur.execute("DELETE FROM irrigation_zones")

    cur.executemany("""
        INSERT INTO irrigation_zones (id, name, gpio_pin, enabled)
        VALUES (?, ?, ?, 1)
    """, [
        (1, "Sector 1", 23),
        (2, "Sector 2", 24),
        (3, "Sector 3", 25),
    ])

    # -------------------------
    # PROGRAMACIÓN
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            enabled INTEGER DEFAULT 1
        )
    """)

    # -------------------------
    # LOG DE RIEGOS
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sector INTEGER,
            start_time TEXT,
            end_time TEXT,
            type TEXT
        )
    """)

    # -------------------------
    # CONSUMO AGUA
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS water_consumption (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            irrigation_id INTEGER,
            liters REAL,
            cost REAL,
            timestamp TEXT
        )
    """)

    # -------------------------
    # SENSOR DATA GENERAL
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            solar REAL,
            pressure REAL,
            ec REAL,
            ph REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # DHT11
    # -------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dht_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Base de datos inicializada correctamente.")


if __name__ == "__main__":
    init_database()
