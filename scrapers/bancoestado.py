# scrapers/bancoestado.py
from bs4 import BeautifulSoup
from datetime import datetime
import re
from scrapers.utils import looks_like_offer

# Lista blanca de páginas oficiales de beneficios BancoEstado
URLS = [
    # Catálogo de "Bieeeneficios" (tu link)
    "https://start.bancoestado.cl/content/bancoestado-public/cl/es/home/home/todosuma---bancoestado-personas/bieneeeneficios-que-te-vienen-bien---bancoestado-personas.html",
    # Fallback: landing general "Todos Beneficios"
    "https://start.bancoestado.cl/content/bancoestado-public/cl/es/home/home/todosuma---bancoestado-personas/todos-beneficios.html",
]

# Patrones auxiliares (opcional, normalizer también los procesa)
PCT = re.compile(r"\d+%")
AMT = re.compile(r"\$\s?\d{1,3}(?:[.,]\d{3})*")

def parse_single(html: str, source: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    # Buscamos tarjetas/bloques posibles de beneficios
    for el in soup.find_all(["section", "article", "div", "li", "a", "span"]):
        text = el.get_text(" ", strip=True)
        if not looks_like_offer(text):
            continue

        # Comercio/título (si existe un Hx fuerte, úsalo)
        title_tag = el.find(["h3", "h2", "strong", "b"])
        comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

        # Link preferente del propio bloque si lo hay
        href = ""
        if hasattr(el, "name") and el.name == "a" and el.has_attr("href"):
            href = el["href"]
        link = href if href.startswith("http") else source

        # Categoría aproximada por heading ancestro
        cat = "Beneficios"
        parent = el.find_parent(["section", "div"])
        if parent:
            h = parent.find(["h2", "h3"])
            if h and 2 <= len(h.get_text(strip=True)) <= 60:
                cat = h.get_text(strip=True)

        rows.append({
            "Proveedor": "BancoEstado",
            "Categoría": cat,
            "Comercio": comercio,
            "Beneficio": text,
            "Vigencia": "",
            "Link": link,
            "Fuente": source,
            "Extraido_En": datetime.now().isoformat()
        })

    # Deduplicación local por (Comercio, Beneficio)
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in rows}
    return list(uniq.values())

def parse_all(html_map: dict):
    """
    html_map: {url: html}
    """
    out = []
    for url, html in html_map.items():
        out += parse_single(html, url)
    # Dedup global
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
