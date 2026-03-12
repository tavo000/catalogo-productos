import requests
from bs4 import BeautifulSoup
import json
import time

base_url = "https://tuatiendaonline.com.ar"

productos = []
page = 1

headers = {
    "User-Agent": "Mozilla/5.0"
}

while True:

    url = f"{base_url}/productos/page/{page}/"
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        break

    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select(".item-product")

    if not cards:
        break

    print(f"Página {page} -> {len(cards)} productos")

    for card in cards:

        name_tag = card.select_one(".item-name")
        price_tag = card.select_one(".item-price")
        img_tag = card.select_one("img")
        link_tag = card.select_one("a")

        name = name_tag.text.strip() if name_tag else ""
        price = price_tag.text.strip() if price_tag else ""

        # -------- obtener imagen --------
        img = ""

        if img_tag:

            posibles = [
                img_tag.get("data-src"),
                img_tag.get("data-original"),
                img_tag.get("data-srcset"),
                img_tag.get("src")
            ]

            for p in posibles:
                if p and not p.startswith("data:image"):
                    img = p
                    break

            if " " in img:
                img = img.split(" ")[0]

            if img.startswith("//"):
                img = "https:" + img

            elif img.startswith("/"):
                img = base_url + img

        # -------- obtener link --------
        link = ""

        if link_tag:
            href = link_tag.get("href", "")
            if href.startswith("/"):
                link = base_url + href
            else:
                link = href

        # -------- obtener categoria --------
        categoria = "Otros"

        if link:
            try:
                r_prod = requests.get(link, headers=headers)
                soup_prod = BeautifulSoup(r_prod.text, "html.parser")

                breadcrumb = soup_prod.select(".breadcrumbs a")

                cats = []

                for b in breadcrumb:
                    txt = b.text.strip()

                    if txt.lower() != "inicio":
                        cats.append(txt)

                if cats:
                    categoria = " > ".join(cats)

            except:
                pass

        producto = {
            "name": name,
            "price": price,
            "image": img,
            "link": link,
            "category": categoria
        }

        productos.append(producto)

        print("OK:", name)

        time.sleep(0.3)

    page += 1


print("Total productos:", len(productos))

with open("productos.json", "w", encoding="utf8") as f:
    json.dump(productos, f, indent=2, ensure_ascii=False)

print("productos.json generado")