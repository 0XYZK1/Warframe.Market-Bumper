import json
import os
import sys
import threading
import time

import requests
import webview

NAME = "TAOS | WF Bumper"
FROZEN = getattr(sys, "frozen", False)
RES = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
APP = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(RES, "web")
ICON = os.path.join(RES, "assets", "icon.ico")
CONFIG = os.path.join(APP, "config.json")

status = {"message": "SYSTEM READY.", "type": "", "done": True}


def save_token(token):
    try:
        with open(CONFIG, "w", encoding="utf-8") as f:
            json.dump({"token": token}, f)
    except OSError:
        pass


def bump_orders(token):
    global status

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
        r = requests.get("https://api.warframe.market/v2/orders/my", headers=headers, timeout=10)

        if r.status_code == 401:
            status = {"message": "ERROR: INVALID OR EXPIRED TOKEN.", "type": "error", "done": True}
            return
        if r.status_code == 403:
            status = {"message": "ERROR 403: ACCESS DENIED.", "type": "error", "done": True}
            return

        r.raise_for_status()
        data = r.json()

        payload = data.get("data", [])
        if isinstance(payload, dict):
            orders = payload.get("orders", [])
        else:
            orders = payload if isinstance(payload, list) else []

        if not orders:
            status = {"message": "NO ACTIVE ORDERS FOUND.", "type": "success", "done": True}
            return

        done = 0
        for i, order in enumerate(orders):
            order_id = order.get("id")
            if not order_id:
                continue

            body = {
                "platinum": order.get("platinum"),
                "quantity": order.get("quantity"),
                "visible": order.get("visible"),
            }

            status = {
                "message": f"UPDATING {i + 1} OF {len(orders)}...",
                "type": "loading",
                "done": False,
            }

            put = requests.patch(
                f"https://api.warframe.market/v2/order/{order_id}",
                headers=headers,
                data=json.dumps(body),
                timeout=10,
            )

            if put.status_code in (200, 201, 204):
                done += 1

            # nicht zu schnell, sonst sperrt die api irgendwann
            time.sleep(0.4)

        status = {
            "message": f"SUCCESS. {done}/{len(orders)} ORDERS UPDATED.",
            "type": "success",
            "done": True,
        }

    except requests.RequestException:
        status = {"message": "NETWORK ERROR.", "type": "error", "done": True}
    except Exception:
        status = {"message": "SYSTEM ERROR.", "type": "error", "done": True}


class Api:
    def load_token(self):
        if not os.path.exists(CONFIG):
            return ""
        try:
            with open(CONFIG, "r", encoding="utf-8") as f:
                return json.load(f).get("token", "")
        except (OSError, ValueError):
            return ""

    def get_status(self):
        return status

    def start_update_process(self, token):
        global status
        save_token(token)
        status = {"message": "CONNECTING TO MARKET...", "type": "loading", "done": False}
        threading.Thread(target=bump_orders, args=(token,), daemon=True).start()
        return True


def set_icon(window):
    # ohne das nimmt windows das python-icon in der taskleiste
    try:
        import clr

        clr.AddReference("System.Drawing")
        from System.Drawing import Icon

        window.native.Icon = Icon(ICON)
    except Exception:
        pass


if __name__ == "__main__":
    win = webview.create_window(
        NAME,
        os.path.join(WEB, "index.html"),
        width=500,
        height=420,
        resizable=False,
        background_color="#000000",
        js_api=Api(),
    )
    webview.start(set_icon, (win,), private_mode=False, storage_path=os.path.join(APP, ".webview"))
