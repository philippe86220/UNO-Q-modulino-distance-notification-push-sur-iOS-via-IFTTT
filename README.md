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

# Principe du JSON et de la requête HTTP vers IFTTT

Dans ce projet, le cœur Linux de l’Arduino UNO Q envoie une notification vers IFTTT en utilisant une requête HTTP de type POST contenant des données au format JSON.

Ce mécanisme permet de transmettre simplement des informations (distance, date, source) vers un service cloud, qui se charge ensuite de notifier l’utilisateur (par exemple sur un iPhone).

---

## 1️⃣ Pourquoi utiliser du JSON ?

JSON (JavaScript Object Notation) est un format texte standard utilisé pour l’échange de données entre machines.

Ses principaux avantages sont :
- lisible par un humain,
- simple à générer,
- indépendant du langage (Python, C, JavaScript, etc.),
- largement utilisé par les services web (dont IFTTT).

JSON repose sur des paires **clé / valeur**.



Exemple simple de JSON

Voici un exemple de message JSON envoyé à IFTTT :

```json
{
  "value1": "distance_mm=742",
  "value2": "2025-12-16 11:13:22",
  "value3": "UNO Q"
}

```
## 2️⃣ Ce que fait exactement IFTTT
IFTTT propose un `Webhook` qui attend :  
- une requête HTTP POST,
- vers une URL spécifique,
- avec un contenu JSON optionnel.
Format général de l’URL :
```ruby
https://maker.ifttt.com/trigger/NOM_EVENEMENT/with/key/CLE_SECRETE
```

Dans notre cas :  
- `NOM_EVENEMENT` = `uno-q-presence`
- `CLE_SECRETE` = clé personnelle IFTTT

## 3️⃣ Le rôle des champs `value1`, `value2`, `value3`
IFTTT Webhooks accepte jusqu’à **trois valeurs nommées** :
| Champ    | Utilisation dans le projet |
| -------- | -------------------------- |
| `value1` | Distance mesurée           |
| `value2` | Date et heure              |
| `value3` | Source de l’événement      |


## 5️⃣ Envoi de la requête HTTP POST
La requête est envoyée ainsi :
```python
req = urllib.request.Request(
    IFTTT_URL,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
```
Ce que cela signifie :
- `data=data` → le corps de la requête contient le JSON
- `Content-Type`: application/json → on précise le format
- `POST` → **on envoie des données**
Puis :
```python
urllib.request.urlopen(req)
```
➡️ La requête est envoyée sur Internet depuis le cœur Linux de l’UNO Q.

## 6️⃣ Ce qui se passe ensuite
- IFTTT reçoit la requête
- Il reconnaît l’événement uno-q-presence
- Il lit value1, value2, value3
- Il déclenche l’applet associée
- L’iPhone reçoit la notification  
Tout cela se fait en **quelques centaines de millisecondes**.

##  7️⃣ Résumé en une phrase (très utile)
Le STM32 détecte un événement,    
le cœur Linux le transforme en message JSON et l’envoie via une requête HTTP sécurisée vers IFTTT,   
qui notifie ensuite l’iPhone.

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

##🙏 Remerciements
Ce projet a été développé avec l’aide de ChatGPT, pour l’architecture,   
le débogage et la mise en œuvre complète de la communication STM32 ↔ Linux.

