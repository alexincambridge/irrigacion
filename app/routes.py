from flask import Blueprint, render_template, jsonify
from flask_login import login_required


routes = Blueprint("routes", __name__)

@routes.route("/")
@login_required
def dashboard():
    return "<h1>DASHBOARD OK</h1>"

@routes.route("/sensors")
@login_required
def sensors():
    return render_template("sensors.html")

@routes.route("/history")
@login_required
def history():
    db = get_db()
    rows = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 200
    """).fetchall()

    return jsonify([
        {
            "temperature": r[0],
            "humidity": r[1],
            "solar": r[2],
            "pressure": r[3],
            "ec": r[4],
            "ph": r[5],
            "timestamp": r[6]
        } for r in reversed(rows)
    ])
