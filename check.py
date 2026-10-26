import json
import os
import pathlib

import requests

BASE = "https://www.maquillajetrendyshop.com"
SEARCH_TERM = "calendario adviento"
KEYWORDS = ["adviento"]  # palabra que debe estar en el nombre
STATE = pathlib.Path("seen.json")

TG_USER = os.environ["TG_USER"]  # tu usuario de Telegram, ej: @miusuario


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
        "https://api.callmebot.com/start.php",
        params={"user": TG_USER, "text": texto, "lang": "es-US-Standard-A", "rpt": 2},
        timeout=60,
    )
    print("Llamada:", r.status_code, r.text[:150])


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
        print("Encontrado:", p["productName"], f"{BASE}/{p['linkText']}/p")
        avisar("Atención. Ya subió el calendario de adviento en la tienda Trendy. Entra ahora a comprarlo.")
        seen.add(p["productId"])

    STATE.write_text(json.dumps(sorted(seen)))
    print(f"Revisado. Nuevos: {len(nuevos)}")


if __name__ == "__main__":
    main()
