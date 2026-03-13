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

static uint16_t map8to12(uint8_t v) {
  return map(v, 0, 255, 0, 4095);
}

static uint16_t servoPulseFromAngle(uint8_t deg) {
  // Common range for 0-180 deg servos on PCA9685 (approx 0.5-2.5ms)
  return map(deg, 0, 180, 150, 600);
}

void setupHobbitTownHardware() {
  if (htSDA >= 0 && htSCL >= 0) {
    Serial.println(F("Hobbit Town: Initializing HT I2C..."));
    Wire.begin(htSDA, htSCL);
    Wire.setClock(400000);

    // PCA9685 drivers
    Serial.println(F("Hobbit Town: Waking up Bag End Servo Driver..."));
    pwm1.begin();
    pwm1.setOscillatorFrequency(27000000);
    pwm1.setPWMFreq(50); // 50Hz for Servos and Misters

    pwm2.begin();
    pwm2.setOscillatorFrequency(27000000);
    pwm2.setPWMFreq(50);

    // Initial hardware state: safe defaults
    hobbitResetAll();

    // Initialize audio
    Serial.println(F("Hobbit Town: Starting DFPlayer Mini..."));
    Serial1.begin(9600, SERIAL_8N1, 5, 4);
    Serial2.begin(9600, SERIAL_8N1, 19, 18);

    if (dfPlayerBase.begin(Serial1)) {
      Serial.println(F("Hobbit Town: Audio Base Online."));
      dfPlayerBase.volume(base_vol);
    } else {
      Serial.println(F("Hobbit Town: DFPlayer Base NOT FOUND. Check SD/Wiring."));
    }
    if (dfPlayerSpots.begin(Serial2)) {
      Serial.println(F("Hobbit Town: Audio Spots Online."));
      dfPlayerSpots.volume(spot_vol);
    } else {
      Serial.println(F("Hobbit Town: DFPlayer Spots NOT FOUND. Check SD/Wiring."));
    }
  }
}

void hobbitSetDoor(int id, uint8_t angle) {
  if (id < 1 || id > 3) return;
  uint16_t pulse = servoPulseFromAngle(angle);
  pwm1.setPWM(id - 1, 0, pulse);
}

void hobbitSetMister(int id, uint8_t value) {
  if (id < 1 || id > 4) return;
  uint16_t duty = map8to12(value);
  pwm2.setPWM(id - 1, 0, duty);
}

void hobbitSetSpeaker(int channel, uint8_t value) {
  if (channel < 8 || channel > 13) return;
  uint16_t duty = map8to12(value);
  pwm1.setPWM(channel, 0, duty);
}

void hobbitSetBlower(int id, uint8_t value) {
  if (id < 1 || id > 3) return;
  uint16_t duty = map8to12(value);
  pwm2.setPWM(3 + id, 0, duty); // blower channels 4-6
}

void hobbitPlayAudio(int player, int track, bool loop) {
  if (player == 1) {
    if (loop) dfPlayerBase.loop(track);
    else dfPlayerBase.play(track);
  } else if (player == 2) {
    if (loop) dfPlayerSpots.loop(track);
    else dfPlayerSpots.play(track);
  }
}

void hobbitResetAll() {
  // Doors: midpoint
  hobbitSetDoor(1, 90);
  hobbitSetDoor(2, 90);
  hobbitSetDoor(3, 90);

  // Misters off
  for (int i = 1; i <= 4; i++) hobbitSetMister(i, 0);

  // Speaker matrix: spots off, exciters on
  hobbitSetSpeaker(8, 0);
  hobbitSetSpeaker(9, 0);
  hobbitSetSpeaker(10, 0);
  hobbitSetSpeaker(11, 0);
  hobbitSetSpeaker(12, 255);
  hobbitSetSpeaker(13, 255);

  // Blowers off
  for (int i = 1; i <= 3; i++) hobbitSetBlower(i, 0);
}

