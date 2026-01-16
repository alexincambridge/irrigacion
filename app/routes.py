from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.hardware import read_dht
from app.models import get_db

routes = Blueprint("routes", __name__)

@routes.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

@routes.route("/data")
@login_required
def data():
    t,h = read_dht()
    db = get_db()
    if t and h:
        db.execute("INSERT INTO sensor_data(temperature,humidity) VALUES(?,?)",(t,h))
        db.commit()
    return jsonify({"temperature":t,"humidity":h})

@routes.route("/history")
@login_required
def history():
    db = get_db()
    rows = db.execute("""
        SELECT temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 50
    """).fetchall()

    return jsonify([
        {
            "temperature": r[0],
            "humidity": r[1],
            "time": r[2]
        } for r in reversed(rows)
    ])

