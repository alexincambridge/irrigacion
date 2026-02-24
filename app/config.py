SECRET_KEY = "change_this"
DB_PATH = "database/irrigation.db"

RELAY_PIN = 23
DHT_PIN = 22

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

