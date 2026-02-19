from bs4 import BeautifulSoup
from datetime import datetime
import re
from scrapers.utils import looks_like_offer

# SOLO esta fuente pública (listado de beneficios/campañas)
URLS = [
    "https://sitiospublicos.bancochile.cl/personas/beneficios"
]

PCT = re.compile(r"\d+%")
AMT = re.compile(r"\$\s?\d{1,3}(?:[.,]\d{3})*")

def parse_single(html: str, source: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.find_all(["section","article","div","li","a"]):
        text = card.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue

        # Título probable
        title_tag = card.find(["h3","h2","strong","b"])
        comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

        # Link preferente del propio card si existe
        href = card.get("href", "")
        link = href if href.startswith("http") else source

        # Categoría por heading ancestro
        cat = "Beneficios"
        parent = card.find_parent(["section","div"])
        if parent:
            h = parent.find(["h2","h3"])
            if h and 2 <= len(h.get_text(strip=True)) <= 60:
                cat = h.get_text(strip=True)

        rows.append({
            "Proveedor": "Banco de Chile",
            "Categoría": cat,
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": link,
            "Fuente": source,
            "Extraido_En": datetime.now().isoformat()
        })
    # dedup
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in rows}
    return list(uniq.values())

def parse_all(html_map: dict):
    out = []
    for url, html in html_map.items():
        out += parse_single(html, url)
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
