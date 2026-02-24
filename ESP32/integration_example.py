"""
Example: Integration of LoRa-based ESP32 control with existing irrigation system
"""

from flask import Flask, jsonify, request
from app.lora_controller import get_lora_controller
from app.hardware_lora import zone_on, zone_off, get_all_zones_status, check_connection
from app.db import get_db
from datetime import datetime

# Initialize Flask app (this would be in your main app)
app = Flask(__name__)

# Get LoRa controller instance
lora = get_lora_controller()


# Example 1: Manual valve control with duration
@app.route("/api/irrigation/valve/<int:valve_id>/on", methods=["POST"])
def turn_valve_on(valve_id):
    """
    Turn on a valve with optional duration

    POST /api/irrigation/valve/1/on
    Body: {"duration": 300}  # 300 seconds = 5 minutes
    """
    data = request.get_json() or {}
    duration = data.get("duration", 0)  # 0 = manual mode (no auto-off)

    # Turn on valve via LoRa
    success = zone_on(valve_id, duration)

    if success:
        # Log to database
        db = get_db()
        db.execute("""
            INSERT INTO irrigation_log 
            (sector, start_time, end_time, type) 
            VALUES (?, datetime('now'), '', 'manual')
        """, (valve_id,))
        db.commit()

        return jsonify({
            "success": True,
            "valve_id": valve_id,
            "duration": duration,
            "message": f"Valve {valve_id} turned on" +
                      (f" for {duration} seconds" if duration > 0 else " (manual mode)")
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to communicate with ESP32"
        }), 500


# Example 2: Turn off valve
@app.route("/api/irrigation/valve/<int:valve_id>/off", methods=["POST"])
def turn_valve_off(valve_id):
    """
    Turn off a valve

    POST /api/irrigation/valve/1/off
    """
    success = zone_off(valve_id)

    if success:
        # Update database
        db = get_db()
        db.execute("""
            UPDATE irrigation_log 
            SET end_time = datetime('now')
            WHERE sector = ? 
              AND end_time = ''
            ORDER BY start_time DESC 
            LIMIT 1
        """, (valve_id,))
        db.commit()

        return jsonify({
            "success": True,
            "valve_id": valve_id,
            "message": f"Valve {valve_id} turned off"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to communicate with ESP32"
        }), 500


# Example 3: Get all valves status
@app.route("/api/irrigation/status")
def get_status():
    """
    Get status of all valves and connection quality

    GET /api/irrigation/status
    """
    # Get valve states from ESP32
    status = get_all_zones_status()

    # Get signal quality
    signal = lora.get_signal_quality()

    # Check connection
    connected = check_connection()

    return jsonify({
        "connected": connected,
        "valves": status,
        "signal_quality": signal,
        "timestamp": datetime.now().isoformat()
    })


# Example 4: Emergency stop - turn off all valves
@app.route("/api/irrigation/emergency-stop", methods=["POST"])
def emergency_stop():
    """
    Emergency stop - turn off all valves immediately

    POST /api/irrigation/emergency-stop
    """
    from app.hardware_lora import all_off

    success = all_off()

    if success:
        # Log emergency stop
        db = get_db()
        db.execute("""
            UPDATE irrigation_log 
            SET end_time = datetime('now')
            WHERE end_time = ''
        """)
        db.commit()

        return jsonify({
            "success": True,
            "message": "All valves turned off"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Failed to communicate with ESP32"
        }), 500


# Example 5: Scheduled irrigation with LoRa
def run_scheduled_irrigation(valve_id, duration_minutes):
    """
    Run scheduled irrigation task
    Called by scheduler (app/scheduler.py)

    Args:
        valve_id: Valve number (1-4)
        duration_minutes: Duration in minutes
    """
    duration_seconds = duration_minutes * 60

    # Turn on valve with auto-off timer
    success = zone_on(valve_id, duration_seconds)

    if success:
        # Log to database
        db = get_db()
        db.execute("""
            INSERT INTO irrigation_log 
            (sector, start_time, end_time, type) 
            VALUES (?, datetime('now'), 
                    datetime('now', '+' || ? || ' seconds'), 
                    'scheduled')
        """, (valve_id, duration_seconds))
        db.commit()

        print(f"✅ Scheduled irrigation started: Valve {valve_id} for {duration_minutes} minutes")
        return True
    else:
        print(f"❌ Failed to start scheduled irrigation for Valve {valve_id}")
        return False


# Example 6: Monitor connection and auto-reconnect
def monitor_connection():
    """
    Periodically check LoRa connection
    Can be run as background task
    """
    import time

    while True:
        if not check_connection():
            print("⚠️  Lost connection to ESP32, attempting to reconnect...")

            # Try to ping
            if lora.ping():
                print("✅ Reconnected to ESP32")
            else:
                print("❌ Still no connection to ESP32")

                # Turn off all valves locally to be safe
                # (they should auto-off on ESP32 side with timers)
                pass

        time.sleep(30)  # Check every 30 seconds


