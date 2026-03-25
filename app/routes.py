from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.db import get_db
from datetime import datetime

routes = Blueprint("routes", __name__)

# --------------------
# USER & SYSTEM INFO
# --------------------
@routes.route("/api/current-user")
@login_required
def get_current_user():
    """Get current logged-in user information"""
    return jsonify({
        "username": current_user.username if hasattr(current_user, 'username') else 'Usuario',
        "email": getattr(current_user, 'email', '')
    })

# --------------------
# DASHBOARD
# --------------------
@routes.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@routes.route("/dashboard/data")
@login_required
def dashboard_data():
    db = get_db()
    sensor = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()
    water = db.execute("SELECT SUM(liters) FROM water_consumption").fetchone()
    dht = db.execute("""
        SELECT temperature, humidity
        FROM dht_readings
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()
    return jsonify({
        "temperature": sensor[0] if sensor else None,
        "humidity": sensor[1] if sensor else None,
        "solar": sensor[2] if sensor else None,
        "pressure": sensor[3] if sensor else None,
        "ec": sensor[4] if sensor else None,
        "ph": sensor[5] if sensor else None,
        "time": sensor[6] if sensor else None,
        "water_liters": water[0] or 0,
        "dht_temperature": dht[0] if dht else None,
        "dht_humidity": dht[1] if dht else None
    })

@routes.route("/dashboard/history")
@login_required
def dashboard_history():
    """Obtener histórico de sensores de las últimas 24 horas"""
    try:
        db = get_db()
        from datetime import datetime, timedelta

        # Últimas 24 horas
        since = (datetime.now() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

        rows = db.execute("""
            SELECT temperature, humidity, pressure, solar, ec, ph, timestamp
            FROM sensor_data
            WHERE timestamp > ?
            ORDER BY timestamp ASC
            LIMIT 500
        """, (since,)).fetchall()

        history = []
        for row in rows:
            history.append({
                "temperature": row[0],
                "humidity": row[1],
                "pressure": row[2],
                "solar": row[3],
                "ec": row[4],
                "ph": row[5],
                "timestamp": row[6]
            })

        return jsonify(history)
    except Exception as e:
        print(f"Error fetching dashboard history: {e}")
        return jsonify({"error": str(e)}), 500

# --------------------
# WATER CONSUMPTION
# --------------------
@routes.route("/water")
@login_required
def water_consumption():
    db = get_db()
    total = db.execute("SELECT SUM(liters), SUM(cost) FROM water_consumption").fetchone()
    return render_template("water.html", liters=total[0] or 0, cost=total[1] or 0)

@routes.route("/water/data")
@login_required
def water_data():
    db = get_db()
    rows = db.execute("SELECT timestamp, liters FROM water_consumption ORDER BY timestamp ASC LIMIT 50").fetchall()
    return jsonify([{"time": r[0], "liters": r[1]} for r in rows])

# --------------------
# ALARMS
# --------------------
@routes.route("/alarms")
@login_required
def alarms():
    db = get_db()
    rows = db.execute("""
        SELECT type, level, message, value, created_at
        FROM alarms
        ORDER BY created_at DESC
        LIMIT 20
    """).fetchall()
    return jsonify([{"type": r[0], "level": r[1], "message": r[2], "value": r[3], "time": r[4]} for r in rows])

# --------------------
# IRRIGATION
# --------------------

# Página de riego
@routes.route("/irrigation")
@login_required
def irrigation():
    return render_template("irrigation.html")

@routes.route("/fertilization")
@login_required
def fertilization():
    return render_template("fertilization.html")

@routes.route("/api/fertilize", methods=["POST"])
@login_required
def apply_fertilizer():
    """Apply a fertilization recipe (activates Zone 4 + peristaltic pump)"""
    try:
        from app.config import HARDWARE_MODE
    except ImportError:
        HARDWARE_MODE = 'GPIO'

    data = request.get_json()
    recipe = data.get("recipe", "General")
    duration_minutes = data.get("duration", 30)

    # Zone 4 is for Trees
    ZONE_ID = 4
    duration_seconds = duration_minutes * 60

    try:
        # Activate zone 4 (irrigation valve)
        from app.hardware_manager import zone_on as hw_zone_on, pump_on as hw_pump_on

        success_zone = hw_zone_on(ZONE_ID, duration_seconds)
        success_pump = hw_pump_on(duration_seconds)

        if success_zone or success_pump:
            # Log it
            db = get_db()
            db.execute("""
                INSERT INTO irrigation_log 
                (sector, start_time, end_time, type) 
                VALUES (?, datetime('now'), datetime('now', '+' || ? || ' seconds'), ?)
            """, (ZONE_ID, duration_seconds, f"Fertilizacion: {recipe}"))
            db.commit()

            return jsonify({"success": True, "message": f"Fertilización '{recipe}' iniciada por {duration_minutes} min (Zona 4 + Bomba)"})
        else:
            return jsonify({"success": False, "error": "No se pudo iniciar (hardware error)"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Crear riego programado
@routes.route("/irrigation/schedule/add", methods=["POST"])
@login_required
def schedule_add():
    try:

        data = request.get_json()

        sector = int(data.get("sector"))
        date = data.get("date")
        start_time = data.get("start_time")[:5]
        end_time = data.get("end_time")[:5]
        repeat_days = data.get("repeat_days", "")
        repeat_enabled = int(data.get("repeat_enabled", 0))
        origin = data.get("origin", "manual")

        # Calcular duración en minutos
        start_hour, start_min = map(int, start_time.split(':'))
        end_hour, end_min = map(int, end_time.split(':'))

        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min
        duration_minutes = end_minutes - start_minutes

        db = get_db()

        # Determinar prioridad por sector (nueva)
        priority_map = {
            4: 1,  # Árboles - Prioridad 1
            1: 2,  # Jardín - Prioridad 2
            2: 3,  # Huerta - Prioridad 3
            3: 4   # Césped - Prioridad 4
        }
        priority = priority_map.get(sector, 0)

        db.execute("""
            INSERT INTO irrigation_schedule 
            (sector, date, start_time, end_time, duration, duration_minutes, status, priority, 
             repeat_days, repeat_enabled, origin, enabled)
            VALUES (?, ?, ?, ?, ?, ?, 'en espera', ?, ?, ?, ?, 1)
        """, (sector, date, start_time, end_time, duration_minutes, duration_minutes, priority,
              repeat_days, repeat_enabled, origin))

        db.commit()

        return jsonify({"success": True})

    except Exception as e:
        print("🔥 ERROR REAL:", e)
        return jsonify({"error": str(e)}), 500

@routes.route("/irrigation/schedule/list")
@login_required
def schedule_list():
    try:
        db = get_db()

        # Primero, eliminar riegos que ya terminaron
        from datetime import datetime
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        # Intentar obtener riegos vencidos con nuevos campos
        try:
            vencidos = db.execute("""
                SELECT id, sector, start_time, end_time, duration_minutes
                FROM irrigation_schedule
                WHERE enabled = 1
                AND datetime(date || ' ' || end_time) <= ?
            """, (current_datetime,)).fetchall()

            # Registrar en log y eliminar
            for row in vencidos:
                schedule_id = row[0]
                sector = row[1]
                start_time = row[2]
                end_time = row[3]
                duration_minutes = row[4] if len(row) > 4 else None

                # Registrar finalización en log si no está ya registrado
                try:
                    db.execute("""
                        INSERT OR IGNORE INTO irrigation_log 
                        (sector, start_time, end_time, type, scheduled_id, duration_minutes, status)
                        VALUES (?, ?, ?, 'programado', ?, ?, 'completado')
                    """, (sector, f"{now.strftime('%Y-%m-%d')} {start_time}",
                          f"{now.strftime('%Y-%m-%d')} {end_time}", schedule_id, duration_minutes))
                except:
                    # Si falla, usar campos básicos
                    db.execute("""
                        INSERT OR IGNORE INTO irrigation_log (sector, start_time, end_time, type)
                        VALUES (?, ?, ?, 'programado')
                    """, (sector, f"{now.strftime('%Y-%m-%d')} {start_time}",
                          f"{now.strftime('%Y-%m-%d')} {end_time}"))

                # Marcar como no activo
                db.execute("""
                    UPDATE irrigation_schedule
                    SET enabled = 0
                    WHERE id = ?
                """, (schedule_id,))

            db.commit()
        except Exception as e:
            print(f"Warning in vencidos check: {e}")

        # Intentar obtener schedules con nuevos campos
        try:
            rows = db.execute("""
                SELECT id, sector, date, start_time, end_time, duration_minutes, priority, status, 
                       repeat_days, repeat_enabled, origin
                FROM irrigation_schedule
                WHERE enabled = 1
                ORDER BY priority ASC, date ASC, start_time ASC
                LIMIT 10
            """).fetchall()

            schedules = []
            for r in rows:
                schedules.append({
                    "id": r[0],
                    "sector": r[1],
                    "date": r[2],
                    "start_time": r[3],
                    "end_time": r[4],
                    "duration_minutes": r[5],
                    "priority": r[6],
                    "status": r[7],
                    "repeat_days": r[8],
                    "repeat_enabled": r[9],
                    "origin": r[10],
                    "enabled": 1  # Sabemos que enabled=1 porque es el WHERE
                })
        except Exception as e:
            # Si falla, usar campos básicos
            print(f"Warning: Using basic fields for schedule: {e}")
            rows = db.execute("""
                SELECT id, sector, date, start_time
                FROM irrigation_schedule
                WHERE enabled = 1
                ORDER BY date ASC, start_time ASC
                LIMIT 10
            """).fetchall()

            schedules = []
            for r in rows:
                # Calcular end_time como start_time + 30 min (default)
                start_h, start_m = map(int, r[3].split(':'))
                end_m = start_m + 30
                end_h = start_h + (end_m // 60)
                end_m = end_m % 60
                end_time = f"{end_h:02d}:{end_m:02d}"

                schedules.append({
                    "id": r[0],
                    "sector": r[1],
                    "date": r[2],
                    "start_time": r[3],
                    "end_time": end_time,
                    "duration_minutes": 30,
                    "priority": 0,
                    "status": "en espera",
                    "repeat_days": "",
                    "repeat_enabled": 0,
                    "origin": "manual",
                    "enabled": 1
                })

        return jsonify(schedules)
    except Exception as e:
        print(f"Error in schedule_list: {e}")
        return jsonify({"error": str(e)}), 500

@routes.route("/irrigation/schedule/delete/<int:schedule_id>", methods=["DELETE"])
@login_required
def schedule_delete(schedule_id):

    db = get_db()

    db.execute("""
        DELETE FROM irrigation_schedule
        WHERE id = ?
    """, (schedule_id,))

    db.commit()

    return jsonify({"success": True})


@routes.route("/irrigation/manual/<int:sector>", methods=["POST"])
@login_required
def irrigation_manual(sector):

    from app.hardware_manager import zone_on, zone_off, zone_state

    db = get_db()

    is_active = zone_state(sector)

    if is_active:
        zone_off(sector)
        db.execute("""
            UPDATE irrigation_log
            SET end_time = ?
            WHERE sector = ? AND end_time IS NULL
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sector))
    else:
        zone_on(sector)
        db.execute("""
            INSERT INTO irrigation_log (sector, start_time, type)
            VALUES (?, ?, 'manual')
        """, (sector, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    db.commit()

    return jsonify({
        "success": True,
        "active": not is_active,  # Return new state
        "sector": sector
    })


# @routes.route("/irrigation/schedule", methods=["POST"])
# @login_required
# def add_schedule():
#     data = request.json
#     sector = data.get("sector")
#     date = data.get("date")
#     start_time = data.get("time")
#
#     if not all([sector, date, start_time]):
#         return jsonify({"success": False, "message": "Datos incompletos"}), 400
#
#     db = get_db()
#     db.execute("""
#         INSERT INTO irrigation_schedule (sector, date, start_time, enabled)
#         VALUES (?, ?, ?, 1)
#     """, (sector, date, start_time))
#     db.commit()
#     return jsonify({"success": True})

# Obtener riegos programados pendientes (max 10)
@routes.route("/irrigation/schedule", methods=["GET"])
@login_required
def get_schedules():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, date, start_time
        FROM irrigation_schedule
        WHERE enabled=1 AND (date || ' ' || start_time) > ?
        ORDER BY date ASC, start_time ASC
        LIMIT 10
    """, (now_str,)).fetchall()
    schedules = [dict(r) for r in rows]
    return jsonify(schedules)

# Cancelar riego programado
@routes.route("/irrigation/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def delete_schedule(schedule_id):
    db = get_db()
    db.execute("DELETE FROM irrigation_schedule WHERE id=?", (schedule_id,))
    db.commit()
    return jsonify({"success": True})

# Get zone status for real-time updates
@routes.route("/irrigation/zones/status")
@login_required
def zones_status():
    try:
        from app.hardware_manager import zone_state

        zones = {}
        for zone_id in range(1, 5):  # Zones 1-4
            zones[zone_id] = {
                "active": zone_state(zone_id),
                "duration": 0  # Can be enhanced with timer tracking
            }

        return jsonify({
            "success": True,
            "zones": zones
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "zones": {}
        })

# Get irrigation history asynchronously
@routes.route("/irrigation/history/list")
@login_required
def history_list():
    try:
        db = get_db()

        # Intentar con todos los campos nuevos
        try:
            rows = db.execute("""
                SELECT sector, start_time, end_time, type, duration_minutes, status, id, scheduled_id
                FROM irrigation_log
                ORDER BY id DESC
                LIMIT 50
            """).fetchall()

            history = []
            for row in rows:
                history.append({
                    "id": row[6],
                    "sector": row[0],
                    "start_time": row[1],
                    "end_time": row[2],
                    "type": row[3],
                    "duration_minutes": row[4],
                    "status": row[5],
                    "scheduled_id": row[7]
                })
        except Exception as e:
            # Si falla, usar campos básicos (BD antigua)
            print(f"Warning: Using basic fields for irrigation_log: {e}")
            rows = db.execute("""
                SELECT sector, start_time, end_time, type, id
                FROM irrigation_log
                ORDER BY id DESC
                LIMIT 50
            """).fetchall()

            history = []
            for row in rows:
                history.append({
                    "id": row[4],
                    "sector": row[0],
                    "start_time": row[1],
                    "end_time": row[2],
                    "type": row[3],
                    "duration_minutes": None,
                    "status": None,
                    "scheduled_id": None
                })

        return jsonify(history)
    except Exception as e:
        print(f"Error in history_list: {e}")
        return jsonify({"error": str(e)}), 500

# Emergency stop - turn off all zones
@routes.route("/irrigation/emergency-stop", methods=["POST"])
@login_required
def emergency_stop():
    try:
        from app.hardware_manager import all_off

        all_off()

        # Update database - close all open irrigation logs
        db = get_db()
        db.execute("""
            UPDATE irrigation_log
            SET end_time = ?
            WHERE end_time IS NULL
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
        db.commit()

        return jsonify({
            "success": True,
            "message": "All zones stopped"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Activar / desactivar riego manual
@routes.route("/irrigation/manual", methods=["POST"])
@login_required
def manual_irrigate():
    data = request.json
    sector = data.get("sector")
    action = data.get("action")  # "start" o "stop"

    if not sector or action not in ["start", "stop"]:
        return jsonify({"success": False}), 400

    db = get_db()
    if action == "start":
        db.execute("""
            INSERT INTO irrigation_log (sector, start_time, type)
            VALUES (?, CURRENT_TIMESTAMP, 'manual')
        """, (sector,))
    else:
        db.execute("""
            UPDATE irrigation_log
            SET end_time=CURRENT_TIMESTAMP
            WHERE sector=? AND type='manual' AND end_time IS NULL
        """, (sector,))
    db.commit()
    return jsonify({"success": True})

# Obtener historial de riegos (últimos 10)
@routes.route("/irrigation/log", methods=["GET"])
@login_required
def get_irrigation_log():
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()
    log = [dict(r) for r in rows]
    return jsonify(log)

@routes.route("/irrigation/history")
@login_required
def irrigation_history():
    db = get_db()
    rows = db.execute("""
        SELECT id, sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()
    return render_template("irrigation_history.html", rows=rows)

@routes.route("/logs")
@login_required
def irrigation_logs():

    db = get_db()

    rows = db.execute("""
        SELECT sector, start_time, end_time, type
        FROM irrigation_log
        ORDER BY start_time DESC
        LIMIT 50
    """).fetchall()

    logs = []

    for r in rows:
        logs.append({
            "sector": r[0],
            "start_time": r[1],
            "end_time": r[2],
            "type": r[3]
        })

    return render_template("logs.html", logs=logs)

# --------------------
# HARDWARE STATUS
# --------------------
@routes.route("/hardware/status")
@login_required
def hardware_status():
    """Get hardware connection status and signal quality"""
    try:
        from app.hardware_manager import get_hardware_info, check_connection

        info = get_hardware_info()
        info['connected'] = check_connection()

        return jsonify(info)
    except ImportError:
        # Fallback if hardware_lora doesn't exist yet
        return jsonify({
            'mode': 'GPIO',
            'zones': 4,
            'active_zones': [],
            'connected': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------
# SYSTEM
# --------------------
@routes.route("/system")
@login_required
def system():
    """Página de información del sistema"""
    import socket
    import platform
    import sys

    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    # Get hostname
    hostname = socket.gethostname()

    # Get gateway (approximate)
    gateway = ".".join(local_ip.split(".")[:-1]) + ".1"

    # OS info
    os_info = f"{platform.system()} {platform.release()}"

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    return render_template(
        "system.html",
        local_ip=local_ip,
        hostname=hostname,
        gateway=gateway,
        os_info=os_info,
        python_version=python_version
    )

@routes.route("/system/internet-check")
@login_required
def system_internet_check():
    """Check internet connectivity"""
    import urllib.request
    import json

    try:
        # Try to get public IP
        response = urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5)
        data = json.loads(response.read().decode('utf-8'))
        public_ip = data.get('ip', 'Unknown')

        # Try to get ISP info
        try:
            isp_response = urllib.request.urlopen(f'https://ipapi.co/{public_ip}/json/', timeout=5)
            isp_data = json.loads(isp_response.read().decode('utf-8'))
            isp = isp_data.get('org', 'Unknown')
        except:
            isp = 'Unknown'

        return jsonify({
            "connected": True,
            "public_ip": public_ip,
            "isp": isp
        })
    except Exception as e:
        return jsonify({
            "connected": False,
            "public_ip": None,
            "isp": None,
            "error": str(e)
        })

@routes.route("/system/esp32-devices")
@login_required
def system_esp32_devices():
    """Scan for ESP32 devices on the network"""
    import socket

    # Get local network
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network_prefix = ".".join(local_ip.split(".")[:-1])
    except:
        network_prefix = "192.168.1"

    devices = []

    # Check for known ESP32 devices (you can expand this list)
    # In a real scenario, you'd scan the network or check a configuration
    known_esp32_ips = [
        f"{network_prefix}.100",
        f"{network_prefix}.101",
        f"{network_prefix}.102",
        f"{network_prefix}.103"
    ]

    for i, ip in enumerate(known_esp32_ips):
        # Try to ping or check if device responds
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, 80))  # Try HTTP port
            online = (result == 0)
            sock.close()

            if online:
                devices.append({
                    "name": f"ESP32-{i+1}",
                    "ip": ip,
                    "mac": f"AA:BB:CC:DD:EE:{i:02d}",
                    "zones": 4,
                    "online": True,
                    "last_seen": "Ahora"
                })
        except:
            pass

    return jsonify({"devices": devices})

@routes.route("/system/water-total")
@login_required
def system_water_total():
    """Get total water consumption"""
    db = get_db()
    total = db.execute("SELECT SUM(liters) FROM water_consumption").fetchone()
    return jsonify({"total": total[0] or 0})

@routes.route("/system/logs-count")
@login_required
def system_logs_count():
    """Get total logs count"""
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM irrigation_log").fetchone()
    return jsonify({"count": count[0] or 0})

# --------------------
# PERIPHERALS / HEALTH CHECK
# --------------------
@routes.route("/peripherals")
@login_required
def peripherals():
    """Página de estado de periféricos"""
    return render_template("peripherals.html")

@routes.route("/api/peripherals/status")
@login_required
def peripherals_status():
    """Check status of all peripherals and return JSON"""
    from app.config import HARDWARE_MODE, PERIPHERALS
    peripherals_config = PERIPHERALS

    results = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for key, cfg in peripherals_config.items():
        device = {
            "id": key,
            "name": cfg["name"],
            "type": cfg["type"],
            "status": "unknown",
            "message": "",
            "last_seen": now_str,
            "detail": ""
        }

        try:
            if cfg["type"] == "relay":
                # Check relay GPIO
                gpio_pin = cfg["gpio"]
                try:
                    from app.hardware_manager import zone_state, ZONE_PINS
                    # Find zone_id for this pin
                    zone_id = None
                    for zid, pin in ZONE_PINS.items():
                        if pin == gpio_pin:
                            zone_id = zid
                            break

                    if zone_id is not None:
                        is_active = zone_state(zone_id)
                        if is_active:
                            device["status"] = "active"
                            device["message"] = "Regando"
                            device["detail"] = f"GPIO {gpio_pin} - HIGH"
                        else:
                            device["status"] = "ok"
                            device["message"] = "Listo (en reposo)"
                            device["detail"] = f"GPIO {gpio_pin} - LOW"
                    else:
                        device["status"] = "idle"
                        device["message"] = "Pin no mapeado"
                except ImportError:
                    # On macOS/dev, no GPIO
                    device["status"] = "idle"
                    device["message"] = "GPIO no disponible (modo simulación)"
                    device["detail"] = f"GPIO {gpio_pin}"

            elif cfg["type"] == "sensor" and key == "dht22":
                # Try reading DHT22
                try:
                    db = get_db()
                    last = db.execute("""
                        SELECT temperature, humidity, timestamp 
                        FROM dht_readings 
                        ORDER BY id DESC LIMIT 1
                    """).fetchone()

                    if last:
                        device["status"] = "ok"
                        device["message"] = f"T: {last[0]}°C | H: {last[1]}%"
                        device["last_seen"] = str(last[2]) if last[2] else now_str
                        device["detail"] = f"GPIO {cfg['gpio']}"
                    else:
                        device["status"] = "idle"
                        device["message"] = "Sin lecturas recientes"
                        device["detail"] = f"GPIO {cfg['gpio']}"
                except Exception as e:
                    device["status"] = "error"
                    device["message"] = f"Error: {str(e)[:50]}"

            elif cfg["type"] == "sensor" and key == "fertilizer_counter":
                # Fertilizer counter - check GPIO
                try:
                    from app.gpio import setup_pin, read_pin
                    device["status"] = "idle"
                    device["message"] = "En reposo"
                    device["detail"] = f"GPIO {cfg['gpio']}"
                except ImportError:
                    device["status"] = "idle"
                    device["message"] = "GPIO no disponible"


            elif cfg["type"] == "actuator" and key == "pump":
                # Peristaltic pump
                try:
                    from app.hardware_manager import pump_state
                    if pump_state():
                        device["status"] = "active"
                        device["message"] = "Bomba activa (inyectando)"
                    else:
                        device["status"] = "ok"
                        device["message"] = "Bomba en espera"
                    device["detail"] = f"GPIO {cfg['gpio']}"
                except ImportError:
                    device["status"] = "idle"
                    device["message"] = "GPIO no disponible"

            elif cfg["type"] == "esp32":
                # ESP32 via LoRa
                try:
                    if HARDWARE_MODE == 'LORA':
                        from app.lora_controller import get_lora_controller
                        lora = get_lora_controller()
                        if lora and lora.ping():
                            device["status"] = "ok"
                            device["message"] = "Conectado vía LoRa"
                            quality = lora.get_signal_quality()
                            if quality:
                                device["detail"] = f"RSSI: {quality.get('rssi', '?')} dBm"
                        else:
                            device["status"] = "error"
                            device["message"] = "Sin respuesta LoRa"
                    else:
                        device["status"] = "idle"
                        device["message"] = f"Modo {HARDWARE_MODE} (LoRa desactivado)"
                except Exception as e:
                    device["status"] = "error"
                    device["message"] = f"Error LoRa: {str(e)[:50]}"

        except Exception as e:
            device["status"] = "error"
            device["message"] = f"Error: {str(e)[:60]}"

        results.append(device)

    # Also check database health
    try:
        db = get_db()
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        db_status = {
            "id": "database",
            "name": "Base de Datos SQLite",
            "type": "system",
            "status": "ok",
            "message": f"{len(tables)} tablas activas",
            "last_seen": now_str,
            "detail": "irrigation.db"
        }
    except Exception as e:
        db_status = {
            "id": "database",
            "name": "Base de Datos SQLite",
            "type": "system",
            "status": "error",
            "message": str(e)[:60],
            "last_seen": now_str,
            "detail": ""
        }
    results.append(db_status)

    return jsonify(results)

@routes.route("/api/pump/on", methods=["POST"])
@login_required
def pump_on_route():
    """Turn on peristaltic pump"""
    try:
        data = request.get_json() or {}
        duration = data.get("duration", 300)  # default 5 min
        from app.hardware_manager import pump_on
        pump_on(duration)
        return jsonify({"success": True, "message": f"Bomba encendida ({duration}s)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@routes.route("/api/pump/off", methods=["POST"])
@login_required
def pump_off_route():
    """Turn off peristaltic pump"""
    try:
        from app.hardware_manager import pump_off
        pump_off()
        return jsonify({"success": True, "message": "Bomba apagada"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

