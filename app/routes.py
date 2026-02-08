from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required
from app.db import get_db

routes = Blueprint("routes", __name__)

@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@routes.route("/water")
@login_required
def water_consumption():
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


@routes.route("/irrigation")
@login_required
def irrigation_page():
    db = get_db()
    zones = db.execute("""
        SELECT id, name, gpio_pin, enabled
        FROM irrigation_zones
    """).fetchall()

    return render_template("irrigation.html", zones=zones)


@routes.route("/irrigation/history")
@login_required
def irrigation_history():
    db = get_db()
    rows = db.execute("""
        SELECT
            zone_id,
            start_time,
            end_time,
            duration
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
def irrigation_history_data():
    db = get_db()

    rows = db.execute("""
        SELECT
            start_time,
            duration
        FROM irrigation_events
        ORDER BY start_time ASC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {
            "time": r[0],
            "duration": r[1]
        } for r in rows
    ])


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
        "temperature": sensor[0] if sensor else None,
        "humidity": sensor[1] if sensor else None,
        "solar": sensor[2] if sensor else None,
        "pressure": sensor[3] if sensor else None,
        "ec": sensor[4] if sensor else None,
        "ph": sensor[5] if sensor else None,
        "time": sensor[6] if sensor else None,
        "water_liters": water[0] or 0,

        # 🔥 NUEVO (DHT11)
        "dht_temperature": dht[0] if dht else None,
        "dht_humidity": dht[1] if dht else None
    })

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

    return jsonify([
        {
            "type": r[0],
            "level": r[1],
            "message": r[2],
            "value": r[3],
            "time": r[4]
        }
        for r in rows
    ])
