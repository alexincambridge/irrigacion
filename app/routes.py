@routes.route("/irrigation/schedule/add", methods=["POST"])
@login_required
def schedule_add_ajax():
    try:
        from datetime import datetime
        from flask import request, jsonify

        data = request.get_json()
        print("DATA:", data)

        if not data:
            return jsonify({"error": "No JSON recibido"}), 400

        sector = int(data.get("sector"))
        date = data.get("date")
        start = data.get("start")
        end = data.get("end")

        if not all([sector, date, start, end]):
            return jsonify({"error": "Datos incompletos"}), 400

        start_dt = datetime.strptime(f"{date} {start}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date} {end}", "%Y-%m-%d %H:%M")

        duration = int((end_dt - start_dt).total_seconds() / 60)

        if duration <= 0:
            return jsonify({"error": "Hora fin inválida"}), 400

        if duration > 60:
            return jsonify({"error": "Máximo 60 minutos"}), 400

        if duration not in [15, 30, 45, 60]:
            return jsonify({"error": "Solo 15, 30, 45 o 60 minutos"}), 400

        db = get_db()

        count = db.execute("""
            SELECT COUNT(*)
            FROM irrigation_schedule
            WHERE sector = ?
              AND date = ?
        """, (sector, date)).fetchone()[0]

        if count >= 3:
            return jsonify({"error": "Máximo 3 riegos por sector por día"}), 400

        db.execute("""
            INSERT INTO irrigation_schedule
            (sector, date, start_time, end_time, duration, enabled)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (sector, date, start, end, duration))

        db.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500
