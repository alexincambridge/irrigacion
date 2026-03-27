"""
LoRa UART Controller for Raspberry Pi
EBYTE E220/E32 module — communicates with ESP32 via LoRa UART

Pinout:
  RPi GPIO 14 (TXD) → RXD módulo LoRa
  RPi GPIO 15 (RXD) → TXD módulo LoRa
  RPi GPIO 5        → M0
  RPi GPIO 6        → M1
  RPi GPIO 13       → AUX
  3.3V (Pin 1)      → VCC
  GND  (Pin 6)      → GND
"""

import time
import logging

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logging.warning("pyserial not available. pip install pyserial")

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO not available — LoRa control pins disabled")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# EBYTE operating modes (M0, M1 pin combinations)
# -----------------------------------------------------------
MODE_NORMAL     = (0, 0)  # M0=LOW,  M1=LOW  → UART transparent transmission
MODE_WAKEUP     = (1, 0)  # M0=HIGH, M1=LOW  → Wake-up mode
MODE_POWERSAVE  = (0, 1)  # M0=LOW,  M1=HIGH → Power saving / listen
MODE_SLEEP      = (1, 1)  # M0=HIGH, M1=HIGH → Sleep / configuration mode


class LoRaController:
    """LoRa UART communication controller for EBYTE E220/E32 modules"""

    def __init__(self, port='/dev/serial0', baud=9600,
                 m0_pin=5, m1_pin=6, aux_pin=13):
        self.port = port
        self.baud = baud
        self.m0_pin = m0_pin
        self.m1_pin = m1_pin
        self.aux_pin = aux_pin
        self.serial = None
        self.connected = False
        self.last_response = None
        self.last_rssi = None

        self._init_gpio()
        self._init_serial()

    # -------------------------------------------------------
    # Initialisation helpers
    # -------------------------------------------------------
    def _init_gpio(self):
        """Set up M0, M1, AUX pins"""
        if not GPIO_AVAILABLE:
            logger.warning("GPIO not available — M0/M1/AUX pins not configured")
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.m0_pin, GPIO.OUT)
        GPIO.setup(self.m1_pin, GPIO.OUT)
        GPIO.setup(self.aux_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Default to normal (transparent) mode
        self._set_mode(MODE_NORMAL)
        logger.info(f"📡 LoRa GPIO: M0={self.m0_pin}, M1={self.m1_pin}, AUX={self.aux_pin}")

    def _init_serial(self):
        """Open UART serial port"""
        if not SERIAL_AVAILABLE:
            logger.warning("pyserial not installed — running simulation")
            return

        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
            )
            self.connected = True
            logger.info(f"📡 LoRa UART opened: {self.port} @ {self.baud} baud")
        except Exception as e:
            logger.error(f"❌ Failed to open LoRa UART: {e}")
            self.connected = False

    # -------------------------------------------------------
    # Operating mode control
    # -------------------------------------------------------
    def _set_mode(self, mode):
        """Set EBYTE operating mode via M0/M1 pins"""
        if not GPIO_AVAILABLE:
            return
        m0_val, m1_val = mode
        GPIO.output(self.m0_pin, m0_val)
        GPIO.output(self.m1_pin, m1_val)
        time.sleep(0.1)  # allow module to switch mode
        self._wait_aux()

    def _wait_aux(self, timeout=3):
        """Wait for AUX pin to go HIGH (module ready)"""
        if not GPIO_AVAILABLE:
            time.sleep(0.1)
            return True
        start = time.time()
        while time.time() - start < timeout:
            if GPIO.input(self.aux_pin) == 1:
                return True
            time.sleep(0.01)
        logger.warning("⚠️ AUX timeout — module may be busy")
        return False

    # -------------------------------------------------------
    # Core send / receive
    # -------------------------------------------------------
    def send_command(self, command, timeout=5):
        """
        Send a text command via LoRa UART and wait for response.

        Args:
            command: e.g. "ON:1:300", "OFF:2", "STATUS", "PING"
            timeout: seconds to wait for response

        Returns:
            Response string or None
        """
        if not self.connected or not self.serial:
            logger.info(f"[SIM] Would send: {command}")
            return self._simulate_response(command)

        try:
            self._set_mode(MODE_NORMAL)
            self._wait_aux()

            # Flush stale data
            self.serial.reset_input_buffer()

            # Send command with newline terminator
            payload = (command + '\n').encode('utf-8')
            self.serial.write(payload)
            self.serial.flush()
            logger.info(f"📤 LoRa TX: {command}")

            # Wait for response
            start = time.time()
            buffer = b''
            while time.time() - start < timeout:
                if self.serial.in_waiting > 0:
                    chunk = self.serial.read(self.serial.in_waiting)
                    buffer += chunk
                    if b'\n' in buffer:
                        break
                time.sleep(0.05)

            if buffer:
                response = buffer.decode('utf-8', errors='replace').strip()
                self.last_response = response
                logger.info(f"📡 LoRa RX: {response}")
                return response

            logger.warning(f"⏱️ Timeout waiting for response to: {command}")
            return None

        except Exception as e:
            logger.error(f"❌ LoRa send error: {e}")
            return None

    def _simulate_response(self, command):
        """Simulate response for testing without hardware"""
        time.sleep(0.3)
        parts = command.split(':')
        cmd = parts[0] if parts else ""

        if cmd == "ON" and len(parts) >= 2:
            return f"OK:VALVE_{parts[1]}_ON"
        elif cmd == "OFF" and len(parts) >= 2:
            return f"OK:VALVE_{parts[1]}_OFF"
        elif cmd == "ALL_OFF":
            return "OK:ALL_OFF"
        elif cmd == "STATUS":
            return "STATUS:1=OFF,2=OFF,3=OFF,4=OFF"
        elif cmd == "PING":
            return "PONG:ESP32_IRR_001"
        return "ERROR:INVALID_COMMAND"

    # -------------------------------------------------------
    # Convenience methods — valve control
    # -------------------------------------------------------
    def valve_on(self, valve_id, duration=0):
        cmd = f"ON:{valve_id}:{duration}" if duration > 0 else f"ON:{valve_id}"
        resp = self.send_command(cmd)
        return resp is not None and resp.startswith("OK")

    def valve_off(self, valve_id):
        resp = self.send_command(f"OFF:{valve_id}")
        return resp is not None and resp.startswith("OK")

    def all_valves_off(self):
        resp = self.send_command("ALL_OFF")
        return resp is not None and resp.startswith("OK")

    def get_status(self):
        """
        Returns dict {1: False, 2: True, 3: False, 4: False}
        """
        resp = self.send_command("STATUS")
        if not resp or not resp.startswith("STATUS:"):
            return None
        try:
            status_str = resp.split(':', 1)[1]
            states = {}
            for item in status_str.split(','):
                num, state = item.split('=')
                states[int(num)] = (state.strip().upper() == "ON")
            return states
        except Exception as e:
            logger.error(f"Error parsing status: {e}")
            return None

    def ping(self):
        resp = self.send_command("PING", timeout=3)
        return resp is not None and resp.startswith("PONG")

    # -------------------------------------------------------
    # Module configuration (sleep mode required)
    # -------------------------------------------------------
    def configure_module(self, address=0x0001, channel=23, air_rate=2,
                         uart_rate=3, power=0):
        """
        Configure EBYTE module parameters (enters sleep mode).

        Args:
            address: 2-byte device address (0x0000 - 0xFFFF)
            channel: LoRa channel (0-83 for E220)
            air_rate: 0=0.3k, 1=1.2k, 2=2.4k, 3=4.8k, 4=9.6k, 5=19.2k
            uart_rate: 0=1200, 1=2400, 2=4800, 3=9600, 4=19200, 5=38400, 6=57600, 7=115200
            power: 0=22dBm, 1=17dBm, 2=13dBm, 3=10dBm
        """
        if not self.connected or not self.serial:
            logger.warning("Cannot configure — serial not available")
            return False

        try:
            self._set_mode(MODE_SLEEP)
            time.sleep(0.5)

            addr_h = (address >> 8) & 0xFF
            addr_l = address & 0xFF
            speed = (uart_rate << 5) | (air_rate & 0x07)
            option = (power & 0x03)

            config_bytes = bytes([0xC0, addr_h, addr_l, speed, channel, option])
            self.serial.write(config_bytes)
            self.serial.flush()
            time.sleep(0.5)

            resp = self.serial.read(6)
            self._set_mode(MODE_NORMAL)

            if len(resp) >= 4:
                logger.info(f"✅ Module configured: addr=0x{address:04X}, ch={channel}")
                return True
            else:
                logger.warning("⚠️ No response to config command")
                return False

        except Exception as e:
            logger.error(f"❌ Config error: {e}")
            self._set_mode(MODE_NORMAL)
            return False

    def read_config(self):
        """Read current module configuration"""
        if not self.connected or not self.serial:
            return None

        try:
            self._set_mode(MODE_SLEEP)
            time.sleep(0.3)

            self.serial.write(bytes([0xC1, 0xC1, 0xC1]))
            self.serial.flush()
            time.sleep(0.5)

            resp = self.serial.read(6)
            self._set_mode(MODE_NORMAL)

            if len(resp) >= 6:
                config = {
                    'head': hex(resp[0]),
                    'address': (resp[1] << 8) | resp[2],
                    'speed': hex(resp[3]),
                    'channel': resp[4],
                    'option': hex(resp[5])
                }
                logger.info(f"📋 Module config: {config}")
                return config
            return None

        except Exception as e:
            logger.error(f"Error reading config: {e}")
            self._set_mode(MODE_NORMAL)
            return None

    # -------------------------------------------------------
    # Signal quality
    # -------------------------------------------------------
    def get_signal_quality(self):
        """Approximate signal quality (EBYTE modules don't report RSSI easily)"""
        if self.last_rssi is not None:
            return {
                'rssi': self.last_rssi,
                'quality': min(100, max(0, (self.last_rssi + 120) * 100 // 90))
            }
        # If we got a recent successful response, assume decent quality
        if self.last_response:
            return {'rssi': -60, 'quality': 67}
        return None

    # -------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------
    def cleanup(self):
        """Release serial port and GPIO"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("📡 LoRa serial port closed")
        # Note: GPIO cleanup is handled globally by hardware module
        self.connected = False


# ---------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------
_lora_controller = None

def get_lora_controller():
    """Get or create LoRa controller singleton"""
    global _lora_controller
    if _lora_controller is None:
        try:
            from app import config
            port = getattr(config, 'LORA_SERIAL_PORT', '/dev/serial0')
            baud = getattr(config, 'LORA_BAUD_RATE', 9600)
            m0 = getattr(config, 'LORA_M0_PIN', 5)
            m1 = getattr(config, 'LORA_M1_PIN', 6)
            aux = getattr(config, 'LORA_AUX_PIN', 13)
        except ImportError:
            port, baud, m0, m1, aux = '/dev/serial0', 9600, 5, 6, 13

        _lora_controller = LoRaController(port=port, baud=baud,
                                          m0_pin=m0, m1_pin=m1, aux_pin=aux)
    return _lora_controller


# ---------------------------------------------------------------
# Test script
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("  LoRa EBYTE UART Controller Test")
    print("=" * 50)

    ctrl = LoRaController()

    print("\n1. Ping ESP32...")
    if ctrl.ping():
        print("   ✅ ESP32 responded")
    else:
        print("   ❌ No response (simulation mode?)")

    print("\n2. Read module config...")
    cfg = ctrl.read_config()
    if cfg:
        print(f"   Address: 0x{cfg['address']:04X}")
        print(f"   Channel: {cfg['channel']}")
    else:
        print("   ⚠️ Could not read config")

    print("\n3. Get status...")
    status = ctrl.get_status()
    if status:
        for v, s in status.items():
            print(f"   Valve {v}: {'ON' if s else 'OFF'}")

    print("\n4. Test valve 1 ON (10s)...")
    if ctrl.valve_on(1, 10):
        print("   ✅ Valve 1 ON")

    time.sleep(2)
    print("\n5. Signal quality...")
    q = ctrl.get_signal_quality()
    if q:
        print(f"   Quality: {q['quality']}%")

    print("\n6. Cleanup...")
    ctrl.cleanup()
    print("✅ Done")
