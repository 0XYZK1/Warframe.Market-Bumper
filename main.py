import eel
import requests
import time
import os
import threading
import json

WEB_DIR = 'web'
if not os.path.exists(WEB_DIR):
    os.makedirs(WEB_DIR)

# ... (HTML_TEMPLATE bleibt unverändert, du kannst ihn aus deiner Datei übernehmen) ...

GLOBAL_STATUS = {"message": "Bereit.", "type": "", "done": True}


@eel.expose
def get_status():
    return GLOBAL_STATUS


@eel.expose
def start_update_process(token):
    global GLOBAL_STATUS
    GLOBAL_STATUS = {"message": "Verbinde mit Warframe Market...", "type": "loading", "done": False}
    thread = threading.Thread(target=run_update, args=(token,))
    thread.start()


def run_update(token):
    global GLOBAL_STATUS

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Language": "en",
        "Platform": "pc",
        "Crossplay": "true"
    }

    try:
        # 1. Eigene Orders abrufen
        resp = requests.get("https://api.warframe.market/v2/orders/my", headers=headers, timeout=10)

        if resp.status_code == 401:
            GLOBAL_STATUS = {"message": "Fehler: Token ungültig oder abgelaufen.", "type": "error", "done": True}
            return
        elif resp.status_code == 403:
            GLOBAL_STATUS = {"message": "Fehler 403: Zugriff verweigert. Bitte prüfe Token und User-Agent.",
                             "type": "error", "done": True}
            return

        resp.raise_for_status()
        data = resp.json()

        payload = data.get("data", [])
        if isinstance(payload, list):
            orders = payload
        elif isinstance(payload, dict):
            orders = payload.get("orders", [])
        else:
            orders = []

        total = len(orders)

        if total == 0:
            GLOBAL_STATUS = {"message": "Keine aktiven Orders gefunden.", "type": "success", "done": True}
            return

        updated_count = 0
        for i, order in enumerate(orders):
            order_id = order.get("id")
            if not order_id:
                continue

            # --- KORREKTUR: Body mit den aktuellen Werten füllen ---
            # Die API erwartet beim PATCH die Felder, die aktualisiert werden sollen.
            # Wir senden die aktuellen Werte, damit sich nichts ändert, außer dem "zuletzt aktualisiert"-Zeitstempel.
            patch_body = {
                "platinum": order.get("platinum"),
                "quantity": order.get("quantity"),
                "visible": order.get("visible")
            }

            GLOBAL_STATUS = {"message": f"Aktualisiere {i + 1} von {total}...\n(Order ID: {order_id})",
                             "type": "loading", "done": False}

            # PATCH-Request mit JSON-Body
            put_resp = requests.patch(
                f"https://api.warframe.market/v2/order/{order_id}",
                headers=headers,
                data=json.dumps(patch_body),  # Body als JSON-String senden
                timeout=10
            )

            if put_resp.status_code in [200, 201, 204]:
                updated_count += 1
            else:
                # Logge den Fehler, falls ein anderer Status zurückkommt
                print(f"Fehler bei {order_id}: {put_resp.status_code} - {put_resp.text}")

            # Rate-Limit beachten (max. 3 Anfragen/Sekunde)
            time.sleep(0.4)

        GLOBAL_STATUS = {"message": f"Erfolgreich! {updated_count} von {total} Orders aktualisiert.", "type": "success",
                         "done": True}

    except requests.exceptions.RequestException as e:
        GLOBAL_STATUS = {"message": f"Netzwerkfehler: {str(e)}", "type": "error", "done": True}
    except Exception as e:
        GLOBAL_STATUS = {"message": f"Unerwarteter Fehler: {str(e)}", "type": "error", "done": True}


if __name__ == '__main__':
    print("Starte App... Bitte warten.")
    eel.init(WEB_DIR)
    eel.start('index.html', size=(500, 420), mode='edge', port=0)