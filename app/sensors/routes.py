from flask import Blueprint, render_template, jsonify
from app.db import get_db
from app.auth import login_required

routes = Blueprint("sensors", __name__)


@routes.route("/sensors")
@login_required
def dashboard():
    return render_template("sensors.html")


@routes.route("/dashboard/dht")
@login_required
def dashboard_dht():
    db = get_db()
    rows = db.execute("""
        SELECT temperature, humidity
        FROM dht_readings
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    return jsonify([
        {
            "temperature": r[0],
            "humidity": r[1]
        } for r in rows
    ])
