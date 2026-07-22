import os
import sqlite3
from flask import g

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "irrigation.db")

_migrated = False

def _ensure_columns(conn):
    """Auto-migrate: add missing columns/tables for backward compatibility."""
    global _migrated
    if _migrated:
        return
    try:
        cur = conn.cursor()
        # sensor_data timestamp compatibility
        cols = [row[1] for row in cur.execute("PRAGMA table_info(sensor_data)").fetchall()]
        if "timestamp" not in cols and "created_at" in cols:
            cur.execute("ALTER TABLE sensor_data ADD COLUMN timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
        elif "created_at" not in cols and "timestamp" in cols:
            cur.execute("ALTER TABLE sensor_data ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            conn.commit()

        # lora_readings table for satellite devices
        tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "lora_readings" not in tables:
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
    except Exception:
        pass
    _migrated = True

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        _ensure_columns(g.db)
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
