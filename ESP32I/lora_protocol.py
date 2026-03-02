"""
LoRa Communication Protocol for Irrigation System
Bidirectional communication between RPi (Gateway) and ESP32 (Nodes)
"""

import struct
import time
from enum import Enum
from typing import Optional, Tuple

class CommandType(Enum):
    """LoRa Command Types"""
    ZONE_ON = 0x01
    ZONE_OFF = 0x02
    STATUS = 0x03
    TELEMETRY = 0x04
    PING = 0x05
    SET_SCHEDULE = 0x06
    RESET = 0x07
    UPDATE_FIRMWARE = 0x08
    ERROR = 0xFF

class DeviceStatus(Enum):
    """Device Connection Status"""
    ONLINE = 0x01
    OFFLINE = 0x02
    ERROR = 0x03
    UNKNOWN = 0x04

class LoRaFrame:
    """LoRa Frame Structure"""

    HEADER = 0xAA
    FRAME_SIZE = 256

    def __init__(self, device_id: int, command: CommandType, data: bytes = b'', priority: int = 0):
        self.device_id = device_id
        self.command = command
        self.data = data
        self.priority = priority
        self.timestamp = int(time.time())
        self.checksum = 0

    def encode(self) -> bytes:
        """
        Encode frame to bytes
        Format: [HEADER:1][DEVICE_ID:1][CMD:1][DATA_LEN:2][DATA:N][CHECKSUM:1]
        """
        frame = bytearray()

        # Header
        frame.append(self.HEADER)

        # Device ID
        frame.append(self.device_id & 0xFF)

        # Command
        frame.append(self.command.value)

        # Data length
        data_len = len(self.data)
        frame.append((data_len >> 8) & 0xFF)
        frame.append(data_len & 0xFF)

        # Data
        frame.extend(self.data)

        # Checksum (XOR of all bytes)
        checksum = 0
        for byte in frame:
            checksum ^= byte
        frame.append(checksum)

        return bytes(frame)

    @staticmethod
    def decode(data: bytes) -> Optional['LoRaFrame']:
        """Decode frame from bytes"""
        if len(data) < 6:
            return None

        # Check header
        if data[0] != LoRaFrame.HEADER:
            print(f"[LoRa] Invalid header: {hex(data[0])}")
            return None

        device_id = data[1]
        command_value = data[2]
        data_len = (data[3] << 8) | data[4]

        # Extract data
        frame_data = data[5:5 + data_len]

        # Verify checksum
        expected_checksum = data[5 + data_len]
        calculated_checksum = 0
        for byte in data[:5 + data_len]:
            calculated_checksum ^= byte

        if expected_checksum != calculated_checksum:
            print(f"[LoRa] Checksum mismatch: {hex(expected_checksum)} vs {hex(calculated_checksum)}")
            return None

        # Convert command
        try:
            command = CommandType(command_value)
        except ValueError:
            print(f"[LoRa] Unknown command: {hex(command_value)}")
            return None

        frame = LoRaFrame(device_id, command, frame_data)
        return frame


