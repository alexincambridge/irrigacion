from flask import Blueprint, jsonify
from datetime import datetime
from app.models import get_db

irrigation_bp = Blueprint("irrigation", __name__, url_prefix="/irrigation")

@irrigation_bp.route("/toggle/<int:zone_id>", methods=["POST"])
def toggle_zone(zone_id):
    db = get_db()
    zone = db.execute(
        "SELECT is_active FROM irrigation_zones WHERE id=?",
        (zone_id,)
    ).fetchone()

    now = datetime.now().isoformat()

    if zone["is_active"]:
        db.execute("""
            UPDATE irrigation_zones
            SET is_active=0, started_at=NULL
            WHERE id=?
        """, (zone_id,))
    else:
        db.execute("""
            UPDATE irrigation_zones
            SET is_active=1, started_at=?
            WHERE id=?
        """, (now, zone_id))

    db.commit()
    return jsonify({"ok": True})
