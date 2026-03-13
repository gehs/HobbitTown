

### 📡 How to send these commands

You can use a browser extension like **Talend API Tester** or a command-line tool like **cURL**.

#### HobbitTown Hardware Test UI

To quickly exercise servos, misters, speakers, blowers, and audio without writing JSON, open:

* `http://<DEVICE_IP>/hobbit`

This page provides a small UI to set servo angles, speaker/mister/blower levels, and play audio tracks.

#### REST API (advanced)

* **Target URL for Lighting (WLED):** `http://[WLED_IP]/json/state`
* **Target URL for Audio/Fogger (HobbitTown):** `http://[BRAIN_IP]/json/event` (if we add a JSON handler to your WebLogic).

---

### 🎨 1. Lighting Commands (WLED)

Send these to your WLED ESP32 to change the mood instantly.

| Action | JSON Payload | What it does |
| --- | --- | --- |
| **All Off** | `{"on":false}` | Blackout the Shire. |
| **All On** | `{"on":true, "bri":128}` | Turn on at 50% brightness. |
| **Trigger Sunset** | `{"ps":3}` | Activates Preset 3 (Sunset). |
| **Fire Effect** | `{"seg":[{"fx":6, "sx":128, "ix":200}]}` | Makes Segment 0 look like a flicker. |
| **Night Mode** | `{"ps":4, "bri":50}` | Dim blue stars with low brightness. |

---

### 🔊 2. Audio & Event Commands (Brain ESP32)

These would be handled by your `WebLogic.h`. You can expand your `handleClient` to look for these specific "Keys."

| Action | JSON Payload | Resulting C++ Function |
| --- | --- | --- |
| **Party Trigger** | `{"event":"party"}` | `playPartyMusic()` |
| **Dragon Roar** | `{"event":"dragon"}` | `playDragonEvent()` |
| **Fog Pulse** | `{"event":"fog", "duration":2000}` | Triggers Relay for 2 seconds. |
| **Volume Set** | `{"volume":25}` | `dfPlayerBase.volume(25)` |

---

### 🧩 3. The "Master Scene" Command

This is the most powerful one. You can send a single JSON object that tells WLED and the Brain exactly what to do for a complex scene, like a **Rain Storm**.

```json
{
  "scene": "storm",
  "lighting": {
    "preset": 9,
    "transition": 50
  },
  "audio": {
    "track": 9,
    "loop": true
  },
  "atmosphere": {
    "fog": true
  }
}

```

---

### 🛠️ Upgrading `WebLogic.h` to read JSON

Since you’re comfortable with the C++ files now, you can eventually swap your simple `/party` route for a **JSON Parser**. This allows you to send one "packet" of data that contains multiple instructions.

**For your GitHub Tinker Session:**
In C++, parsing JSON is a bit heavy for the memory, so we usually use a library called **ArduinoJson**.

> **Pro-Tip:** If you find yourself wanting to control this from a "Dashboard" on your PC later, look into **Node-RED**. It’s a visual "wiring" tool for the internet that plays beautifully with the JSON commands we just mapped out.

---

### 🏁 Final Pre-Delivery Task

You have the code, the wiring, the logic, and now the API.

**Since your materials are still in transit, would you like me to create the "110V Mains Safety Guide" for your Mean Well power supply?** This covers how to safely wire the "Wall Plug" side of things so you don't have exposed high-voltage wires under your wooden Shire. Conclude your response with a next step.