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
};

ServoData servos[] = {
  { Servo(), 27, "Base", 90, 90 },
  { Servo(), 26, "Shoulder", 90, 90 },
  { Servo(), 25, "Elbow", 90, 90 },
  { Servo(), 33, "Gripper", 90, 90 }
};

const int in1 = 32;
const int in2 = 13;
const int in3 = 12;
const int in4 = 14;

#define SERVO_COUNT 4

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
// Helpers
// =======================
// دالة التحكم في المواتير
void controlCar(String command) {
  if (command == "F") {  // قدام
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
    Serial.println("Car Farward");
  } else if (command == "B") {  // ورا
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
    Serial.println("Car Back");
  } else if (command == "L") {  // شمال
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
    Serial.println("Car Left");
  } else if (command == "R") {  // يمين
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
    Serial.println("Car Right");
  } else if (command == "S") {  // وقف
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
    Serial.println("Car Stoped!!");
  }
}

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
  // 1. Anti-spam
  if (millis() - lastMsgTime < msgCooldown) return;
  lastMsgTime = millis();

  AwsFrameInfo *info = (AwsFrameInfo *)arg;
  if (!(info->final && info->index == 0 && info->len == len)) return;

  // 2. انقل الداتا لمكان آمن بدل ما تعدل في الـ pointer الأصلي
  char msg[64];  // حجم كافي للرسايل بتاعتك
  size_t safeLen = (len < sizeof(msg) - 1) ? len : sizeof(msg) - 1;
  memcpy(msg, data, safeLen);
  msg[safeLen] = '\0';  // قفل السلسلة هنا بأمان

  if (strlen(msg) == 1) {
    // لو الرسالة حرف واحد يبقى غالباً أمر حركة للعربية
    controlCar(String(msg));
    
    return;
  }

  // =========================
  // GET ALL
  // =========================
  if (strcmp(msg, "GET") == 0) {
    char buffer[128];
    buildJSON(buffer);
    client->text(buffer);
    Serial.println("All Servo's info:");
    Serial.println(buffer);
    return;
  }

  // =========================
  // GET ONE (مثلاً: GET,Base)
  // =========================
  if (strncmp(msg, "GET,", 4) == 0) {
    char *name = msg + 4;
    int idx = findServoIndex(name);
    if (idx != -1) {
      char buffer[32];
      snprintf(buffer, sizeof(buffer), "%s:%d", servos[idx].name, servos[idx].current);
      client->text(buffer);
    }
    return;
  }

  // =========================
  // SET (مثلاً: Base,120)
  // =========================
  char *comma = strchr(msg, ',');
  if (comma != NULL) {
    *comma = '\0';
    char *name = msg;
    int value = atoi(comma + 1);

    int idx = findServoIndex(name);
    if (idx != -1) {
      servos[idx].target = constrain(value, 0, 180);
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

  // مهم للاستقرار
  esp_netif_init();

  // LittleFS
  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS Error");
    return;
  }

  // WiFi AP
  WiFi.softAP(ssid, password);
  WiFi.softAPConfig(local_IP, gateway, subnet);

  Serial.print("IP: ");
  Serial.println(WiFi.softAPIP());

  // Servos
  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].servo.attach(servos[i].pin);
    servos[i].servo.write(servos[i].current);
  }

  // WebSocket
  ws.onEvent(onEvent);
  server.addHandler(&ws);

  // Serve HTML
  server.serveStatic("/", LittleFS, "/").setDefaultFile("index.html");

  DefaultHeaders::Instance().addHeader("Access-Control-Allow-Origin", "*");

  server.begin();
}

// =======================
// Loop
// =======================
void loop() {

  // 🟢 Smooth Movement
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

  // 📡 Broadcast Flag
  if (millis() - lastBroadcast > broadcastInterval) {
    lastBroadcast = millis();
    shouldBroadcast = true;
  }

  // 📡 Safe Broadcast
  if (shouldBroadcast) {
    shouldBroadcast = false;

    char buffer[128];
    buildJSON(buffer);
    ws.textAll(buffer);
  }

  ws.cleanupClients();
}