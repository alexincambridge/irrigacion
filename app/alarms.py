from app.models import get_db
from app.alarms_config import ALARM_LIMITS

def check_alarm(sensor, value):
    limits = ALARM_LIMITS.get(sensor)
    if not limits:
        return

    level = None
    message = None
    threshold = None

    if "min" in limits and value < limits["min"]:
        level = "warning"
        threshold = limits["min"]
        message = f"{sensor} demasiado baja"

    if "max" in limits and value > limits["max"]:
        level = "critical"
        threshold = limits["max"]
        message = f"{sensor} demasiado alta"

    if level:
        db = get_db()
        db.execute("""
            INSERT INTO alarms (type, level, message, value, threshold)
            VALUES (?, ?, ?, ?, ?)
        """, (sensor, level, message, value, threshold))
        db.commit()
