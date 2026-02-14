from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.db import get_db
from app.hardware import zone_on, zone_off, zone_state

irrigation = Blueprint("irrigation", __name__)


@irrigation.route("/irrigation/status")
@login_required
def irrigation_status():
    db = get_db()
    zones = db.execute("""
        SELECT id, started_at, is_active
        FROM irrigation_zones
    """).fetchall()

    return jsonify([
        {
            "id": z["id"],
            "is_active": bool(z["is_active"]),
            "started_at": z["started_at"]
        }
        for z in zones
    ])

@irrigation.route("/irrigation/toggle/<int:zone_id>", methods=["POST"])
@login_required
def irrigation_toggle(zone_id):
    db = get_db()

    if zone_state(zone_id):
        zone_off(zone_id)
        db.execute("""
            INSERT INTO irrigation_records (sector, start_datetime, end_datetime, type)
            VALUES (?, datetime('now'), '', 'manual')
        """, (zone_id,))
    else:
        zone_on(zone_id)
        db.execute("""
            UPDATE irrigation_records
            SET end_datetime = datetime('now')
            WHERE sector = ?
              AND type = 'manual'
              AND end_datetime = ''
        """, (zone_id,))

    db.commit()
    return jsonify({"ok": True})