String processHobbitRequest(WebServer &server) {
  String msg;
  if (server.hasArg("cmd")) {
    String cmd = server.arg("cmd");
    if (cmd == "door") {
      int id = server.hasArg("id") ? server.arg("id").toInt() : 1;
      int pos = server.hasArg("pos") ? server.arg("pos").toInt() : 90;
      hobbitSetDoor(id, pos);
      msg = "Door " + String(id) + " -> " + String(pos) + "°";
    } else if (cmd == "mister") {
      int id = server.hasArg("id") ? server.arg("id").toInt() : 1;
      int val = server.hasArg("val") ? server.arg("val").toInt() : 0;
      hobbitSetMister(id, val);
      msg = "Mister " + String(id) + " -> " + String(val);
    } else if (cmd == "speaker") {
      int ch = server.hasArg("ch") ? server.arg("ch").toInt() : 8;
      int val = server.hasArg("val") ? server.arg("val").toInt() : 0;
      hobbitSetSpeaker(ch, val);
      msg = "Speaker ch " + String(ch) + " -> " + String(val);
    } else if (cmd == "blower") {
      int id = server.hasArg("id") ? server.arg("id").toInt() : 1;
      int val = server.hasArg("val") ? server.arg("val").toInt() : 0;
      hobbitSetBlower(id, val);
      msg = "Blower " + String(id) + " -> " + String(val);
    } else if (cmd == "audio") {
      int player = server.hasArg("player") ? server.arg("player").toInt() : 1;
      int track = server.hasArg("track") ? server.arg("track").toInt() : 1;
      bool loop = server.hasArg("loop") && server.arg("loop") == "1";
      hobbitPlayAudio(player, track, loop);
      msg = "Audio player " + String(player) + " -> track " + String(track) + (loop ? " (loop)" : "");
    } else if (cmd == "reset") {
      hobbitResetAll();
      msg = "Reset to safe default state.";
    }
  }
  return msg;
}

String buildHobbitPage(const String &msg) {
  String html;
  html += "<!doctype html><html><head><meta charset=\"utf-8\"><title>HobbitTown Test</title>";
  html += "<style>body{font-family:Arial,Helvetica,sans-serif;padding:1em;}button{margin:0.25em 0;}</style>";
  html += "</head><body><h1>HobbitTown Hardware Test</h1>";
  if (msg.length()) html += "<p><strong>" + msg + "</strong></p>";
  html += "<h2>Doors (Servos)</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"door\">";
  html += "Door: <select name=\"id\"><option value=1>1</option><option value=2>2</option><option value=3>3</option></select> ";
  html += "Angle: <input name=\"pos\" type=\"number\" value=\"90\" min=\"0\" max=\"180\"> ";
  html += "<button type=\"submit\">Set</button></form>";
  html += "<h2>Misters</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"mister\">";
  html += "Mister: <select name=\"id\"><option value=1>1</option><option value=2>2</option><option value=3>3</option><option value=4>Stream</option></select> ";
  html += "Value: <input name=\"val\" type=\"number\" value=\"0\" min=\"0\" max=\"255\"> ";
  html += "<button type=\"submit\">Set</button></form>";
  html += "<h2>Speaker Matrix</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"speaker\">";
  html += "Channel: <select name=\"ch\"><option value=8>Spot 1</option><option value=9>Spot 2</option><option value=10>Spot 3</option><option value=11>Spot 4</option><option value=12>Exciter L</option><option value=13>Exciter R</option></select> ";
  html += "Value: <input name=\"val\" type=\"number\" value=\"0\" min=\"0\" max=\"255\"> ";
  html += "<button type=\"submit\">Set</button></form>";
  html += "<h2>Blowers</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"blower\">";
  html += "Blower: <select name=\"id\"><option value=1>1</option><option value=2>2</option><option value=3>3</option></select> ";
  html += "Value: <input name=\"val\" type=\"number\" value=\"0\" min=\"0\" max=\"255\"> ";
  html += "<button type=\"submit\">Set</button></form>";
  html += "<h2>Audio</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"audio\">";
  html += "Player: <select name=\"player\"><option value=1>Base</option><option value=2>Spots</option></select> ";
  html += "Track: <input name=\"track\" type=\"number\" value=\"1\" min=\"1\"> ";
  html += "Loop: <input name=\"loop\" type=\"checkbox\" value=1> ";
  html += "<button type=\"submit\">Play</button></form>";
  html += "<h2>Quick Actions</h2>";
  html += "<form action=\"/hobbit\" method=\"get\">";
  html += "<input type=\"hidden\" name=\"cmd\" value=\"reset\">";
  html += "<button type=\"submit\">Reset to Safe Defaults</button></form>";
  html += "</body></html>";
  return html;
}
