#!/usr/bin/env python3
"""
Test script for LoRa communication with ESP32
Run this on Raspberry Pi to test LoRa connectivity
"""

import sys
import time
from app.lora_controller import LoRaController

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_ping(controller):
    """Test basic connectivity"""
    print_header("Test 1: Ping ESP32")
    print("Sending PING command...")

    if controller.ping():
        print("✅ SUCCESS: ESP32 is responding")
        return True
    else:
        print("❌ FAILED: No response from ESP32")
        return False

def test_status(controller):
    """Test status query"""
    print_header("Test 2: Get Valve Status")
    print("Requesting valve status...")

    status = controller.get_status()
    if status:
        print("✅ SUCCESS: Status received")
        print("\nCurrent valve states:")
        for valve, state in sorted(status.items()):
            state_str = "🟢 ON" if state else "⚫ OFF"
            print(f"   Valve {valve}: {state_str}")
        return True
    else:
        print("❌ FAILED: Could not get status")
        return False

def test_valve_control(controller):
    """Test valve control"""
    print_header("Test 3: Valve Control")

    # Turn on valve 1
    print("\n1. Turning ON Valve 1 for 5 seconds...")
    if controller.valve_on(1, 5):
        print("✅ Command sent successfully")

        # Wait and check status
        time.sleep(2)
        status = controller.get_status()
        if status and status.get(1):
            print("✅ Verified: Valve 1 is ON")

            # Wait for auto-off
            print("\n2. Waiting for auto-off (3 more seconds)...")
            time.sleep(4)

            status = controller.get_status()
            if status and not status.get(1):
                print("✅ Verified: Valve 1 auto-turned OFF")
                return True
            else:
                print("⚠️  Warning: Valve may still be ON")
                # Turn it off manually
                controller.valve_off(1)
                return True
        else:
            print("❌ Could not verify valve state")
            return False
    else:
        print("❌ Failed to send command")
        return False

def test_signal_quality(controller):
    """Test signal quality"""
    print_header("Test 4: Signal Quality")

    # Send a ping to get fresh signal data
    controller.ping()
    time.sleep(0.5)

    quality = controller.get_signal_quality()
    if quality:
        print("✅ Signal quality metrics:")
        print(f"   RSSI: {quality['rssi']} dBm")
        print(f"   SNR: {quality['snr']} dB")
        print(f"   Quality: {quality['quality']}%")

        # Interpret quality
        rssi = quality['rssi']
        if rssi > -70:
            print("\n   📶 Excellent signal")
        elif rssi > -90:
            print("\n   📶 Good signal")
        elif rssi > -110:
            print("\n   📶 Fair signal (may have issues)")
        else:
            print("\n   📶 Poor signal (expect problems)")

        return True
    else:
        print("⚠️  No signal data available")
        return False

def test_all_off(controller):
    """Test emergency stop"""
    print_header("Test 5: Emergency Stop (All OFF)")
    print("Turning all valves OFF...")

    if controller.all_valves_off():
        print("✅ SUCCESS: All valves OFF command sent")

        # Verify
        time.sleep(1)
        status = controller.get_status()
        if status:
            all_off = all(not state for state in status.values())
            if all_off:
                print("✅ Verified: All valves are OFF")
                return True
            else:
                print("⚠️  Warning: Some valves may still be ON")
                return True
        return True
    else:
        print("❌ FAILED: Could not send command")
        return False

def main():
    print("\n" + "=" * 60)
    print("  ESP32 LoRa Irrigation System - Connection Test")
    print("=" * 60)
    print("\nInitializing LoRa controller...")

    controller = LoRaController()

    if not controller.connected:
        print("\n⚠️  WARNING: LoRa module not initialized")
        print("Running in simulation mode for testing")
        print("\nIf this is unexpected, check:")
        print("  1. LoRa module connections")
        print("  2. SPI is enabled (sudo raspi-config)")
        print("  3. pyLoRa library is installed")

    print("\nStarting tests...\n")

    results = []

    # Run tests
    try:
        results.append(("Ping", test_ping(controller)))
        time.sleep(1)

        results.append(("Status Query", test_status(controller)))
        time.sleep(1)

        results.append(("Valve Control", test_valve_control(controller)))
        time.sleep(1)

        results.append(("Signal Quality", test_signal_quality(controller)))
        time.sleep(1)

        results.append(("Emergency Stop", test_all_off(controller)))

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        controller.all_valves_off()
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
    finally:
        print("\nCleaning up...")
        controller.cleanup()

    # Summary
    print_header("Test Results Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    elif passed > 0:
        print("\n⚠️  Some tests failed. Check connections and configuration.")
        return 1
    else:
        print("\n❌ All tests failed. Please check:")
        print("   1. ESP32 is powered on")
        print("   2. ESP32 code is uploaded and running")
        print("   3. LoRa modules are properly connected")
        print("   4. Both devices use the same frequency")
        print("   5. Antennas are connected")
        return 2

if __name__ == "__main__":
    sys.exit(main())

