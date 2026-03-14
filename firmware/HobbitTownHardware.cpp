#include "HobbitTownHardware.h"

// Hardware globals
int8_t htSDA = HT_SDA_PIN;
int8_t htSCL = HT_SCL_PIN;
Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(HT_PCA9685_ADDR1);
Adafruit_PWMServoDriver pwm2 = Adafruit_PWMServoDriver(HT_PCA9685_ADDR2);

DFRobotDFPlayerMini dfPlayerBase;
DFRobotDFPlayerMini dfPlayerSpots;

uint8_t base_vol = 15;
uint8_t spot_vol = 15;

// --- HELPERS ---
static uint16_t map8to12(uint8_t v) {
  return map(v, 0, 255, 0, 4095);
}

static uint16_t servoPulseFromAngle(uint8_t deg) {
  return map(deg, 0, 180, 150, 600);
}

void setupHobbitTownHardware() {
  if (htSDA >= 0 && htSCL >= 0) {
    Serial.println(F("Hobbit Town: Initializing I2C..."));
    Wire.begin(htSDA, htSCL);
    Wire.setClock(400000);

    pwm1.begin();
    pwm1.setPWMFreq(60); 
    pwm2.begin();
    pwm2.setPWMFreq(60);

    // 74AHCT Gates
    pinMode(GATE_VOICES_PIN, OUTPUT);
    pinMode(GATE_DEEP_PIN, OUTPUT);
    digitalWrite(GATE_VOICES_PIN, HIGH); 
    digitalWrite(GATE_DEEP_PIN, HIGH);   

    // Shared TX Serial
    Serial2.begin(9600, SERIAL_8N1, AUDIO_RX_PIN, AUDIO_TX_PIN);

    // Init Voices (Player 2)
    digitalWrite(GATE_VOICES_PIN, LOW);
    delay(100);
    if (dfPlayerSpots.begin(Serial2)) {
      dfPlayerSpots.volume(spot_vol);
      Serial.println(F("Voices Online."));
    }
    digitalWrite(GATE_VOICES_PIN, HIGH);

    // Init Base (Player 1)
    digitalWrite(GATE_DEEP_PIN, LOW);
    delay(100);
    if (dfPlayerBase.begin(Serial2)) {
      dfPlayerBase.volume(base_vol);
      Serial.println(F("Base Online."));
    }
    digitalWrite(GATE_DEEP_PIN, HIGH);

    hobbitResetAll();
  }
}

void hobbitSetDoor(int id, uint8_t angle) {
  if (id < 1 || id > 3) return;
  pwm1.setPWM(id - 1, 0, servoPulseFromAngle(angle));
}

void hobbitSetMister(int id, uint8_t value) {
  if (id < 1 || id > 4) return;
  pwm2.setPWM(id - 1, 0, map8to12(value));
}

void hobbitSetSpeaker(int channel, uint8_t value) {
  if (channel >= 8 && channel <= 11) {
    pwm1.setPWM(channel, 0, (value > 0) ? 4095 : 0);
  } else if (channel == 12 || channel == 13) {
    pwm1.setPWM(channel, 0, map8to12(value));
  }
}

void hobbitSetBlower(int id, uint8_t value) {
  if (id < 1 || id > 3) return;
  pwm2.setPWM(3 + id, 0, map8to12(value));
}

void hobbitPlayAudio(int player, int track, bool loop) {
  int gate = (player == 2) ? GATE_VOICES_PIN : GATE_DEEP_PIN;
  digitalWrite(gate, LOW);
  delay(20);
  if (player == 1) {
    if (loop) dfPlayerBase.loop(track); else dfPlayerBase.play(track);
  } else {
    if (loop) dfPlayerSpots.loop(track); else dfPlayerSpots.play(track);
  }
  delay(50);
  digitalWrite(gate, HIGH);
}

void hobbitResetAll() {
  for (int i = 1; i <= 3; i++) hobbitSetDoor(i, 90);
  for (int i = 1; i <= 4; i++) hobbitSetMister(i, 0);
  for (int i = 8; i <= 11; i++) hobbitSetSpeaker(i, 0);
  hobbitSetSpeaker(12, 255);
  hobbitSetSpeaker(13, 255);
  for (int i = 1; i <= 3; i++) hobbitSetBlower(i, 0);
}

