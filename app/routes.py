from flask import Blueprint, render_template, jsonify, redirect, url_for
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


from flask import request
from app.hardware import irrigation_on, irrigation_off, irrigation_status

@routes.route("/irrigation")
@login_required
def irrigation():
    return render_template("irrigation.html")

@routes.route("/irrigation/status")
@login_required
def irrigation_status_api():
    return jsonify({"on": irrigation_status()})

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

