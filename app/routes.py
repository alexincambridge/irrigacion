from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.db import get_db
from datetime import datetime

routes = Blueprint("routes", __name__)

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
    sensor = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()
    water = db.execute("SELECT SUM(liters) FROM water_consumption").fetchone()
    dht = db.execute("""
        SELECT temperature, humidity
        FROM dht_readings
        ORDER BY timestamp DESC
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
        "water_liters": water[0] or 0,
        "dht_temperature": dht[0] if dht else None,
        "dht_humidity": dht[1] if dht else None
    })

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

    db = get_db()

    # Riegos pendientes (máximo 10)
    schedules = db.execute("""
        SELECT id, sector, date, start_time
        FROM irrigation_schedule
        WHERE datetime(date || ' ' || start_time) > datetime('now')
          AND enabled = 1
        ORDER BY date ASC, start_time ASC
        LIMIT 10
    """).fetchall()

    # Historial últimos 10
    history = db.execute("""
        SELECT sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    return render_template(
        "irrigation.html",
        schedules=schedules,
        history=history
    )


# Crear riego programado
@routes.route("/irrigation/schedule/add", methods=["POST"])
@login_required
def schedule_add():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON recibido"}), 400

        sector = int(data.get("sector"))
        date = data.get("date")
        start_time = data.get("start_time")[:5]
        end_time = data.get("end_time")[:5]

        if not sector or not date or not start_time:
            return jsonify({"error": "Datos incompletos"}), 400

        db = get_db()

        db.execute("""
            INSERT INTO irrigation_schedule (sector, date, start_time, end_time, enabled)
            VALUES (?, ?, ?, 1)
        """, (sector, date, start_time, end_time))

        db.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR schedule_add:", e)
        return jsonify({"error": str(e)}), 500


@routes.route("/irrigation/schedule/list")
@login_required
def schedule_list():

    db = get_db()

    rows = db.execute("""
        SELECT id, sector, date, start_time
        FROM irrigation_schedule
        WHERE datetime(date || ' ' || start_time) > datetime('now')
          AND enabled = 1
        ORDER BY date ASC, start_time ASC
        LIMIT 10
    """).fetchall()

    data = [
        {
            "id": r[0],
            "sector": r[1],
            "date": r[2],
            "time": r[3]
        }
        for r in rows
    ]

    return jsonify(data)

@routes.route("/irrigation/schedule/delete/<int:schedule_id>", methods=["DELETE"])
@login_required
def schedule_delete(schedule_id):

    db = get_db()

    db.execute("""
        DELETE FROM irrigation_schedule
        WHERE id = ?
    """, (schedule_id,))

    db.commit()

    return jsonify({"success": True})


@routes.route("/irrigation/manual/<int:sector>", methods=["POST"])
@login_required
def irrigation_manual(sector):

    from app.hardware import zone_on, zone_off, zone_state

    db = get_db()

    if zone_state(sector):

        zone_off(sector)

        db.execute("""
            UPDATE irrigation_log
            SET end_time = ?
            WHERE sector = ? AND end_time IS NULL
        """, (datetime.now(), sector))

    else:

        zone_on(sector)

        db.execute("""
            INSERT INTO irrigation_log (sector, start_time, type)
            VALUES (?, ?, 'manual')
        """, (sector, datetime.now()))

    db.commit()

    return jsonify({"success": True})


# @routes.route("/irrigation/schedule", methods=["POST"])
# @login_required
# def add_schedule():
#     data = request.json
#     sector = data.get("sector")
#     date = data.get("date")
#     start_time = data.get("time")
#
#     if not all([sector, date, start_time]):
#         return jsonify({"success": False, "message": "Datos incompletos"}), 400
#
#     db = get_db()
#     db.execute("""
#         INSERT INTO irrigation_schedule (sector, date, start_time, enabled)
#         VALUES (?, ?, ?, 1)
#     """, (sector, date, start_time))
#     db.commit()
#     return jsonify({"success": True})

# Obtener riegos programados pendientes (max 10)
@routes.route("/irrigation/schedule", methods=["GET"])
@login_required
def get_schedules():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, date, start_time
        FROM irrigation_schedule
        WHERE enabled=1 AND (date || ' ' || start_time) > ?
        ORDER BY date ASC, start_time ASC
        LIMIT 10
    """, (now_str,)).fetchall()
    schedules = [dict(r) for r in rows]
    return jsonify(schedules)

# Cancelar riego programado
@routes.route("/irrigation/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def delete_schedule(schedule_id):
    db = get_db()
    db.execute("DELETE FROM irrigation_schedule WHERE id=?", (schedule_id,))
    db.commit()
    return jsonify({"success": True})

# Activar / desactivar riego manual
@routes.route("/irrigation/manual", methods=["POST"])
@login_required
def manual_irrigate():
    data = request.json
    sector = data.get("sector")
    action = data.get("action")  # "start" o "stop"

    if not sector or action not in ["start", "stop"]:
        return jsonify({"success": False}), 400

    db = get_db()
    if action == "start":
        db.execute("""
            INSERT INTO irrigation_log (sector, start_time, type)
            VALUES (?, CURRENT_TIMESTAMP, 'manual')
        """, (sector,))
    else:
        db.execute("""
            UPDATE irrigation_log
            SET end_time=CURRENT_TIMESTAMP
            WHERE sector=? AND type='manual' AND end_time IS NULL
        """, (sector,))
    db.commit()
    return jsonify({"success": True})

# Obtener historial de riegos (últimos 10)
@routes.route("/irrigation/log", methods=["GET"])
@login_required
def get_irrigation_log():
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    log = [dict(r) for r in rows]
    return jsonify(log)

@routes.route("/irrigation/history")
@login_required
def irrigation_history():
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()
    return render_template("irrigation_history.html", rows=rows)