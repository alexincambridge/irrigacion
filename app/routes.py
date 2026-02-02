from flask import Blueprint, render_template, jsonify, redirect, url_for, request
from flask_login import login_required
from app.db import get_db

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
        "temperature": sensor["temperature"],
        "humidity": sensor["humidity"],
        "solar": sensor["solar"],
        "pressure": sensor["pressure"],
        "ec": sensor["ec"],
        "ph": sensor["ph"],
        "time": sensor["timestamp"],
        "water_liters": water[0] or 0,
        "water_cost": water[1] or 0
    })


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
