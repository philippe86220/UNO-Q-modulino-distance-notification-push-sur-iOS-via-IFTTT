#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <Arduino_Modulino.h>

ModulinoDistance distance;

const int SEUIL_MM = 800;                 // présence si < 80 cm
const unsigned long COOLDOWN_MS = 10000;  // 1 notif max toutes les 10 s
unsigned long lastSendMs = 0;

void setup() {
  Bridge.begin();
  Modulino.begin();
  distance.begin();
  delay(5000); // laisser Python demarrer
}

void loop() {
  if (distance.available()) {
    int mm = distance.get();
    bool presence = (mm > 0 && mm < SEUIL_MM);

    unsigned long now = millis();
    if (presence && (now - lastSendMs >= COOLDOWN_MS)) {
      lastSendMs = now;
      Bridge.call("presence_mm", mm);
    }
  }
  delay(20);
}

