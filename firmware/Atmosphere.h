// --- RELAY & FOGGER DEFINITIONS ---
const int RELAY_PIN = 18;          // Digital pin connected to Relay IN
unsigned long lastFogTime = 0;     // Stores the last time fog was triggered
bool isFogging = false;

// Custom Settings
const long fogDuration = 15000;    // How long to fog (15 seconds)
const long fogInterval = 300000;   // Wait between fogging (5 minutes)

void setupAtmosphere() {
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); 
}

void runAtmosphereCycle() {
  unsigned long currentMillis = millis();

  // Logic: If it's time to fog AND we aren't already fogging...
  if (!isFogging && (currentMillis - lastFogTime >= fogInterval)) {
    Serial.println("Atmosphere: Triggering morning mist...");
    digitalWrite(RELAY_PIN, LOW);  // Turn Relay ON
    lastFogTime = currentMillis;
    isFogging = true;
  }

  // Logic: If we've been fogging long enough, turn it off.
  if (isFogging && (currentMillis - lastFogTime >= fogDuration)) {
    Serial.println("Atmosphere: Mist cycle complete.");
    digitalWrite(RELAY_PIN, HIGH); // Turn Relay OFF
    isFogging = false;
  }
}