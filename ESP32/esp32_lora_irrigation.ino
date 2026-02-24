/*
 * ESP32 LoRa Irrigation Controller
 * Controls 4 solenoid valves via LoRa commands from Raspberry Pi
 *
 * Hardware:
 * - ESP32 board
 * - LoRa module (SX1276/RFM95)
 * - 4 relay modules for solenoid valves
 *
 * LoRa Pins (adjust based on your module):
 * - NSS: 5
 * - RST: 14
 * - DIO0: 2
 */

#include <SPI.h>
#include <LoRa.h>

// LoRa Configuration
#define LORA_FREQUENCY 915E6  // 915 MHz for US, use 868E6 for Europe
#define LORA_SS 5
#define LORA_RST 14
#define LORA_DIO0 2

// Solenoid Valve Pins (connected to relay modules)
const int VALVE_PINS[4] = {13, 12, 27, 26};  // GPIO pins for 4 valves
const char* VALVE_NAMES[4] = {"Valve 1", "Valve 2", "Valve 3", "Valve 4"};

// Valve states
bool valveStates[4] = {false, false, false, false};

// Device ID
const String DEVICE_ID = "ESP32_IRR_001";

// Command structure
struct Command {
  char cmd[16];      // Command type: ON, OFF, STATUS, ALL_OFF
  int valve;         // Valve number (1-4, or 0 for all)
  int duration;      // Duration in seconds (optional)
};

// Timer for auto-shutoff
unsigned long valveTimers[4] = {0, 0, 0, 0};
int valveDurations[4] = {0, 0, 0, 0};

void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("ESP32 LoRa Irrigation Controller");
  Serial.println("================================");

  // Initialize valve pins
  for (int i = 0; i < 4; i++) {
    pinMode(VALVE_PINS[i], OUTPUT);
    digitalWrite(VALVE_PINS[i], LOW);  // All valves OFF initially
  }

  // Initialize LoRa
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa initialization failed!");
    while (1);
  }

  // LoRa parameters for better range and reliability
  LoRa.setSpreadingFactor(12);        // SF7 to SF12, higher = longer range
  LoRa.setSignalBandwidth(125E3);     // 125 kHz
  LoRa.setCodingRate4(5);             // 4/5 coding rate
  LoRa.setTxPower(20);                // Max power 20 dBm
  LoRa.enableCrc();                   // Enable CRC check

  Serial.println("LoRa initialized successfully");
  Serial.print("Frequency: ");
  Serial.print(LORA_FREQUENCY / 1E6);
  Serial.println(" MHz");
  Serial.println("\nWaiting for commands...\n");
}

void loop() {
  // Check for incoming LoRa messages
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    handleLoRaPacket();
  }

  // Check valve timers for auto-shutoff
  checkValveTimers();

  delay(10);
}

void handleLoRaPacket() {
  String message = "";

  // Read packet
  while (LoRa.available()) {
    message += (char)LoRa.read();
  }

  // Get RSSI
  int rssi = LoRa.packetRssi();
  float snr = LoRa.packetSnr();

  Serial.println("📡 Received: " + message);
  Serial.print("   RSSI: ");
  Serial.print(rssi);
  Serial.print(" dBm, SNR: ");
  Serial.print(snr);
  Serial.println(" dB");

  // Parse and execute command
  processCommand(message);
}

void processCommand(String message) {
  message.trim();

  // Parse command format: "CMD:VALVE:DURATION"
  // Examples: "ON:1:300", "OFF:2", "STATUS", "ALL_OFF"

  int firstColon = message.indexOf(':');
  int secondColon = message.indexOf(':', firstColon + 1);

  String cmd = message.substring(0, firstColon);
  String valveStr = "";
  String durationStr = "";

  if (firstColon > 0) {
    if (secondColon > 0) {
      valveStr = message.substring(firstColon + 1, secondColon);
      durationStr = message.substring(secondColon + 1);
    } else {
      valveStr = message.substring(firstColon + 1);
    }
  } else {
    cmd = message;
  }

  int valve = valveStr.toInt();
  int duration = durationStr.toInt();

  // Execute command
  if (cmd == "ON" && valve >= 1 && valve <= 4) {
    turnValveOn(valve - 1, duration);
    sendResponse("OK:VALVE_" + String(valve) + "_ON");
  }
  else if (cmd == "OFF" && valve >= 1 && valve <= 4) {
    turnValveOff(valve - 1);
    sendResponse("OK:VALVE_" + String(valve) + "_OFF");
  }
  else if (cmd == "ALL_OFF") {
    allValvesOff();
    sendResponse("OK:ALL_OFF");
  }
  else if (cmd == "STATUS") {
    sendStatus();
  }
  else if (cmd == "PING") {
    sendResponse("PONG:" + DEVICE_ID);
  }
  else {
    sendResponse("ERROR:INVALID_COMMAND");
    Serial.println("❌ Invalid command");
  }
}

void turnValveOn(int index, int duration) {
  if (index < 0 || index >= 4) return;

  digitalWrite(VALVE_PINS[index], HIGH);
  valveStates[index] = true;

  if (duration > 0) {
    valveTimers[index] = millis();
    valveDurations[index] = duration * 1000;  // Convert to milliseconds
    Serial.print("✅ ");
    Serial.print(VALVE_NAMES[index]);
    Serial.print(" ON (auto-off in ");
    Serial.print(duration);
    Serial.println(" seconds)");
  } else {
    valveTimers[index] = 0;
    valveDurations[index] = 0;
    Serial.print("✅ ");
    Serial.print(VALVE_NAMES[index]);
    Serial.println(" ON (manual mode)");
  }
}

void turnValveOff(int index) {
  if (index < 0 || index >= 4) return;

  digitalWrite(VALVE_PINS[index], LOW);
  valveStates[index] = false;
  valveTimers[index] = 0;
  valveDurations[index] = 0;

  Serial.print("⛔ ");
  Serial.print(VALVE_NAMES[index]);
  Serial.println(" OFF");
}

void allValvesOff() {
  for (int i = 0; i < 4; i++) {
    turnValveOff(i);
  }
  Serial.println("⛔ All valves OFF");
}

void checkValveTimers() {
  for (int i = 0; i < 4; i++) {
    if (valveStates[i] && valveDurations[i] > 0) {
      if (millis() - valveTimers[i] >= valveDurations[i]) {
        turnValveOff(i);
        sendResponse("AUTO_OFF:VALVE_" + String(i + 1));
      }
    }
  }
}

void sendStatus() {
  String status = "STATUS:";
  for (int i = 0; i < 4; i++) {
    status += String(i + 1) + "=" + (valveStates[i] ? "ON" : "OFF");
    if (i < 3) status += ",";
  }
  sendResponse(status);

  Serial.println("📊 Status sent:");
  for (int i = 0; i < 4; i++) {
    Serial.print("   ");
    Serial.print(VALVE_NAMES[i]);
    Serial.print(": ");
    Serial.println(valveStates[i] ? "ON" : "OFF");
  }
}

void sendResponse(String response) {
  LoRa.beginPacket();
  LoRa.print(response);
  LoRa.endPacket();

  Serial.println("📤 Sent: " + response);
  Serial.println();
}

