from bs4 import BeautifulSoup
from datetime import datetime

# Si usaste utils.py:
from scrapers.utils import looks_like_offer

URL = "https://www.entel.cl/beneficios"  # catálogo público Club Entel

def parse_entel(html: str):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Buscamos bloques candidatos (secciones, artículos, tarjetas, etc.)
    candidates = soup.find_all(["section", "div", "article", "li", "a"])
    for c in candidates:
        text = c.get_text(" ", strip=True)

        # 🔴 FILTRO DE ACEPTACIÓN: descarta menús y textos genéricos
        if not looks_like_offer(text):
            continue

        # Deducir categoría por heading cercano (si existe)
        cat = "Beneficios"
        parent = c.find_parent(["section", "div"])
        if parent:
            h = parent.find(["h2", "h3"])
            if h and 2 <= len(h.get_text(strip=True)) <= 60:
                cat = h.get_text(strip=True)

        # Título/comercio: usa h3/h2/strong si existe; si no, corta el texto
        title_tag = c.find(["h3", "h2", "strong", "b"])
        titulo = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

        # Link: si la tarjeta tiene href, úsalo; si no, usa la landing
        a = c.find("a")
        href = a.get("href") if a else ""
        link = href if (href and href.startswith("http")) else URL

        data.append({
            "Proveedor": "Entel - Club Entel",
            "Categoría": cat,
            "Comercio": titulo,
            "Beneficio": text,
            "Vigencia": "",
            "Link": link,
            "Fuente": URL,
            "Extraido_En": datetime.now().isoformat()
        })

    # Deduplicar por Comercio+Beneficio
    uniq = {(d["Comercio"], d["Beneficio"]): d for d in data}
    return list(uniq.values())
