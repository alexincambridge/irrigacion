SECRET_KEY = "change_this"
DB_PATH = "database/irrigation.db"

RELAY_PIN = 23
DHT_PIN = 22

# Peristaltic Pump (Fertilization)
PUMP_PIN = 17  # GPIO 17 for peristaltic pump
PUMP_MAX_DURATION = 3600  # Max 60 min safety limit (seconds)

TEMP_MAX = 30
HUM_MIN = 40
WATER_TIME = 5

# Hardware Configuration
# Options: 'GPIO' (direct Raspberry Pi GPIO), 'LORA' (ESP32 via LoRa), 'SIMULATION' (testing)
HARDWARE_MODE = 'LORA'  # Change to 'GPIO' for direct control or 'SIMULATION' for testing

# LoRa Configuration (if HARDWARE_MODE = 'LORA')
LORA_FREQUENCY = 915E6  # 915 MHz for US/Americas, 868E6 for Europe/Asia
LORA_SPREADING_FACTOR = 12  # 7-12, higher = longer range but slower
LORA_BANDWIDTH = 125E3  # 125 kHz
LORA_CODING_RATE = 5  # 4/5
LORA_TX_POWER = 20  # dBm

# Irrigation Zones
NUM_ZONES = 4  # Number of irrigation zones/valves

# Peripherals Registry (for health check page)
PERIPHERALS = {
    "relay_1": {"name": "Relé Zona 1 - Jardín", "type": "relay", "gpio": 23},
    "relay_2": {"name": "Relé Zona 2 - Huerta", "type": "relay", "gpio": 24},
    "relay_3": {"name": "Relé Zona 3 - Césped", "type": "relay", "gpio": 25},
    "relay_4": {"name": "Relé Zona 4 - Árboles", "type": "relay", "gpio": 27},
    "dht11": {"name": "DHT11 Temp/Humedad", "type": "sensor", "gpio": 22},
    "pump": {"name": "Bomba Peristáltica", "type": "actuator", "gpio": 17},
    "esp32_lora": {"name": "ESP32 LoRa (Tensiómetro)", "type": "esp32", "address": "lora"},
    "fertilizer_counter": {"name": "Contador Fertilizante", "type": "sensor", "gpio": 18},
}

