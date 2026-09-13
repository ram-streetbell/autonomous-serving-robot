/* Autonomous Serving Robot - ESP32 low-level interface.
 * Outputs are disabled until an explicit command enables them.
 * PWM is intended for an external electrically suitable 0-5 V interface/DAC
 * or filtered/level-shifted stage for the Zbotic VR input. Never connect an
 * ESP32 GPIO directly to a 5 V input without verified interface circuitry.
 * Set GPIO constants only after wiring is verified.
 * Serial 115200: CMD,left,right,enable,sequence
 * Example: CMD,0.25,-0.25,1,42
 * Telemetry: TEL,left_tach,right_tach,enabled,sequence
 */
#include <Arduino.h>

static const int LEFT_PWM_PIN = -1;
static const int RIGHT_PWM_PIN = -1;
static const int LEFT_DIR_PIN = -1;
static const int RIGHT_DIR_PIN = -1;
static const int ENABLE_PIN = -1;
static const int LEFT_TACH_PIN = -1;
static const int RIGHT_TACH_PIN = -1;
static const uint32_t SERIAL_BAUD = 115200;
static const uint32_t COMMAND_TIMEOUT_MS = 500;
static const uint32_t TELEMETRY_PERIOD_MS = 100;

bool enabled = false;
float leftCmd = 0.0f, rightCmd = 0.0f;
uint32_t sequence = 0, lastCommandMs = 0, lastTelemetryMs = 0;
volatile uint32_t leftTach = 0, rightTach = 0;

void IRAM_ATTR onLeftTach() { leftTach++; }
void IRAM_ATTR onRightTach() { rightTach++; }

void safeDisable() {
  enabled = false; leftCmd = 0.0f; rightCmd = 0.0f;
  if (ENABLE_PIN >= 0) digitalWrite(ENABLE_PIN, LOW);
  if (LEFT_PWM_PIN >= 0) analogWrite(LEFT_PWM_PIN, 0);
  if (RIGHT_PWM_PIN >= 0) analogWrite(RIGHT_PWM_PIN, 0);
}

void writeMotor(float value, int pwmPin, int dirPin) {
  value = constrain(value, -1.0f, 1.0f);
  if (!enabled || pwmPin < 0 || dirPin < 0) return;
  digitalWrite(dirPin, value >= 0.0f ? HIGH : LOW);
  analogWrite(pwmPin, (int)(fabs(value) * 255.0f));
}

void applyOutputs() {
  if (ENABLE_PIN >= 0) digitalWrite(ENABLE_PIN, enabled ? HIGH : LOW);
  if (!enabled) {
    if (LEFT_PWM_PIN >= 0) analogWrite(LEFT_PWM_PIN, 0);
    if (RIGHT_PWM_PIN >= 0) analogWrite(RIGHT_PWM_PIN, 0);
    return;
  }
  writeMotor(leftCmd, LEFT_PWM_PIN, LEFT_DIR_PIN);
  writeMotor(rightCmd, RIGHT_PWM_PIN, RIGHT_DIR_PIN);
}

void parseCommand(char *line) {
  char *token = strtok(line, ",");
  if (!token || strcmp(token, "CMD") != 0) return;
  char *l = strtok(nullptr, ","), *r = strtok(nullptr, ",");
  char *e = strtok(nullptr, ","), *s = strtok(nullptr, ",");
  if (!l || !r || !e || !s) return;
  leftCmd = constrain(atof(l), -1.0f, 1.0f);
  rightCmd = constrain(atof(r), -1.0f, 1.0f);
  enabled = atoi(e) != 0;
  sequence = strtoul(s, nullptr, 10);
  lastCommandMs = millis();
  applyOutputs();
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  if (ENABLE_PIN >= 0) pinMode(ENABLE_PIN, OUTPUT);
  if (LEFT_DIR_PIN >= 0) pinMode(LEFT_DIR_PIN, OUTPUT);
  if (RIGHT_DIR_PIN >= 0) pinMode(RIGHT_DIR_PIN, OUTPUT);
  if (LEFT_PWM_PIN >= 0) pinMode(LEFT_PWM_PIN, OUTPUT);
  if (RIGHT_PWM_PIN >= 0) pinMode(RIGHT_PWM_PIN, OUTPUT);
  if (LEFT_TACH_PIN >= 0) { pinMode(LEFT_TACH_PIN, INPUT_PULLUP); attachInterrupt(digitalPinToInterrupt(LEFT_TACH_PIN), onLeftTach, RISING); }
  if (RIGHT_TACH_PIN >= 0) { pinMode(RIGHT_TACH_PIN, INPUT_PULLUP); attachInterrupt(digitalPinToInterrupt(RIGHT_TACH_PIN), onRightTach, RISING); }
  safeDisable(); lastCommandMs = millis(); Serial.println("READY,DISABLED");
}

void loop() {
  static char buffer[96]; static size_t index = 0;
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (index > 0) { buffer[index] = '\0'; parseCommand(buffer); index = 0; }
    } else if (index < sizeof(buffer) - 1) buffer[index++] = c;
    else { index = 0; safeDisable(); }
  }
  if (enabled && millis() - lastCommandMs > COMMAND_TIMEOUT_MS) safeDisable();
  if (millis() - lastTelemetryMs >= TELEMETRY_PERIOD_MS) {
    lastTelemetryMs = millis();
    noInterrupts(); uint32_t l = leftTach, r = rightTach; interrupts();
    Serial.printf("TEL,%lu,%lu,%d,%lu\n", (unsigned long)l, (unsigned long)r, enabled ? 1 : 0, (unsigned long)sequence);
  }
}