# Example 7: Get signal quality for monitoring
@app.route("/api/irrigation/signal")
def get_signal_quality():
    """
    Get LoRa signal quality metrics

    GET /api/irrigation/signal
    """
    # Send a ping to get fresh signal data
    lora.ping()

    quality = lora.get_signal_quality()

    if quality:
        return jsonify({
            "rssi": quality['rssi'],
            "snr": quality['snr'],
            "quality_percent": quality['quality'],
            "status": "excellent" if quality['rssi'] > -70 else
                     "good" if quality['rssi'] > -90 else
                     "fair" if quality['rssi'] > -110 else "poor",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "error": "No signal data available"
        }), 404


# Example 8: Integration with existing irrigation routes
def integrate_with_existing_system():
    """
    Example of how to modify existing irrigation.py routes

    Replace hardware.zone_on/zone_off calls with:
    - app.hardware_lora.zone_on(zone_id, duration)
    - app.hardware_lora.zone_off(zone_id)
    """

    # In app/irrigation.py, change:
    # from app.hardware import zone_on, zone_off, zone_state
    #
    # To:
    # from app.hardware_lora import zone_on, zone_off, zone_state

    # That's it! The API stays the same, but now uses LoRa
    pass


# Example 9: Dashboard widget for signal quality
def get_dashboard_data():
    """
    Add LoRa status to dashboard
    Used in /dashboard/data route
    """
    db = get_db()

    # Existing sensor data
    sensor = db.execute("""
        SELECT temperature, humidity, solar, pressure, ec, ph, timestamp
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    # Add LoRa connection status
    connected = check_connection()
    signal = lora.get_signal_quality() if connected else None
    valve_status = get_all_zones_status()

    return {
        # Existing data
        "temperature": sensor[0] if sensor else None,
        "humidity": sensor[1] if sensor else None,
        # ... other sensor data ...

        # New LoRa data
        "lora_connected": connected,
        "lora_signal_rssi": signal['rssi'] if signal else None,
        "lora_signal_quality": signal['quality'] if signal else None,
        "active_valves": [v for v, state in valve_status.items() if state],
        "valve_status": valve_status
    }


# Example 10: Error handling and retry logic
def safe_valve_control(valve_id, action, duration=0, retries=3):
    """
    Control valve with automatic retry on failure

    Args:
        valve_id: Valve number (1-4)
        action: 'on' or 'off'
        duration: Duration in seconds (for 'on' action)
        retries: Number of retry attempts

    Returns:
        True if successful, False if all retries failed
    """
    import time

    for attempt in range(retries):
        try:
            if action == 'on':
                success = zone_on(valve_id, duration)
            elif action == 'off':
                success = zone_off(valve_id)
            else:
                return False

            if success:
                # Verify by checking status
                time.sleep(0.5)
                status = get_all_zones_status()
                expected_state = (action == 'on')

                if status.get(valve_id) == expected_state:
                    print(f"✅ Valve {valve_id} {action} confirmed")
                    return True
                else:
                    print(f"⚠️  Valve {valve_id} {action} not confirmed, retrying...")
            else:
                print(f"⚠️  Valve {valve_id} {action} failed, attempt {attempt + 1}/{retries}")

            if attempt < retries - 1:
                time.sleep(1)  # Wait before retry

        except Exception as e:
            print(f"❌ Error controlling valve {valve_id}: {e}")
            if attempt < retries - 1:
                time.sleep(1)

    print(f"❌ All {retries} attempts failed for valve {valve_id} {action}")
    return False


if __name__ == "__main__":
    """
    Test the integration
    """
    print("Testing LoRa Integration")
    print("=" * 50)

    # Test 1: Check connection
    print("\n1. Checking connection...")
    if check_connection():
        print("✅ ESP32 is connected")
    else:
        print("❌ ESP32 not responding")

    # Test 2: Get status
    print("\n2. Getting valve status...")
    status = get_all_zones_status()
    print(f"Valve status: {status}")

    # Test 3: Turn on valve 1 for 10 seconds
    print("\n3. Turning on valve 1 for 10 seconds...")
    if safe_valve_control(1, 'on', duration=10):
        print("✅ Valve 1 turned on")

    # Test 4: Check signal quality
    print("\n4. Checking signal quality...")
    signal = lora.get_signal_quality()
    if signal:
        print(f"RSSI: {signal['rssi']} dBm")
        print(f"Quality: {signal['quality']}%")

    print("\n✅ Integration test complete")

