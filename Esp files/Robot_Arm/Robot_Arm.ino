#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ESP32Servo.h>
#include <LittleFS.h>
#include "esp_netif.h"

// =======================
// WiFi AP
// =======================
const char *ssid = "ESP32-Control";
const char *password = "12345678";

IPAddress local_IP(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

// =======================
// Server
// =======================
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// =======================
// Servo Struct
// =======================
struct ServoData {
  Servo servo;
  int pin;
  const char *name;
  int current;
  int target;
  int min;
  int max;
  int reset;
};

ServoData servos[] = {
  { Servo(), 26, "Base", 90, 90, 0, 180, 90},
  { Servo(), 25, "Shoulder", 90, 90, 0, 180, 90},
  { Servo(), 33, "Elbow", 90, 90, 0, 180, 90},
  { Servo(), 32, "Gripper", 90, 90, 0, 180, 90}
};

#define SERVO_COUNT 4

// =======================
// L298N
// =======================
const int in1 = 13;
const int in2 = 12;
const int in3 = 14;
const int in4 = 27;

// =======================
// Timing
// =======================
unsigned long lastMove = 0;
const int stepDelay = 20;
const int stepSize = 1;

unsigned long lastBroadcast = 0;
const int broadcastInterval = 500;

unsigned long lastMsgTime = 0;
const int msgCooldown = 20;

bool shouldBroadcast = false;

// =======================
// Reset Function
// =======================
void resetServos() {
  Serial.println("=== RESET SERVOS ===");

  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].target = servos[i].reset;

    Serial.print(servos[i].name);
    Serial.print(" -> Reset to ");
    Serial.println(servos[i].reset);
  }
}

// =======================
// Motor Control
// =======================
void controlCar(char command) {

  Serial.print("Car Command: ");
  Serial.println(command);

  switch (command) {
    case 'F':
      Serial.println("Forward");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      break;

    case 'B':
      Serial.println("Backward");
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, LOW);
      digitalWrite(in4, HIGH);
      break;

    case 'L':
      Serial.println("Left");
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      digitalWrite(in3, HIGH);
      digitalWrite(in4, LOW);
      break;

    case 'R':
      Serial.println("Right");
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, HIGH);
      break;

    case 'S':
      Serial.println("Stop");
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, LOW);
      break;
  }
}

// =======================
// Helpers
// =======================
int findServoIndex(const char *name) {
  for (int i = 0; i < SERVO_COUNT; i++) {
    if (strcmp(servos[i].name, name) == 0) return i;
  }
  return -1;
}

void buildJSON(char *buffer) {
  snprintf(buffer, 128,
           "{\"Base\":%d,\"Shoulder\":%d,\"Elbow\":%d,\"Gripper\":%d}",
           servos[0].current,
           servos[1].current,
           servos[2].current,
           servos[3].current);
}

// =======================
// WebSocket Handler
// =======================
void handleWebSocket(void *arg, uint8_t *data, size_t len, AsyncWebSocketClient *client) {

  if (millis() - lastMsgTime < msgCooldown) return;
  lastMsgTime = millis();

  AwsFrameInfo *info = (AwsFrameInfo *)arg;
  if (!(info->final && info->index == 0 && info->len == len)) return;

  char msg[64];
  size_t safeLen = (len < sizeof(msg) - 1) ? len : sizeof(msg) - 1;
  memcpy(msg, data, safeLen);
  msg[safeLen] = '\0';

  // =========================
  // CAR CONTROL
  // =========================
  if (strlen(msg) == 1) {
    controlCar(msg[0]);
    return;
  }

  // =========================
  // RESET
  // =========================
  if (strcmp(msg, "RESET") == 0) {
    resetServos();
    return;
  }

  // =========================
  // GET ALL
  // =========================
  if (strcmp(msg, "GET") == 0) {
    Serial.println("GET ALL Servos");

    char buffer[128];
    buildJSON(buffer);
    client->text(buffer);
    return;
  }

  // =========================
  // GET ONE
  // =========================
  if (strncmp(msg, "GET,", 4) == 0) {
    char *name = msg + 4;

    Serial.print("GET Servo: ");
    Serial.println(name);

    int idx = findServoIndex(name);

    if (idx != -1) {
      char buffer[32];
      snprintf(buffer, sizeof(buffer), "%s:%d", servos[idx].name, servos[idx].current);
      client->text(buffer);
    }
    return;
  }

  // =========================
  // SET SERVO
  // =========================
  char *comma = strchr(msg, ',');
  if (comma != NULL) {
    *comma = '\0';

    char *name = msg;
    int value = atoi(comma + 1);

    int idx = findServoIndex(name);

    if (idx != -1) {
      int newTarget = constrain(value, servos[idx].min, servos[idx].max);

      Serial.print("Servo Move -> ");
      Serial.print(name);
      Serial.print(" : ");
      Serial.print(servos[idx].current);
      Serial.print(" -> ");
      Serial.println(newTarget);

      servos[idx].target = newTarget;
    }
  }
}

// =======================
// Events
// =======================
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len) {

  if (type == WS_EVT_CONNECT) {
    Serial.println("Client connected");

    char buffer[128];
    buildJSON(buffer);
    client->text(buffer);
  }

  else if (type == WS_EVT_DATA) {
    handleWebSocket(arg, data, len, client);
  }
}

// =======================
// Setup
// =======================
void setup() {
  Serial.begin(115200);

  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  esp_netif_init();

  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS Error");
    return;
  }

  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_IP, gateway, subnet);

  Serial.print("IP: ");
  Serial.println(WiFi.softAPIP());

  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].servo.attach(servos[i].pin);
    servos[i].servo.write(servos[i].current);
  }

  ws.onEvent(onEvent);
  server.addHandler(&ws);

  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*");

  server.begin();
}

// =======================
// Loop
// =======================
void loop() {

  // Smooth Servo Movement
  if (millis() - lastMove > stepDelay) {
    lastMove = millis();

    for (int i = 0; i < SERVO_COUNT; i++) {

      if (servos[i].current < servos[i].target)
        servos[i].current += stepSize;

      else if (servos[i].current > servos[i].target)
        servos[i].current -= stepSize;

      servos[i].servo.write(servos[i].current);
    }
  }

  // Broadcast
  if (millis() - lastBroadcast > broadcastInterval) {
    lastBroadcast = millis();
    shouldBroadcast = true;
  }

  if (shouldBroadcast) {
    shouldBroadcast = false;

    char buffer[128];
    buildJSON(buffer);
    ws.textAll(buffer);
  }

  ws.cleanupClients();
}