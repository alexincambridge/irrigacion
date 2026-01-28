import sqlite3
from datetime import datetime, timedelta
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "instance/irrigacion.db"

def seed_irrigation_log(n=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    now = datetime.now()

    for i in range(n):
        duration = random.choice([5, 10, 15, 20, 30, 45])
        start = now - timedelta(days=i, hours=random.randint(0, 3))
        end = start + timedelta(minutes=duration)

        cur.execute("""
            INSERT INTO irrigation_log (start_time, end_time, duration)
            VALUES (?, ?, ?)
        """, (start, end, duration))

    conn.commit()
    conn.close()
    print(f"✔ Insertados {n} riegos en irrigation_log")

if __name__ == "__main__":
    seed_irrigation_log(25)
