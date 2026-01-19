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
        return jsonify({})

    return jsonify(dict(row))


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

    return jsonify([dict(r) for r in reversed(rows)])