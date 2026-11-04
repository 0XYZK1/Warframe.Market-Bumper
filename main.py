import eel
import requests
import time
import os
import threading
import json

WEB_DIR = 'web'
if not os.path.exists(WEB_DIR):
    os.makedirs(WEB_DIR)

TOKEN_FILE = 'config.json'


def save_token(token):
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump({"token": token}, f)
    except:
        pass


@eel.expose
def load_token():
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                data = json.load(f)
                return data.get("token", "")
        except:
            return ""
    return ""


GLOBAL_STATUS = {"message": "SYSTEM READY.", "type": "", "done": True}


@eel.expose
def get_status():
    return GLOBAL_STATUS


@eel.expose
def start_update_process(token):
    global GLOBAL_STATUS
    # HIER: Speichere den Token sofort ab, wenn der User auf Start drückt!
    save_token(token)

    GLOBAL_STATUS = {"message": "CONNECTING TO MARKET...", "type": "loading", "done": False}
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
        resp = requests.get("https://api.warframe.market/v2/orders/my", headers=headers, timeout=10)

        if resp.status_code == 401:
            GLOBAL_STATUS = {"message": "ERROR: INVALID OR EXPIRED TOKEN.", "type": "error", "done": True}
            return
        elif resp.status_code == 403:
            GLOBAL_STATUS = {"message": "ERROR 403: ACCESS DENIED.", "type": "error", "done": True}
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
            GLOBAL_STATUS = {"message": "NO ACTIVE ORDERS FOUND.", "type": "success", "done": True}
            return

        updated_count = 0
        for i, order in enumerate(orders):
            order_id = order.get("id")
            if not order_id:
                continue

            patch_body = {
                "platinum": order.get("platinum"),
                "quantity": order.get("quantity"),
                "visible": order.get("visible")
            }

            GLOBAL_STATUS = {"message": f"UPDATING {i + 1} OF {total}...", "type": "loading", "done": False}

            put_resp = requests.patch(
                f"https://api.warframe.market/v2/order/{order_id}",
                headers=headers,
                data=json.dumps(patch_body),
                timeout=10
            )

            if put_resp.status_code in [200, 201, 204]:
                updated_count += 1

            time.sleep(0.4)

        GLOBAL_STATUS = {"message": f"SUCCESS. {updated_count}/{total} ORDERS UPDATED.", "type": "success",
                         "done": True}

    except requests.exceptions.RequestException as e:
        GLOBAL_STATUS = {"message": f"NETWORK ERROR.", "type": "error", "done": True}
    except Exception as e:
        GLOBAL_STATUS = {"message": f"SYSTEM ERROR.", "type": "error", "done": True}


if __name__ == '__main__':
    eel.init(WEB_DIR)
    # eel startet jetzt mit dem sauberen Titel
    eel.start('index.html', size=(500, 420), mode='edge', port=0)