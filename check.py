import json
import os
import pathlib
import urllib.parse

import requests

BASE = "https://www.maquillajetrendyshop.com"
SEARCH_TERM = "calendario adviento"
KEYWORDS = ["adviento"]  # palabra que debe estar en el nombre
STATE = pathlib.Path("seen.json")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
}

TG_USER = os.environ["TG_USER"]  # tu usuario de Telegram, ej: @miusuario


def buscar():
    q = urllib.parse.quote(SEARCH_TERM)
    urls = [
        f"{BASE}/api/io/_v/api/intelligent-search/product_search/?query={q}&locale=es-CO",
        f"{BASE}/api/catalog_system/pub/products/search/{q}?map=ft",
        f"{BASE}/api/catalog_system/pub/products/search?ft={q}",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            print("Probando:", url, "->", r.status_code)
            if r.status_code != 200:
                print("   Respuesta:", r.text[:200])
                continue
            data = r.json()
            return data["products"] if isinstance(data, dict) else data
        except Exception as e:
            print("   Fallo:", e)
    raise SystemExit("Ninguna forma de consultar la tienda funcion\u00f3")


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
