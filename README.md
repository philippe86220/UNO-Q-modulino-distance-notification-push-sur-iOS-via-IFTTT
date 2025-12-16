# Arduino UNO Q – Détecteur de présence avec Modulino Distance et notification iPhone (IFTTT)

Ce projet montre comment utiliser **l’Arduino UNO Q** pour créer un **détecteur de présence** basé sur le **Modulino Distance**, avec envoi d’une **notification sur iPhone** via **IFTTT**.

Il met en œuvre une architecture complète et réaliste :
- lecture capteur temps réel sur le **STM32**
- communication **STM32 → Linux** via `Arduino_RouterBridge`
- envoi HTTPS depuis le cœur Linux (Python)
- notification push sur iOS via IFTTT

---

## ✨ Fonctionnalités

- Détection de présence par distance (seuil configurable)
- Anti-rebond / limitation de notifications (cooldown)
- Communication STM32 ↔ Linux validée
- Notification instantanée sur iPhone
- Architecture conforme à la philosophie de l’UNO Q

---

## 🧠 Architecture générale

```
Modulino Distance
↓
STM32 (Arduino)
↓ Bridge.call()
Cœur Linux (Python)
↓ Webhook HTTPS
IFTTT
↓
Notification iPhone
```

---

## 🔧 Matériel utilisé

- Arduino **UNO Q**
- **Modulino Distance**
- iPhone avec application IFTTT installée

---

## 📦 Dépendances

### Côté STM32 (Arduino)
- Arduino_Modulino
- Arduino_RouterBridge

### Côté Linux (App Lab / Python)
- arduino.app_utils
- urllib / json (standard Python)

---

## 🚀 1. Code STM32 (Arduino)

```cpp
#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <Arduino_Modulino.h>

ModulinoDistance distance;

const int SEUIL_MM = 800;                 // présence si distance < 80 cm
const unsigned long COOLDOWN_MS = 10000;  // 1 notification max toutes les 10 s
unsigned long lastSendMs = 0;

void setup() {
  Bridge.begin();
  Modulino.begin();
  distance.begin();

  // Laisse le temps au script Python de s'initialiser
  delay(5000);
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
```
---

## 🐍 Code Python (Linux / App Lab)  
⚠️ Important : remplacez l’URL IFTTT par la vôtre.

```python
import time
import json
import datetime
import urllib.request
from arduino.app_utils import App, Bridge

print("Python ready", flush=True)

IFTTT_URL = "https://maker.ifttt.com/trigger/uno-q-presence/with/key/VOTRE_CLE_IFTTT"

def presence_mm(mm: int):
    print("Presence detectee, mm =", mm, flush=True)

    payload = {
        "value1": "distance_mm=" + str(mm),
        "value2": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "value3": "UNO Q"
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        IFTTT_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as r:
        print("IFTTT status:", r.status, flush=True)

    return True

Bridge.provide("presence_mm", presence_mm)

def loop():
    time.sleep(1)

App.run(user_loop=loop)
```

---

## 📱 Résultat attendu
Lorsqu’une présence est détectée à moins de 80 cm : 
- le STM32 envoie l’événement
- le cœur Linux déclenche le webhook
- **une notification apparaît sur l’iPhone**

---

## 🔒 Sécurité
Ne publiez jamais votre clé IFTTT en clair sur un dépôt public.
Pensez à la régénérer avant toute mise en ligne définitive.

## 🧩 À propos
Ce projet montre une utilisation avancée et réaliste de l’UNO Q, en respectant la séparation des rôles :
STM32 : capteurs, temps réel
Linux : réseau, HTTPS, services cloud



