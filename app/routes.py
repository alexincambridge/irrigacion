from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models import get_db

routes = Blueprint("routes", __name__)

@routes.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

from flask import Blueprint, jsonify
from flask_login import login_required
from app.models import get_db

routes = Blueprint("routes", __name__)

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
        return jsonify({
            "temperature": None,
            "humidity": None,
            "solar": None,
            "pressure": None,
            "ec": None,
            "ph": None,
            "time": None
        })

    return jsonify({
        "temperature": row[0],
        "humidity": row[1],
        "solar": row[2],
        "pressure": row[3],
        "ec": row[4],
        "ph": row[5],
        "time": row[6]
    })

@routes.route("/history")
@login_required
def history():
    db = get_db()
    rows = db.execute("""
        SELECT temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 100
    """).fetchall()

    return jsonify([
        {
            "temperature": r[0],
            "humidity": r[1],
            "time": r[2]
        } for r in reversed(rows)
    ])
