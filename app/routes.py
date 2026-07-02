from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.db import get_db
from app.extensions import limiter
from datetime import datetime

routes = Blueprint("routes", __name__)

# --------------------
# USER & SYSTEM INFO
# --------------------
@routes.route("/api/current-user")
@login_required
def get_current_user():
    """Get current logged-in user information"""
    return jsonify({
        "username": current_user.username if hasattr(current_user, 'username') else 'Usuario',
        "email": getattr(current_user, 'email', '')
    })

# --------------------
# DASHBOARD
# --------------------
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@routes.route("/dashboard/data")
@login_required
def dashboard_data():
    db = get_db()

    # sensor_data may have 'created_at' or 'timestamp' depending on DB version
    sensor = None
    for ts_col in ("created_at", "timestamp"):
        if sensor is not None:
            break
        try:
            sensor = db.execute(f"""
                SELECT temperature, humidity, solar, pressure, ec, ph, {ts_col}
                FROM sensor_data
                ORDER BY id DESC
                LIMIT 1
            """).fetchone()
        except Exception:
            continue

    water = db.execute("SELECT SUM(liters) FROM water_consumption").fetchone()
    dht = db.execute("""
        SELECT temperature, humidity
        FROM dht_readings
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()
    return jsonify({
        "temperature": sensor[0] if sensor else None,
        "humidity": sensor[1] if sensor else None,
        "solar": sensor[2] if sensor else None,
        "pressure": sensor[3] if sensor else None,
        "ec": sensor[4] if sensor else None,
        "ph": sensor[5] if sensor else None,
        "time": sensor[6] if sensor else None,
        "water_pressure": None,  # No water pressure sensor yet
        "water_liters": water[0] or 0,
        "dht_temperature": dht[0] if dht else None,
        "dht_humidity": dht[1] if dht else None
    })

@routes.route("/dashboard/history")
@login_required
def dashboard_history():
    """Obtener histórico de sensores de las últimas 24 horas.
    Combina datos reales del DHT22 (dht_readings) con sensor_data."""
    try:
        db = get_db()
        from datetime import datetime, timedelta

        since = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

        # ── 1. DHT22 readings (real temp & humidity) ──
        dht_rows = []
        try:
            dht_rows = db.execute("""
                SELECT temperature, humidity, created_at
                FROM dht_readings
                WHERE created_at > ?
                ORDER BY created_at ASC
                LIMIT 500
            """, (since,)).fetchall()
        except Exception as e:
            print(f"[dashboard_history] dht_readings error: {e}")

        # ── 2. sensor_data (pressure, solar, ec, ph) ──
        sensor_rows = []
        for ts_col in ("created_at", "timestamp"):
            if sensor_rows:
                break
            try:
                sensor_rows = db.execute(f"""
                    SELECT temperature, humidity, pressure, solar, ec, ph, {ts_col}
                    FROM sensor_data
                    WHERE {ts_col} > ?
                    ORDER BY {ts_col} ASC
                    LIMIT 500
                """, (since,)).fetchall()
            except Exception:
                continue

        # ── 3. Build unified timeline keyed by minute ──
        def ts_key(ts_str):
            if not ts_str:
                return None
            s = str(ts_str)
            if '.' in s:
                s = s.split('.')[0]
            return s[:16]  # "YYYY-MM-DD HH:MM"

        timeline = {}

        for row in dht_rows:
            key = ts_key(row[2])
            if not key:
                continue
            if key not in timeline:
                timeline[key] = {
                    "temperature": None, "humidity": None,
                    "pressure": None, "solar": None,
                    "ec": None, "ph": None, "timestamp": str(row[2])
                }
            timeline[key]["temperature"] = row[0]
            timeline[key]["humidity"] = row[1]

        for row in sensor_rows:
            key = ts_key(row[6])
            if not key:
                continue
            if key not in timeline:
                timeline[key] = {
                    "temperature": None, "humidity": None,
                    "pressure": None, "solar": None,
                    "ec": None, "ph": None, "timestamp": str(row[6])
                }
            entry = timeline[key]
            if entry["temperature"] is None:
                entry["temperature"] = row[0]
            if entry["humidity"] is None:
                entry["humidity"] = row[1]
            if row[2] is not None:
                entry["pressure"] = row[2]
            if row[3] is not None:
                entry["solar"] = row[3]
            if row[4] is not None:
                entry["ec"] = row[4]
            if row[5] is not None:
                entry["ph"] = row[5]

        # ── 4. Sort and return ──
        history = [timeline[k] for k in sorted(timeline.keys())]
        return jsonify(history[:500])

    except Exception as e:
        print(f"Error fetching dashboard history: {e}")
        return jsonify({"error": str(e)}), 500

# --------------------
# WATER CONSUMPTION
# --------------------
@routes.route("/water")
@login_required
def water_consumption():
    db = get_db()
    total = db.execute("SELECT SUM(liters), SUM(cost) FROM water_consumption").fetchone()
    return render_template("water.html", liters=total[0] or 0, cost=total[1] or 0)

@routes.route("/water/data")
@login_required
def water_data():
    db = get_db()
    rows = db.execute("SELECT timestamp, liters FROM water_consumption ORDER BY timestamp ASC LIMIT 50").fetchall()
    return jsonify([{"time": r[0], "liters": r[1]} for r in rows])

# --------------------
# ALARMS
# --------------------
@routes.route("/alarms")
@login_required
def alarms():
    db = get_db()
    rows = db.execute("""
        SELECT type, level, message, value, created_at
        FROM alarms
        ORDER BY created_at DESC
        LIMIT 20
    """).fetchall()
    return jsonify([{"type": r[0], "level": r[1], "message": r[2], "value": r[3], "time": r[4]} for r in rows])

# --------------------
# IRRIGATION
# --------------------

# Página de riego
@routes.route("/irrigation")
@login_required
def irrigation():
    return render_template("irrigation.html")

@routes.route("/fertilization")
@login_required
def fertilization():
    return render_template("fertilization.html")

@routes.route("/api/fertilize", methods=["POST"])
@login_required
@limiter.limit("10 per minute")
def apply_fertilizer():
    """Apply a fertilization recipe (activates Zone 4 + peristaltic pump)"""
    try:
        from app.config import HARDWARE_MODE
    except ImportError:
        HARDWARE_MODE = 'GPIO'

    data = request.get_json()
    recipe = data.get("recipe", "General")
    duration_minutes = data.get("duration", 30)

    # Zone 4 is for Trees
    ZONE_ID = 4
    duration_seconds = duration_minutes * 60

    try:
        # Activate zone 4 (irrigation valve)
        from app.hardware_manager import zone_on as hw_zone_on, pump_on as hw_pump_on

        success_zone = hw_zone_on(ZONE_ID, duration_seconds)
        success_pump = hw_pump_on(duration_seconds)

        if success_zone or success_pump:
            # Log it
            db = get_db()
            db.execute("""
                INSERT INTO irrigation_log 
                (sector, start_time, end_time, type) 
                VALUES (?, datetime('now'), datetime('now', '+' || ? || ' seconds'), ?)
            """, (ZONE_ID, duration_seconds, f"Fertilizacion: {recipe}"))
            db.commit()

            return jsonify({"success": True, "message": f"Fertilización '{recipe}' iniciada por {duration_minutes} min (Zona 4 + Bomba)"})
        else:
            return jsonify({"success": False, "error": "No se pudo iniciar (hardware error)"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Crear riego programado
@routes.route("/irrigation/schedule/add", methods=["POST"])
@login_required
@limiter.limit("20 per minute")
def schedule_add():
    try:

        data = request.get_json()

        sector = int(data.get("sector"))
        date = data.get("date")
        start_time = data.get("start_time")[:5]
        end_time = data.get("end_time")[:5]
        repeat_days = data.get("repeat_days", "")
        repeat_enabled = int(data.get("repeat_enabled", 0))
        origin = data.get("origin", "manual")

        # Calcular duración en minutos
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))

        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        duration_minutes = end_minutes - start_minutes

        db = get_db()

        # Determinar prioridad por sector (nueva)
        priority_map = {
            4: 1,  # Árboles - Prioridad 1
            1: 2,  # Jardín - Prioridad 2
            2: 3,  # Huerta - Prioridad 3
            3: 4   # Césped - Prioridad 4
        }
        priority = priority_map.get(sector, 0)

        db.execute("""
            INSERT INTO irrigation_schedule 
            (sector, date, start_time, end_time, duration, duration_minutes, status, priority, 
             repeat_days, repeat_enabled, origin, enabled)
            VALUES (?, ?, ?, ?, ?, ?, 'en espera', ?, ?, ?, ?, 1)
        """, (sector, date, start_time, end_time, duration_minutes, duration_minutes, priority,
              repeat_days, repeat_enabled, origin))

        db.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500

@routes.route("/irrigation/schedule/list")
@login_required
def schedule_list():
    try:
        db = get_db()

        # Primero, eliminar riegos que ya terminaron
        from datetime import datetime
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        # Intentar obtener riegos vencidos con nuevos campos
        try:
            vencidos = db.execute("""
                SELECT id, sector, start_time, end_time, duration_minutes, repeat_days, repeat_enabled
                FROM irrigation_schedule
                WHERE enabled = 1
                AND datetime(date || ' ' || end_time) <= ?
            """, (current_datetime,)).fetchall()

            # Registrar en log y reprogramar o eliminar
            for row in vencidos:
                schedule_id = row[0]
                sector = row[1]
                start_time = row[2]
                end_time = row[3]
                duration_minutes = row[4] if len(row) > 4 else None
                repeat_days = row[5] if len(row) > 5 else ''
                repeat_enabled = row[6] if len(row) > 6 else 0

                # Registrar finalización en log
                try:
                    db.execute("""
                        INSERT OR IGNORE INTO irrigation_log 
                        (sector, start_time, end_time, type, scheduled_id, duration_minutes, status)
                        VALUES (?, ?, ?, 'programado', ?, ?, 'completado')
                    """, (sector, f"{now.strftime('%Y-%m-%d')} {start_time}",
                          f"{now.strftime('%Y-%m-%d')} {end_time}", schedule_id, duration_minutes))
                except:
                    db.execute("""
                        INSERT OR IGNORE INTO irrigation_log (sector, start_time, end_time, type)
                        VALUES (?, ?, ?, 'programado')
                    """, (sector, f"{now.strftime('%Y-%m-%d')} {start_time}",
                          f"{now.strftime('%Y-%m-%d')} {end_time}"))

                from datetime import timedelta
                # Reprogramar si tiene repetición
                if repeat_enabled == 1 and repeat_days:
                    # Encontrar el próximo día de repetición
                    days_map = {'L': 0, 'M': 1, 'X': 2, 'J': 3, 'V': 4, 'S': 5, 'D': 6}
                    selected_days = [days_map[d] for d in str(repeat_days) if d in days_map]

                    if selected_days:
                        next_date = now + timedelta(days=1) # Empezar desde mañana

                        # Buscar el siguiente día en un máximo de 7 iteraciones
                        for _ in range(7):
                            if next_date.weekday() in selected_days:
                                break
                            next_date += timedelta(days=1)

                        new_date_str = next_date.strftime("%Y-%m-%d")
                        db.execute("""
                            UPDATE irrigation_schedule
                            SET date = ?, status = 'en espera'
                            WHERE id = ?
                        """, (new_date_str, schedule_id))
                    else:
                        # Si no hay días válidos, desactivar
                        db.execute("UPDATE irrigation_schedule SET enabled = 0 WHERE id = ?", (schedule_id,))
                else:
                    # Marcar como no activo si no se repite
                    db.execute("""
                        UPDATE irrigation_schedule
                        SET enabled = 0
                        WHERE id = ?
                    """, (schedule_id,))

            db.commit()
        except Exception as e:
            print(f"Warning in vencidos check: {e}")

        # Intentar obtener schedules con nuevos campos
        try:
            rows = db.execute("""
                SELECT id, sector, date, start_time, end_time, duration_minutes, priority, status, 
                       repeat_days, repeat_enabled, origin
                FROM irrigation_schedule
                WHERE enabled = 1
                ORDER BY priority ASC, date ASC, start_time ASC
                LIMIT 10
            """).fetchall()

            schedules = []
            for r in rows:
                schedules.append({
                    "id": r[0],
                    "sector": r[1],
                    "date": r[2],
                    "start_time": r[3],
                    "end_time": r[4],
                    "duration_minutes": r[5],
                    "priority": r[6],
                    "status": r[7],
                    "repeat_days": r[8],
                    "repeat_enabled": r[9],
                    "origin": r[10],
                    "enabled": 1  # Sabemos que enabled=1 porque es el WHERE
                })
        except Exception as e:
            # Si falla, usar campos básicos
            print(f"Warning: Using basic fields for schedule: {e}")
            rows = db.execute("""
                SELECT id, sector, date, start_time
                FROM irrigation_schedule
                WHERE enabled = 1
                ORDER BY date ASC, start_time ASC
                LIMIT 10
            """).fetchall()

            schedules = []
            for r in rows:
                # Calcular end_time como start_time + 30 min (default)
                start_h, start_m = map(int, r[3].split(':'))
                end_m = start_h
