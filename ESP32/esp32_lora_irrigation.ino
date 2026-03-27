/*
 * ESP32 LoRa Irrigation Controller
 * Controls 4 solenoid valves via LoRa commands from Raspberry Pi
 *
 * Hardware:
 * - ESP32 board
 * - EBYTE E220/E32 LoRa module (UART)
 * - 4 relay modules for solenoid valves
 *
 * EBYTE LoRa UART Pins:
 * - RXD → GPIO16 (ESP32 TX2)
 * - TXD → GPIO17 (ESP32 RX2)
 * - M0  → GPIO4
 * - M1  → GPIO2
 * - AUX → GPIO15
 * - VCC → 3.3V
 * - GND → GND
 *
 * Solenoid Relay Pins:
 * - Relay 1 → GPIO13
 * - Relay 2 → GPIO12
 * - Relay 3 → GPIO27
 * - Relay 4 → GPIO26
 */

// EBYTE LoRa UART pins
#define LORA_RXD  16   // ESP32 TX2 → EBYTE RXD
#define LORA_TXD  17   // ESP32 RX2 → EBYTE TXD
#define LORA_M0   4    // Mode select M0
#define LORA_M1   2    // Mode select M1
#define LORA_AUX  15   // Module busy indicator

// Use Serial2 for LoRa UART
#define LoRaSerial Serial2
#define LORA_BAUD  9600

// Solenoid Valve Pins (connected to relay modules)
const int VALVE_PINS[4] = {13, 12, 27, 26};  // GPIO pins for 4 valves
const char* VALVE_NAMES[4] = {"Valve 1 (Jardín)", "Valve 2 (Huerta)",
                               "Valve 3 (Césped)", "Valve 4 (Árboles)"};

// Valve states
bool valveStates[4] = {false, false, false, false};

// Device ID
const String DEVICE_ID = "ESP32_IRR_001";

// Timer for auto-shutoff
unsigned long valveTimers[4] = {0, 0, 0, 0};
unsigned long valveDurations[4] = {0, 0, 0, 0};

// -------------------------------------------------------
// EBYTE mode helpers
// -------------------------------------------------------
void setLoRaMode(int m0, int m1) {
  digitalWrite(LORA_M0, m0);
  digitalWrite(LORA_M1, m1);
  delay(100);
  waitAux();
}

void waitAux(unsigned long timeout_ms = 3000) {
  unsigned long start = millis();
  while (digitalRead(LORA_AUX) == LOW) {
    if (millis() - start > timeout_ms) {
      Serial.println("⚠️ AUX timeout");
      return;
    }
    delay(10);
  }
}

void setNormalMode()  { setLoRaMode(LOW, LOW); }   // Transparent TX/RX
void setSleepMode()   { setLoRaMode(HIGH, HIGH); }  // Config / sleep

// -------------------------------------------------------
// Setup
// -------------------------------------------------------
void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("======================================");
  Serial.println("  ESP32 LoRa EBYTE Irrigation Ctrl");
  Serial.println("======================================");

  // Initialize EBYTE control pins
  pinMode(LORA_M0, OUTPUT);
  pinMode(LORA_M1, OUTPUT);
  pinMode(LORA_AUX, INPUT);

  // Initialize valve pins
  for (int i = 0; i < 4; i++) {
    pinMode(VALVE_PINS[i], OUTPUT);
    digitalWrite(VALVE_PINS[i], LOW);  // All valves OFF
  }

  // Initialize LoRa UART (Serial2)
  LoRaSerial.begin(LORA_BAUD, SERIAL_8N1, LORA_TXD, LORA_RXD);

  // Set normal (transparent) mode
  setNormalMode();

  Serial.println("✅ LoRa UART initialized");
  Serial.print("   EBYTE pins: RXD=GPIO");
  Serial.print(LORA_RXD);
  Serial.print(", TXD=GPIO");
  Serial.print(LORA_TXD);
  Serial.print(", M0=GPIO");
  Serial.print(LORA_M0);
  Serial.print(", M1=GPIO");
  Serial.print(LORA_M1);
  Serial.print(", AUX=GPIO");
  Serial.println(LORA_AUX);
  Serial.println("\n⏳ Waiting for commands...\n");
}

// -------------------------------------------------------
// Main loop
// -------------------------------------------------------
void loop() {
  // Check for incoming LoRa UART data
  if (LoRaSerial.available()) {
    String message = LoRaSerial.readStringUntil('\n');
    message.trim();
    if (message.length() > 0) {
      Serial.println("📡 Received: " + message);
      processCommand(message);
    }
  }

  // Check valve auto-off timers
  checkValveTimers();

  delay(10);
}

// -------------------------------------------------------
// Command processing
// -------------------------------------------------------
void processCommand(String message) {
  // Parse command format: "CMD:VALVE:DURATION"
  // Examples: "ON:1:300", "OFF:2", "STATUS", "ALL_OFF", "PING"

  int firstColon = message.indexOf(':');
  int secondColon = message.indexOf(':', firstColon + 1);

  String cmd = message.substring(0, firstColon > 0 ? firstColon : message.length());
  String valveStr = "";
  String durationStr = "";

  if (firstColon > 0) {
    if (secondColon > 0) {
      valveStr = message.substring(firstColon + 1, secondColon);
      durationStr = message.substring(secondColon + 1);
    } else {
      valveStr = message.substring(firstColon + 1);
    }
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
    Serial.println("❌ Unknown command: " + cmd);
  }
}

// -------------------------------------------------------
// Valve control
// -------------------------------------------------------
void turnValveOn(int index, int duration) {
  if (index < 0 || index >= 4) return;

  digitalWrite(VALVE_PINS[index], HIGH);
  valveStates[index] = true;

  if (duration > 0) {
    valveTimers[index] = millis();
    valveDurations[index] = (unsigned long)duration * 1000UL;
    Serial.print("✅ ");
    Serial.print(VALVE_NAMES[index]);
    Serial.print(" ON (auto-off in ");
    Serial.print(duration);
    Serial.println("s)");
  } else {
    valveTimers[index] = 0;
    valveDurations[index] = 0;
    Serial.print("✅ ");
    Serial.print(VALVE_NAMES[index]);
    Serial.println(" ON (manual)");
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

// -------------------------------------------------------
// Responses via LoRa UART
// -------------------------------------------------------
void sendStatus() {
  String status = "STATUS:";
  for (int i = 0; i < 4; i++) {
    status += String(i + 1) + "=" + (valveStates[i] ? "ON" : "OFF");
    if (i < 3) status += ",";
  }
  sendResponse(status);

  Serial.println("📊 Status sent");
}

void sendResponse(String response) {
  waitAux();
  LoRaSerial.println(response);  // println adds \n terminator
  Serial.println("📤 TX: " + response);
}