// --- WEB INTERFACE LOGIC ---
String processHobbitRequest(WebServer &server) {
  String msg = "";
  if (!server.hasArg("cmd")) return msg;
  String cmd = server.arg("cmd");

  if (cmd == "door") {
    hobbitSetDoor(server.arg("id").toInt(), server.arg("pos").toInt());
    msg = "Door " + server.arg("id") + " moved.";
  } 
  else if (cmd == "speaker") {
    hobbitSetSpeaker(server.arg("ch").toInt(), server.arg("val").toInt());
    msg = "Speaker channel " + server.arg("ch") + " set to " + server.arg("val");
  } 
  else if (cmd == "blower") {
    hobbitSetBlower(server.arg("id").toInt(), server.arg("val").toInt());
    msg = "Blower " + server.arg("id") + " set to " + server.arg("val");
  } 
  else if (cmd == "audio") {
    int p = server.arg("player").toInt();
    int t = server.arg("track").toInt();
    bool l = server.hasArg("loop");
    hobbitPlayAudio(p, t, l);
    msg = "Playing track " + String(t) + " on Player " + String(p);
  } 
  else if (cmd == "reset") {
    hobbitResetAll();
    msg = "All systems reset to safe defaults.";
  }
  return msg;
}

String buildHobbitPage(const String &msg) {
  String html;
  html += "<!doctype html><html><head><meta charset=\"utf-8\"><title>HobbitTown Test</title>";
  html += "<style>body{font-family:Arial,sans-serif;padding:2em;background:#f4f4f4;} .section{background:white;padding:15px;margin-bottom:10px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.1);}</style>";
  html += "</head><body><h1>HobbitTown Hardware Test</h1>";
  
  if (msg.length()) html += "<p style='color:green;'><strong>" + msg + "</strong></p>";

  html += "<div class='section'><h2>Doors (Servos - PCA1)</h2>";
  html += "<form action='/hobbit' method='get'><input type='hidden' name='cmd' value='door'>";
  html += "Door ID: <select name='id'><option value=1>1</option><option value=2>2</option><option value=3>3</option></select> ";
  html += "Angle (0-180): <input name='pos' type='number' value='90' min='0' max='180'> ";
  html += "<button type='submit'>Set Door</button></form></div>";

  html += "<div class='section'><h2>Speaker Matrix (Relays - PCA1)</h2>";
  html += "<form action='/hobbit' method='get'><input type='hidden' name='cmd' value='speaker'>";
  html += "Channel: <select name='ch'><option value=8>Smial A (Relay 1)</option><option value=9>Smial B (Relay 2)</option><option value=10>Smial C (Relay 3)</option><option value=11>Smial D (Relay 4)</option><option value=12>Exciter L</option><option value=13>Exciter R</option></select> ";
  html += "Power (0 or 255): <input name='val' type='number' value='255' min='0' max='255'> ";
  html += "<button type='submit'>Toggle Speaker</button></form></div>";

  html += "<div class='section'><h2>Environment (Blowers/Misters - PCA2)</h2>";
  html += "<form action='/hobbit' method='get'><input type='hidden' name='cmd' value='blower'>";
  html += "Blower ID: <select name='id'><option value=1>1</option><option value=2>2</option><option value=3>3</option></select> ";
  html += "Speed (0-255): <input name='val' type='number' value='255' min='0' max='255'> ";
  html += "<button type='submit'>Run Blower</button></form></div>";

  html += "<div class='section'><h2>Audio Command</h2>";
  html += "<form action='/hobbit' method='get'><input type='hidden' name='cmd' value='audio'>";
  html += "Player: <select name='player'><option value=1>Base (Exciters)</option><option value=2>Spots (Smials)</option></select> ";
  html += "Track #: <input name='track' type='number' value='1'> ";
  html += "Loop: <input type='checkbox' name='loop' value='1'> ";
  html += "<button type='submit'>Play Sound</button></form></div>";

  html += "<div class='section'><form action='/hobbit' method='get'><input type='hidden' name='cmd' value='reset'><button style='background:red;color:white;' type='submit'>EMERGENCY RESET ALL</button></form></div>";
  
  html += "</body></html>";
  return html;
}