import requests
from bs4 import BeautifulSoup
import json
import os

URLS = [
    "https://simple.ripley.com.pe/jugueteria-y-bebes/jugueteria/pokemon?brand=POKEMON+TCG&page=1",
    "https://simple.ripley.com.pe/jugueteria-y-bebes/jugueteria/pokemon?brand=POKEMON+TCG&page=2"
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0 Safari/537.36"
    )
}

FILE = "productos.json"


def obtener_productos():
    productos = {}

    for url in URLS:
        print(f"Revisando: {url}")

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        respuesta.raise_for_status()

        soup = BeautifulSoup(
            respuesta.text,
            "html.parser"
        )

        for enlace in soup.find_all("a", href=True):

            nombre = enlace.get_text(
                " ",
                strip=True
            )

            href = enlace["href"].strip()

            if not nombre or not href:
                continue

            if href.startswith("/"):
                href = "https://simple.ripley.com.pe" + href

            if (
                "simple.ripley.com.pe" in href
                and "pokemon" in nombre.lower()
            ):
                productos[href] = {
                    "nombre": nombre,
                    "url": href
                }

    return productos


productos_actuales = obtener_productos()

print(f"Productos encontrados: {len(productos_actuales)}")


# PRIMERA EJECUCIÓN
# Solo crea la línea base.
# NO genera ninguna alerta.
if not os.path.exists(FILE):

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(
            productos_actuales,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Línea base creada.")
    print("No se enviará ninguna alerta.")


# EJECUCIONES POSTERIORES
else:

    with open(FILE, "r", encoding="utf-8") as f:
        productos_anteriores = json.load(f)

    nuevos = [
        producto
        for url, producto in productos_actuales.items()
        if url not in productos_anteriores
    ]

    if nuevos:

        print("🚨 PRODUCTOS NUEVOS DETECTADOS:")

        for producto in nuevos:
            print(f"- {producto['nombre']}")
            print(f"  {producto['url']}")

    else:

        print("Sin productos nuevos.")

    # Actualizar la línea base
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(
            productos_actuales,
            f,
            ensure_ascii=False,
            indent=2
        )
