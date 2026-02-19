from bs4 import BeautifulSoup
from datetime import datetime

# Páginas públicas donde Banco de Chile lista beneficios/promos.
URLS = [
    # Catálogo general de beneficios (sitio público)
    "https://sitiospublicos.bancochile.cl/personas/beneficios",
    # Campañas (ej.: Back To School 2026 / “Vuelta a clases”)
    "https://sitiospublicos.bancochile.cl/personas/beneficios/campanas/bts-2026",
    # Home (a veces hay módulos con promos fechadas)
    "https://www.bancochile.cl/",
    # Programa Travel (sección beneficios/panoramas/ofertas)
    "https://www.travel.cl/"
]

def _norm_row(categoria, comercio, beneficio, link, fuente):
    return {
        "Proveedor": "Banco de Chile",
        "Categoría": categoria or "Beneficios",
        "Comercio": (comercio or "").strip()[:120],
        "Beneficio": (beneficio or "").strip(),
        "Vigencia": "",
        "Link": link,
        "Fuente": fuente,
        "Extraido_En": datetime.now().isoformat()
    }

def parse_single(html: str, source: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []

    # 1) Bloques “tarjeta”/enlaces con textos de descuento
    for block in soup.find_all(["section","article","div","li","a"]):
        text = block.get_text(" ", strip=True)
        if not text:
            continue
        low = text.lower()

        # Heurística de beneficios: “dto”, “descuento”, “cuotas sin interés”, “dólares‑premio”
        if any(k in low for k in ["dto", "descuento", "cuotas sin interés", "dólares-premio", "cashback", "promoción", "beneficio"]):
            # Evita textos gigantes de layout
            if 25 <= len(text) <= 600:
                # comercio suele estar en el título de la tarjeta/enlace
                title_tag = block.find(["h3","h2","strong","b"])
                comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

                # link si existe
                href = ""
                if hasattr(block, "name") and block.name == "a" and block.has_attr("href"):
                    href = block["href"]
                link = href if href.startswith("http") else source

                # categoría aproximada por contexto
                cat = "Beneficios"
                section = block.find_parent(["section","div"])
                if section:
                    hsec = section.find(["h2","h3"])
                    if hsec and 2 <= len(hsec.get_text(strip=True)) <= 60:
                        cat = hsec.get_text(strip=True)

                rows.append(_norm_row(cat, comercio, text, link, source))

    # 2) Deduplicación por Comercio+Beneficio
    uniq = {(r["Comercio"], r["Beneficio"]): r for r in rows}
    return list(uniq.values())

def parse_all(html_map: dict):
    """
    html_map = {url: html}
    """
    out = []
    for url, html in html_map.items():
        out += parse_single(html, url)
    # Dedupe global
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
