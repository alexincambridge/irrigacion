@routes.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html")

@routes.route("/history")
@login_required
def history():
    return render_template("history.html")

@routes.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

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

