from flask import Blueprint, jsonify
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
            UPDATE irrigation_zones
            SET is_active=0, started_at=NULL
            WHERE id=?
        """, (zone_id,))
    else:
        zone_on(zone_id)
        db.execute("""
            UPDATE irrigation_zones
            SET is_active=1, started_at=datetime('now')
            WHERE id=?
        """, (zone_id,))

    db.commit()
    return jsonify({"ok": True})
