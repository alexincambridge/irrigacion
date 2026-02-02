from flask import Blueprint, jsonify
from app.db import get_db
from app.gpio import relay_on, relay_off
from datetime import datetime

irrigation = Blueprint("irrigacion", __name__)

@irrigation.route("/irrigacion/toggle/<int:zone_id>", methods=["POST"])
def toggle_zone(zone_id):
    db = get_db()

    zone = db.execute(
        "SELECT gpio_pin, is_active FROM irrigacion_zones WHERE id=?",
        (zone_id,)
    ).fetchone()

    if not zone:
        return jsonify({"error": "Zona no existe"}), 404

    pin, active = zone

    if active:
        relay_off(pin)
        db.execute("""
            UPDATE irrigacion_zones
            SET is_active=0, started_at=NULL
            WHERE id=?
        """, (zone_id,))
    else:
        relay_on(pin)
        db.execute("""
            UPDATE irrigacion_zones
            SET is_active=1, started_at=?
            WHERE id=?
        """, (datetime.now(), zone_id))

    db.commit()
    return jsonify({"ok": True})
