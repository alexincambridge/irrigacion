import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigacion.db")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    solar REAL,
    pressure REAL,
    ec REAL,
    ph REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS irrigation_schedule (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time TEXT,      -- HH:MM
  duration INTEGER,     -- minutos
  enabled INTEGER DEFAULT 1
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS irrigation_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time DATETIME,
  end_time DATETIME,
  duration INTEGER
)
""")
cur.execute("""
CREATE TABLE irrigation_state (
  id INTEGER PRIMARY KEY,
  is_on INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS irrigation_zones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  gpio_pin INTEGER NOT NULL,
  enabled INTEGER DEFAULT 1
)
""")

# INSERT INTO irrigation_zones (name, gpio_pin) VALUES
# ('Jardín', 23),
# ('Huerto', 24),
# ('Goteo', 25);

# tabla de eventos por zona
cur.execute("""
CREATE TABLE IF NOT EXISTS irrigation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  zone_id INTEGER,
  start_time DATETIME,
  end_time DATETIME,
  duration INTEGER,
  FOREIGN KEY(zone_id) REFERENCES irrigation_zones(id)
)
""")
# ALTER TABLE irrigation_zones ADD COLUMN is_active INTEGER DEFAULT 0;
# ALTER TABLE irrigation_zones ADD COLUMN started_at TEXT;
# CREATE TABLE IF NOT EXISTS dht_readings (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   temperature REAL NOT NULL,
#   humidity REAL NOT NULL,
#   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# );
CREATE TABLE IF NOT EXISTS alarms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,              -- temperature, humidity, solar...
    level TEXT NOT NULL,             -- info, warning, critical
    message TEXT NOT NULL,
    value REAL,
    threshold REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged INTEGER DEFAULT 0
);


conn.commit()
conn.close()

print("✅ Base de datos inicializada correctamente")