class LoRaProtocol:
    """Protocol layer for LoRa communication"""

    @staticmethod
    def create_zone_control(zone_id: int, enabled: bool) -> LoRaFrame:
        """
        Create ZONE_ON or ZONE_OFF command
        Data: [ZONE_ID:1] [DURATION:2] (only for ZONE_ON)
        """
        cmd = CommandType.ZONE_ON if enabled else CommandType.ZONE_OFF
        data = bytes([zone_id & 0xFF])

        if enabled:
            # Add default duration (30 minutes)
            duration = 30
            data += struct.pack('>H', duration)

        return LoRaFrame(1, cmd, data, priority=2)

    @staticmethod
    def create_status_request() -> LoRaFrame:
        """Create STATUS request"""
        return LoRaFrame(1, CommandType.STATUS, priority=1)

    @staticmethod
    def create_ping() -> LoRaFrame:
        """Create PING request"""
        return LoRaFrame(1, CommandType.PING, priority=1)

    @staticmethod
    def create_telemetry_response(zones_state: dict, sensors: dict) -> LoRaFrame:
        """
        Create TELEMETRY response
        Data: [ZONES:4 bits][TEMP:1][HUMIDITY:1][PRESSURE:2][FLOW:2]
        """
        data = bytearray()

        # Encode zones as bits (4 zones = 4 bits)
        zones_byte = 0
        for zone_id, state in zones_state.items():
            if state:
                zones_byte |= (1 << (zone_id - 1))
        data.append(zones_byte)

        # Sensors
        data.append(int(sensors.get('temperature', 0)) & 0xFF)
        data.append(int(sensors.get('humidity', 0)) & 0xFF)

        # Pressure (2 bytes)
        pressure = int(sensors.get('pressure', 0) * 10) & 0xFFFF
        data.append((pressure >> 8) & 0xFF)
        data.append(pressure & 0xFF)

        # Water flow (2 bytes)
        flow = int(sensors.get('water_flow', 0) * 10) & 0xFFFF
        data.append((flow >> 8) & 0xFF)
        data.append(flow & 0xFF)

        return LoRaFrame(1, CommandType.TELEMETRY, bytes(data), priority=0)

    @staticmethod
    def parse_zone_control(frame: LoRaFrame) -> Tuple[int, bool, Optional[int]]:
        """
        Parse ZONE_ON/ZONE_OFF command
        Returns: (zone_id, enabled, duration_minutes)
        """
        if len(frame.data) < 1:
            return None, None, None

        zone_id = frame.data[0]
        enabled = frame.command == CommandType.ZONE_ON
        duration = None

        if enabled and len(frame.data) >= 3:
            duration = struct.unpack('>H', frame.data[1:3])[0]

        return zone_id, enabled, duration

    @staticmethod
    def parse_telemetry(frame: LoRaFrame) -> dict:
        """
        Parse TELEMETRY response
        Returns: {
            'zones': {1: True, 2: False, 3: True, 4: False},
            'temperature': 25.5,
            'humidity': 65,
            'pressure': 1.2,
            'water_flow': 1.5
        }
        """
        if len(frame.data) < 7:
            return {}

        result = {}

        # Parse zones
        zones_byte = frame.data[0]
        zones = {}
        for i in range(4):
            zones[i + 1] = bool(zones_byte & (1 << i))
        result['zones'] = zones

        # Parse sensors
        result['temperature'] = frame.data[1]
        result['humidity'] = frame.data[2]
        result['pressure'] = struct.unpack('>H', frame.data[3:5])[0] / 10.0
        result['water_flow'] = struct.unpack('>H', frame.data[5:7])[0] / 10.0

        return result


class LoRaStats:
    """Track LoRa communication statistics"""

    def __init__(self):
        self.packets_sent = 0
        self.packets_received = 0
        self.packets_lost = 0
        self.errors = 0
        self.avg_rssi = 0
        self.last_packet_time = 0

    def record_sent(self):
        self.packets_sent += 1

    def record_received(self, rssi: int):
        self.packets_received += 1
        self.last_packet_time = time.time()
        # Update average RSSI
        self.avg_rssi = (self.avg_rssi * (self.packets_received - 1) + rssi) / self.packets_received

    def record_error(self):
        self.errors += 1

    def get_report(self) -> dict:
        return {
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'packets_lost': self.packets_lost,
            'errors': self.errors,
            'avg_rssi': self.avg_rssi,
            'success_rate': (self.packets_received / self.packets_sent * 100) if self.packets_sent > 0 else 0
        }


if __name__ == "__main__":
    # Test encoding/decoding

    # Test 1: ZONE_ON command
    frame1 = LoRaProtocol.create_zone_control(1, True)
    print(f"[TEST] ZONE_ON frame: {frame1.encode().hex()}")

    decoded1 = LoRaFrame.decode(frame1.encode())
    if decoded1:
        zone_id, enabled, duration = LoRaProtocol.parse_zone_control(decoded1)
        print(f"[TEST] Decoded: Zone {zone_id}, Enabled: {enabled}, Duration: {duration}m")

    # Test 2: TELEMETRY response
    zones = {1: True, 2: False, 3: True, 4: False}
    sensors = {'temperature': 25, 'humidity': 65, 'pressure': 1.2, 'water_flow': 1.5}
    frame2 = LoRaProtocol.create_telemetry_response(zones, sensors)
    print(f"[TEST] TELEMETRY frame: {frame2.encode().hex()}")

    decoded2 = LoRaFrame.decode(frame2.encode())
    if decoded2:
        data = LoRaProtocol.parse_telemetry(decoded2)
        print(f"[TEST] Decoded: {data}")

    print("[TEST] All protocol tests passed!")

