SECRET_KEY = "change_this"
DB_PATH = "database/irrigation.db"

RELAY_PIN = 23
DHT_PIN = 4  # GPIO 4 — DHT22 sensor

# Peristaltic Pump (Fertilization)
PUMP_PIN = 17  # GPIO 17 for peristaltic pump
PUMP_MAX_DURATION = 3600  # Max 60 min safety limit (seconds)


TEMP_MAX = 30
HUM_MIN = 40
WATER_TIME = 5

# Hardware Configuration
# Options: 'GPIO' (direct Raspberry Pi GPIO), 'LORA' (ESP32 via LoRa), 'SIMULATION' (testing)
HARDWARE_MODE = 'GPIO'  # Change to 'LORA' for ESP32 control or 'SIMULATION' for testing

# LoRa UART Configuration (EBYTE E220/E32 module)
LORA_TX_PIN = 14   # GPIO 14 (RPi TXD) → RXD del módulo LoRa
LORA_RX_PIN = 15   # GPIO 15 (RPi RXD) → TXD del módulo LoRa
LORA_M0_PIN = 5    # GPIO 5 → M0 (modo operación)
LORA_M1_PIN = 6    # GPIO 6 → M1 (modo operación)
LORA_AUX_PIN = 13  # GPIO 13 → AUX (estado del módulo)
LORA_SERIAL_PORT = '/dev/serial0'  # UART hardware RPi
LORA_BAUD_RATE = 9600  # Baud rate por defecto EBYTE
LORA_ADDRESS = 0x0001  # Dirección del RPi
LORA_CHANNEL = 23  # Canal LoRa (410.125 + 23 = 433.125 MHz para EU)
LORA_FREQUENCY = 868E6  # 868 MHz para Europa

# Irrigation Zones
NUM_ZONES = 4  # Number of irrigation zones/valves

# Peripherals Registry (for health check page)
PERIPHERALS = {
    "relay_1": {"name": "Relé Zona 1 - Jardín", "type": "relay", "gpio": 16},
    "relay_2": {"name": "Relé Zona 2 - Huerta", "type": "relay", "gpio": 23},
    "relay_3": {"name": "Relé Zona 3 - Césped", "type": "relay", "gpio": 24},
    "relay_4": {"name": "Relé Zona 4 - Árboles", "type": "relay", "gpio": 26},
    "dht22": {"name": "DHT22 Temp/Humedad", "type": "sensor", "gpio": 4},
    "pump": {"name": "Bomba Peristáltica", "type": "actuator", "gpio": 17},
    "esp32_lora": {"name": "ESP32 LoRa (Tensiómetro)", "type": "esp32", "address": "lora"},
    "lora_ebyte": {"name": "LoRa EBYTE E220 (UART)", "type": "lora", "gpio_tx": 14, "gpio_rx": 15, "gpio_m0": 5, "gpio_m1": 6, "gpio_aux": 13},
    "fertilizer_counter": {"name": "Contador Fertilizante", "type": "sensor", "gpio": 18},
}

# --------------------
# TELEGRAM NOTIFICATIONS
# --------------------
NOTIFICATIONS_ENABLED = True
TELEGRAM_BOT_TOKEN = "8567543848:AAHchO7qUStnzc_rx8N_2OZt5WTau_XEXB0"  # O el que hayas regenerado
TELEGRAM_CHAT_ID = "7209472936"
