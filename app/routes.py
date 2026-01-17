from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models import get_db

routes = Blueprint("routes", __name__)

@routes.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

@routes.route("/latest")
@login_required
def latest():
    db = get_db()
    row = db.execute("""
        SELECT temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    return jsonify({
        "temperature": row[0] if row else None,
        "humidity": row[1] if row else None,
        "time": row[2] if row else None
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
