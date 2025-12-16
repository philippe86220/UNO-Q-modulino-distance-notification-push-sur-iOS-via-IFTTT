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

