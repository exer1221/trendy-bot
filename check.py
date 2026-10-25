import json
import os
import pathlib

import requests

BASE = "https://www.maquillajetrendyshop.com"
SEARCH_TERM = "calendario adviento"
KEYWORDS = ["adviento"]  # palabra que debe estar en el nombre
STATE = pathlib.Path("seen.json")

PHONE = os.environ["WA_PHONE"]    # ej: +573001234567
APIKEY = os.environ["WA_APIKEY"]  # la que te dio CallMeBot


def buscar():
    r = requests.get(
        f"{BASE}/api/catalog_system/pub/products/search",
        params={"ft": SEARCH_TERM},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def disponible(prod):
    for item in prod.get("items", []):
        for seller in item.get("sellers", []):
            if seller["commertialOffer"].get("AvailableQuantity", 0) > 0:
                return True
    return False


def avisar(texto):
    r = requests.get(
        "https://api.callmebot.com/whatsapp.php",
        params={"phone": PHONE, "text": texto, "apikey": APIKEY},
        timeout=30,
    )
    print("WhatsApp:", r.status_code, r.text[:100])


def main():
    seen = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    nuevos = []
    for p in buscar():
        nombre = p.get("productName", "")
        if not any(k in nombre.lower() for k in KEYWORDS):
            continue
        if p["productId"] in seen or not disponible(p):
            continue
        nuevos.append(p)

    for p in nuevos:
        link = f"{BASE}/{p['linkText']}/p"
        avisar(f"🎄 ¡Ya subió! {p['productName']}\n{link}")
        seen.add(p["productId"])

    STATE.write_text(json.dumps(sorted(seen)))
    print(f"Revisado. Nuevos: {len(nuevos)}")


if __name__ == "__main__":
    main()
