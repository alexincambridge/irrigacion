"""
LoRa Controller for Raspberry Pi
Communicates with ESP32 to control irrigation valves via LoRa
"""

import time
import logging
from datetime import datetime

try:
    from SX127x.LoRa import LoRa
    from SX127x.board_config import BOARD
    LORA_AVAILABLE = True
except ImportError:
    LORA_AVAILABLE = False
    logging.warning("LoRa module not available. Running in simulation mode.")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoRaController:
    """LoRa communication controller for irrigation system"""

    def __init__(self, frequency=915E6):
        """
        Initialize LoRa controller

        Args:
            frequency: LoRa frequency in Hz (915E6 for US, 868E6 for EU)
        """
        self.frequency = frequency
        self.lora = None
        self.last_response = None
        self.last_rssi = None
        self.last_snr = None
        self.connected = False

        if LORA_AVAILABLE:
            self._init_lora()
        else:
            logger.warning("LoRa hardware not available - using simulation mode")

    def _init_lora(self):
        """Initialize LoRa hardware"""
        try:
            BOARD.setup()
            self.lora = LoRa(verbose=False)
            self.lora.set_mode_stdby()

            # Configure LoRa parameters
            self.lora.set_freq(self.frequency / 1E6)  # Convert to MHz
            self.lora.set_spreading_factor(12)
            self.lora.set_bw(7)  # 125 kHz
            self.lora.set_coding_rate(5)  # 4/5
            self.lora.set_tx_power(20, False)  # 20 dBm
            self.lora.set_crc_on()

            self.lora.set_mode_rx_cont()
            self.connected = True
            logger.info(f"LoRa initialized at {self.frequency/1E6} MHz")

        except Exception as e:
            logger.error(f"Failed to initialize LoRa: {e}")
            self.connected = False

    def send_command(self, command, timeout=5):
        """
        Send command to ESP32 and wait for response

        Args:
            command: Command string (e.g., "ON:1:300")
            timeout: Response timeout in seconds

        Returns:
            Response string or None if timeout/error
        """
        if not LORA_AVAILABLE or not self.connected:
            logger.info(f"[SIMULATION] Would send: {command}")
            return self._simulate_response(command)

        try:
            # Send command
            logger.info(f"📤 Sending: {command}")
            self.lora.set_mode_stdby()

            payload = list(command.encode())
            self.lora.write_payload(payload)
            self.lora.set_mode_tx()

            # Wait for transmission to complete
            time.sleep(0.5)
            self.lora.set_mode_rx_cont()

            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.lora.rx_done():
                    response = self._read_response()
                    if response:
                        logger.info(f"📡 Received: {response}")
                        return response
                time.sleep(0.1)

            logger.warning(f"Timeout waiting for response to: {command}")
            return None

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None

    def _read_response(self):
        """Read and parse LoRa response"""
        try:
            payload = self.lora.read_payload(nocheck=True)
            response = ''.join(chr(c) for c in payload if c != 0)

            self.last_rssi = self.lora.get_pkt_rssi_value()
            self.last_snr = self.lora.get_pkt_snr_value()
            self.last_response = response

            logger.debug(f"RSSI: {self.last_rssi} dBm, SNR: {self.last_snr} dB")

            return response

        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return None

    def _simulate_response(self, command):
        """Simulate response for testing without hardware"""
        time.sleep(0.5)  # Simulate transmission delay

        parts = command.split(':')
        cmd = parts[0] if len(parts) > 0 else ""

        if cmd == "ON" and len(parts) >= 2:
            valve = parts[1]
            return f"OK:VALVE_{valve}_ON"
        elif cmd == "OFF" and len(parts) >= 2:
            valve = parts[1]
            return f"OK:VALVE_{valve}_OFF"
        elif cmd == "ALL_OFF":
            return "OK:ALL_OFF"
        elif cmd == "STATUS":
            return "STATUS:1=OFF,2=OFF,3=OFF,4=OFF"
        elif cmd == "PING":
            return "PONG:ESP32_IRR_001"
        else:
            return "ERROR:INVALID_COMMAND"

    # Convenience methods for common operations

    def valve_on(self, valve_id, duration=0):
        """
        Turn on a specific valve

        Args:
            valve_id: Valve number (1-4)
            duration: Auto-off duration in seconds (0 = manual mode)

        Returns:
            True if successful, False otherwise
        """
        if duration > 0:
            command = f"ON:{valve_id}:{duration}"
        else:
            command = f"ON:{valve_id}"

        response = self.send_command(command)
        return response and response.startswith("OK")

    def valve_off(self, valve_id):
        """
        Turn off a specific valve

        Args:
            valve_id: Valve number (1-4)

        Returns:
            True if successful, False otherwise
        """
        command = f"OFF:{valve_id}"
        response = self.send_command(command)
        return response and response.startswith("OK")

    def all_valves_off(self):
        """
        Turn off all valves

        Returns:
            True if successful, False otherwise
        """
        response = self.send_command("ALL_OFF")
        return response and response.startswith("OK")

    def get_status(self):
        """
        Get status of all valves

        Returns:
            Dictionary with valve states or None if failed
            Example: {1: False, 2: True, 3: False, 4: False}
        """
        response = self.send_command("STATUS")
        if not response or not response.startswith("STATUS:"):
            return None

        try:
            # Parse "STATUS:1=ON,2=OFF,3=OFF,4=OFF"
            status_str = response.split(':')[1]
            states = {}

            for item in status_str.split(','):
                valve_num, state = item.split('=')
                states[int(valve_num)] = (state == "ON")

            return states

        except Exception as e:
            logger.error(f"Error parsing status: {e}")
            return None

    def ping(self):
        """
        Check if ESP32 is responding

        Returns:
            True if ESP32 responds, False otherwise
        """
        response = self.send_command("PING", timeout=3)
        return response and response.startswith("PONG")

    def get_signal_quality(self):
        """
        Get last received signal quality metrics

        Returns:
            Dictionary with RSSI and SNR or None
        """
        if self.last_rssi is None:
            return None

        return {
            'rssi': self.last_rssi,
            'snr': self.last_snr,
            'quality': self._calculate_signal_quality()
        }

    def _calculate_signal_quality(self):
        """Calculate signal quality percentage"""
        if self.last_rssi is None:
            return 0

        # RSSI typically ranges from -120 (worst) to -30 (best)
        rssi_percent = min(100, max(0, (self.last_rssi + 120) * 100 / 90))

        # SNR typically ranges from -20 to +10
        snr_percent = min(100, max(0, (self.last_snr + 20) * 100 / 30)) if self.last_snr else 50

        # Combined quality
        return int((rssi_percent + snr_percent) / 2)

    def cleanup(self):
        """Cleanup LoRa resources"""
        if LORA_AVAILABLE and self.lora:
            try:
                self.lora.set_mode_stdby()
                BOARD.teardown()
                logger.info("LoRa cleaned up")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")


