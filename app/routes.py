from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required
from app.db import get_db
from datetime import datetime

routes = Blueprint("routes", __name__)

@routes.route("/dashboard")
@login_required
def dashboard() :
    return render_template("dashboard.html")

@routes.route("/irrigation/toggle/<int:zone_id>", methods=["POST"])
@login_required
def irrigation_toggle(zone_id):

    from app.hardware import zone_on, zone_off, zone_state
    db = get_db()

    if zone_state(zone_id):

        zone_off(zone_id)

        db.execute("""
            UPDATE irrigation_log
            SET end_time = ?
            WHERE sector = ? AND end_time IS NULL
        """, (datetime.now(), zone_id))

    else:

        zone_on(zone_id)

        db.execute("""
            INSERT INTO irrigation_log (sector, start_time, type)
            VALUES (?, ?, 'manual')
        """, (zone_id, datetime.now()))

    db.commit()

    return jsonify({"status": "ok"})


@routes.route("/water")
@login_required
def water_consumption() :
    db = get_db()
    total = db.execute("""
        SELECT
          SUM(liters),
          SUM(cost)
        FROM water_consumption
    """).fetchone()

    return render_template(
        "water.html",
        liters=total[0] or 0,
        cost=total[1] or 0
    )


@routes.route("/water/data")
@login_required
def water_data() :
    db = get_db()
    rows = db.execute("""
        SELECT timestamp, liters
        FROM water_consumption
        ORDER BY timestamp ASC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {"time" : r[0], "liters" : r[1]}
        for r in rows
    ])


@routes.route("/irrigation")
@login_required
def irrigation():
    db = get_db()

    zones = db.execute("""
        SELECT id, name, gpio_pin, enabled
        FROM irrigation_zones
    """).fetchall()

    schedules = db.execute("""
        SELECT id, sector, start_time, enabled
        FROM irrigation_schedule
        ORDER BY start_time ASC
    """).fetchall()

    return render_template(
        "irrigation.html",
        zones=zones,
        schedules=schedules
    )



@routes.route("/irrigation/history")
@login_required
def irrigation_history() :
    db = get_db()
    rows = db.execute("""
        SELECT
            zone_id,
            start_time,
            end_time,
            
        FROM irrigation_events
        ORDER BY start_time DESC
        LIMIT 10
    """).fetchall()

    return render_template(
        "irrigation_history.html",
        rows=rows
    )


@routes.route("/irrigation/history/data")
@login_required
def irrigation_history_data() :
    db = get_db()

    rows = db.execute("""
        SELECT
            start_time,
            
        FROM irrigation_events
        ORDER BY start_time ASC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {
            "time" : r[0],
        } for r in rows
    ])


@routes.route("/dashboard/data")
@login_required
def dashboard_data() :
    db = get_db()

    sensor = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    water = db.execute("""
        SELECT SUM(liters)
        FROM water_consumption
    """).fetchone()

    dht = db.execute("""
        SELECT temperature, humidity
        FROM dht_readings
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    return jsonify({
        "temperature" : sensor[0] if sensor else None,
        "humidity" : sensor[1] if sensor else None,
        "solar" : sensor[2] if sensor else None,
        "pressure" : sensor[3] if sensor else None,
        "ec" : sensor[4] if sensor else None,
        "ph" : sensor[5] if sensor else None,
        "time" : sensor[6] if sensor else None,
        "water_liters" : water[0] or 0,

        # 🔥 NUEVO (DHT11)
        "dht_temperature" : dht[0] if dht else None,
        "dht_humidity" : dht[1] if dht else None
    })


@routes.route("/alarms")
@login_required
def alarms() :
    db = get_db()
    rows = db.execute("""
        SELECT type, level, message, value, created_at
        FROM alarms
        ORDER BY created_at DESC
        LIMIT 20
    """).fetchall()

    return jsonify([
        {
            "type" : r[0],
            "level" : r[1],
            "message" : r[2],
            "value" : r[3],
            "time" : r[4]
        }
        for r in rows
    ])


@routes.route("/irrigation/schedule/add", methods=["POST"])
@login_required
def schedule_add() :
    data = request.get_json()

    sector = int(data["sector"])
    start_time = data["start_time"]  # formato HH:MM

    db = get_db()

    db.execute("""
        INSERT INTO irrigation_schedule (sector, start_time, enabled)
        VALUES (?, ?, 1)
    """, (sector, start_time))

    db.commit()

    return jsonify({"success" : True})


# @routes.route("/irrigation/schedule/add", methods=["POST"])
# @login_required
# def schedule_add_ajax():
#     data = request.get_json()
#     db = get_db()
#
#     sector = int(data["sector"])
#     date = data["date"]
#     start = data["start"]
#     end = data["end"]
#
#     start_dt = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
#     end_dt   = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")
#
#     duration = int((end_dt - start_dt).total_seconds() / 60)
#
#     if duration <= 0:
#         return jsonify({"error": "Hora fin inválida"})
#
#     if duration > 60:
#         return jsonify({"error": "Máximo 60 minutos"})
#
#     if duration not in [15,30,45,60]:
#         return jsonify({"error": "Solo 15, 30, 45 o 60 minutos"})
#
#     # máximo 3 riegos por sector por día
#     count = db.execute("""
#         SELECT COUNT(*)
#         FROM irrigation_schedule
#         WHERE sector = ?
#           AND date = ?
#     """,(sector,date)).fetchone()[0]
#
#     if count >= 3:
#         return jsonify({"error":"Máximo 3 riegos por sector y día"})
#
#     db.execute("""
#         INSERT INTO irrigation_schedule
#         (sector, date, start_time, end_time, duration)
#         VALUES (?, ?, ?, ?, ?)
#     """,(sector,date,start,end,duration))
#
#     db.commit()
#
#     return jsonify({"success": True})

# @routes.route("/irrigation/schedule/add", methods=["POST"])
# @login_required
# def schedule_add_ajax():
#     try:
#         data = request.get_json()
#         print("DATA RECIBIDA:", data)
#
#         return jsonify({"ok": True})
#
#     except Exception as e:
#         print("ERROR EN ROUTE:", e)
#         return jsonify({"error": str(e)}), 500

# lista programadores

@routes.route("/irrigation/schedule/list")
@login_required
def schedule_list() :
    db = get_db()

    rows = db.execute("""
        SELECT sector, date, start_time, end_time, duration
        FROM irrigation_schedule
        ORDER BY date ASC, start_time ASC
        LIMIT 20
    """).fetchall()

    return jsonify([
        {
            "sector" : r[0],
            "date" : r[1],
            "start" : r[2],
            "end" : r[3],
            "duration" : r[4]
        }
        for r in rows
    ])



