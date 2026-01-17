import sqlite3
from flask import g

DB_PATH = "database/irrigation.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            timeout=5,
            check_same_thread=False
        )
        g.db.execute("PRAGMA journal_mode=WAL;")
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()
