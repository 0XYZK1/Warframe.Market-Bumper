import json
import os
import sys
import threading
import time

import requests
import webview

APP_NAME = "TAOS | WF Bumper"
IS_FROZEN = getattr(sys, "frozen", False)
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(sys.executable) if IS_FROZEN else os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
ICON_FILE = os.path.join(BASE_DIR, "assets", "icon.ico")
TOKEN_FILE = os.path.join(APP_DIR, "config.json")

GLOBAL_STATUS = {"message": "SYSTEM READY.", "type": "", "done": True}


def save_token(token):
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": token}, f)
    except Exception:
        pass


def run_update(token):
    global GLOBAL_STATUS

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Language": "en",
        "Platform": "pc",
        "Crossplay": "true",
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
                "visible": order.get("visible"),
            }

            GLOBAL_STATUS = {"message": f"UPDATING {i + 1} OF {total}...", "type": "loading", "done": False}

            put_resp = requests.patch(
                f"https://api.warframe.market/v2/order/{order_id}",
                headers=headers,
                data=json.dumps(patch_body),
                timeout=10,
            )

            if put_resp.status_code in [200, 201, 204]:
                updated_count += 1

            time.sleep(0.4)

        GLOBAL_STATUS = {
            "message": f"SUCCESS. {updated_count}/{total} ORDERS UPDATED.",
            "type": "success",
            "done": True,
        }

    except requests.exceptions.RequestException:
        GLOBAL_STATUS = {"message": "NETWORK ERROR.", "type": "error", "done": True}
    except Exception:
        GLOBAL_STATUS = {"message": "SYSTEM ERROR.", "type": "error", "done": True}


class Api:
    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("token", "")
            except Exception:
                return ""
        return ""

    def get_status(self):
        return GLOBAL_STATUS

    def start_update_process(self, token):
        global GLOBAL_STATUS
        save_token(token)
        GLOBAL_STATUS = {"message": "CONNECTING TO MARKET...", "type": "loading", "done": False}
        threading.Thread(target=run_update, args=(token,), daemon=True).start()
        return True


def set_taskbar_icon(window):
    """Give the WinForms window the same icon as the executable."""
    try:
        import clr  # provided by pythonnet

        clr.AddReference("System.Drawing")
        from System.Drawing import Icon

        window.native.Icon = Icon(ICON_FILE)
    except Exception:
        pass


if __name__ == "__main__":
    window = webview.create_window(
        APP_NAME,
        os.path.join(WEB_DIR, "index.html"),
        width=500,
        height=420,
        resizable=False,
        background_color="#000000",
        js_api=Api(),
    )

    webview.start(set_taskbar_icon, (window,), private_mode=False, storage_path=os.path.join(APP_DIR, ".webview"))