# Singleton instance
_lora_controller = None

def get_lora_controller():
    """Get or create LoRa controller singleton"""
    global _lora_controller
    if _lora_controller is None:
        _lora_controller = LoRaController()
    return _lora_controller


if __name__ == "__main__":
    # Test script
    print("LoRa Controller Test")
    print("=" * 50)

    controller = LoRaController()

    # Test ping
    print("\n1. Testing ping...")
    if controller.ping():
        print("✅ ESP32 is responding")
    else:
        print("❌ ESP32 not responding")

    # Get status
    print("\n2. Getting status...")
    status = controller.get_status()
    if status:
        print("Current valve states:")
        for valve, state in status.items():
            print(f"   Valve {valve}: {'ON' if state else 'OFF'}")

    # Test valve control
    print("\n3. Testing valve 1...")
    print("   Turning ON for 10 seconds...")
    if controller.valve_on(1, 10):
        print("   ✅ Valve 1 turned ON")
        time.sleep(3)

        # Check status
        status = controller.get_status()
        if status and status.get(1):
            print("   ✅ Status confirmed: Valve 1 is ON")

    # Signal quality
    print("\n4. Signal quality...")
    quality = controller.get_signal_quality()
    if quality:
        print(f"   RSSI: {quality['rssi']} dBm")
        print(f"   SNR: {quality['snr']} dB")
        print(f"   Quality: {quality['quality']}%")

    # Cleanup
    print("\n5. Cleaning up...")
    controller.cleanup()
    print("✅ Test complete")

