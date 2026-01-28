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

# CREATE TABLE IF NOT EXISTS irrigation_schedule (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   start_time TEXT,      -- HH:MM
#   duration INTEGER,     -- minutos
#   enabled INTEGER DEFAULT 1
# );

CREATE TABLE IF NOT EXISTS irrigation_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time DATETIME,
  end_time DATETIME,
  duration INTEGER
);

# CREATE TABLE irrigation_state (
#   id INTEGER PRIMARY KEY,
#   is_on INTEGER
# );

conn.commit()
conn.close()

print("✅ Base de datos inicializada correctamente")
