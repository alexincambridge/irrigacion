from flask import render_template


@routes.route("/sensors")
@login_required
def dashboard():
    return render_template("sensors.html")


@routes.route("/dashboard/dht")
@login_required
def dashboard_dht():
    db = get_db()
    rows = db.execute("""
        SELECT temperature, humidity, timestamp
        FROM dht_readings
        ORDER BY timestamp DESC
        LIMIT 10
    """).fetchall()

    return jsonify([
        {
            "temperature": r[0],
            "humidity": r[1],
            "time": r[2]
        } for r in rows
    ])
