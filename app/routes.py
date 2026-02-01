from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required

from app.irrigation import irrigation
from app.irrigation_1 import irrigation_bp
from app.models import get_db

from flask import request
from app.hardware import irrigation_on, irrigation_off, irrigation_status

routes = Blueprint("routes", __name__)

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

    water = db.execute("""
        SELECT SUM(liters), SUM(cost)
        FROM water_consumption
    """).fetchone()

    return jsonify({
        "temperature": sensor[0],
        "humidity": sensor[1],
        "solar": sensor[2],
        "pressure": sensor[3],
        "ec": sensor[4],
        "ph": sensor[5],
        "time": sensor[6],
        "water_liters": water[0] or 0,
        "water_cost": water[1] or 0
    })


@routes.route("/latest")
@login_required
def latest():
    db = get_db()
    row = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    if row is None:
        return jsonify({})

    return jsonify({
        "temperature": row[0],
        "humidity": row[1],
        "solar": row[2],
        "pressure": row[3],
        "ec": row[4],
        "ph": row[5],
        "timestamp": row[6]
    })

#irrigation statu de desarrollo
# @irrigation_bp.route("/status")
# def irrigation_status():
#     db = get_db()
#     rows = db.execute("""
#         SELECT id, is_active, started_at
#         FROM irrigation_zones
#     """).fetchall()
#
#     return jsonify([
#         {
#             "id": r["id"],
#             "is_active": bool["is_active"],
#             "started_at": r["started_at"]
#         }
#         for r in rows
#     ])

#irrigation status de produccion
@irrigation.route("/irrigation/status")
def irrigation_status():
    db = get_db()
    rows = db.execute("""
        SELECT id, is_active, started_at
        FROM irrigation_zones
    """).fetchall()

    return jsonify([
        {
            "id": r["id"],
            "is_active": bool(r["is_active"]),
            "started_at": r["started_at"]
        }
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
    return render_template("irrigation.html", zones=zones)


@routes.route("/irrigation/toggle/<int:zone_id>", methods=["POST"])
@login_required
def irrigation_toggle(zone_id):
    from app.hardware import zone_on, zone_off, zone_state
    db = get_db()

    if zone_state(zone_id):
        zone_off(zone_id)
        db.execute("""
            UPDATE irrigation_events
            SET end_time = datetime('now'),
                duration = CAST((julianday('now') - julianday(start_time)) * 1440 AS INTEGER)
            WHERE zone_id = ? AND end_time IS NULL
        """, (zone_id,))
    else:
        zone_on(zone_id)
        db.execute("""
            INSERT INTO irrigation_events (zone_id, start_time)
            VALUES (?, datetime('now'))
        """, (zone_id,))

    db.commit()
    return jsonify({"status": "ok"})


# @routes.route("/irrigation/status")
# @login_required
# def irrigation_status_api():
#     return jsonify({"on": irrigation_status()})

@routes.route("/irrigation/status")
@login_required
def irrigation_status():
    from app.hardware import zone_state
    db = get_db()

    zones = db.execute("""
        SELECT id, name FROM irrigation_zones
    """).fetchall()

    return jsonify([
        {
            "id": z[0],
            "on": zone_state(z[0])
        } for z in zones
    ])

@routes.route("/irrigation/on", methods=["POST"])
@login_required
def irrigation_on_api():
    irrigation_on()
    return jsonify({"ok": True})

@routes.route("/irrigation/off", methods=["POST"])
@login_required
def irrigation_off_api():
    irrigation_off()
    return jsonify({"ok": True})

@routes.route("/irrigation/history")
@login_required
def irrigation_history():
    db = get_db()
    rows = db.execute("""
        SELECT start_time, end_time, duration
        FROM irrigation_log
        ORDER BY start_time DESC
        LIMIT 50
    """).fetchall()

    return render_template("irrigation_history.html", rows=rows)


@routes.route("/irrigation/history/data")
@login_required
def irrigation_history_data():
    db = get_db()
    rows = db.execute("""
        SELECT start_time, duration
        FROM irrigation_log
        ORDER BY start_time ASC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {
            "time": r[0],
            "duration": r[1]
        } for r in rows
    ])


@routes.route("/schedule")
@login_required
def schedule():
    db = get_db()
    rows = db.execute("""
        SELECT id, start_time, duration, enabled
        FROM irrigation_schedule
    """).fetchall()
    return render_template("schedule.html", rows=rows)

@routes.route("/schedule/add", methods=["POST"])
@login_required
def schedule_add():
    db = get_db()
    db.execute("""
        INSERT INTO irrigation_schedule (start_time, duration)
        VALUES (?, ?)
    """, (request.form["time"], request.form["duration"]))
    db.commit()
    return redirect(url_for("routes.schedule"))

@routes.route("/water")
@login_required
def water_dashboard():
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
def water_data():
    db = get_db()
    rows = db.execute("""
        SELECT timestamp, liters
        FROM water_consumption
        ORDER BY timestamp ASC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {"time": r[0], "liters": r[1]}
        for r in rows
    ])


