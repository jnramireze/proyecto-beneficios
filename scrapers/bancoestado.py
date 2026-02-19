from bs4 import BeautifulSoup
from datetime import datetime

# Páginas públicas donde BancoEstado publica beneficios
URLS = [
    # Catálogo “Todos Beneficios” (tarjetas, categorías, campañas)
    "https://start.bancoestado.cl/content/bancoestado-public/cl/es/home/home/todosuma---bancoestado-personas/todos-beneficios.html",
    # Mini app de Beneficios en la Súper App Rutpay (landing pública)
    "https://www.rutpay.cl/content/bancoestado-public/cl/es/home/inicio---rutpay-bancoestado/beneficios---rutpay-bancoestado.html",
    # (Opcional) Ejemplos de fichas individuales para extraer formato/estructura
    "https://start.bancoestado.cl/content/bancoestado-public/cl/es/home/home/todosuma---bancoestado-personas/todos-beneficios/examedi--cuidado-integral-de-tu-salud---beneficios-bancoestado.html",
    "https://start.bancoestado.cl/content/bancoestado-public/cl/es/home/home/todosuma---bancoestado-personas/todos-beneficios/club-softys.html"
]

def _norm_row(categoria, comercio, beneficio, link, fuente):
    return {
        "Proveedor": "BancoEstado",
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

    # 1) Tarjetas/bloques con textos de descuento y vigencia
    for block in soup.find_all(["section","article","div","li","a"]):
        text = block.get_text(" ", strip=True)
        if not text:
            continue
        low = text.lower()

        if any(k in low for k in ["% dto", "descuento", "beneficio", "vigencia", "cuotas sin interés", "promoción"]):
            if 25 <= len(text) <= 700:
                title_tag = block.find(["h3","h2","strong","b"])
                comercio = title_tag.get_text(strip=True) if title_tag else text.split(".")[0][:80]

                href = ""
                if hasattr(block, "name") and block.name == "a" and block.has_attr("href"):
                    href = block["href"]
                link = href if href.startswith("http") else source

                cat = "Beneficios"
                section = block.find_parent(["section","div"])
                if section:
                    hsec = section.find(["h2","h3"])
                    if hsec and 2 <= len(hsec.get_text(strip=True)) <= 60:
                        cat = hsec.get_text(strip=True)

                rows.append(_norm_row(cat, comercio, text, link, source))

    uniq = {(r["Comercio"], r["Beneficio"]): r for r in rows}
    return list(uniq.values())

def parse_all(html_map: dict):
    out = []
    for url, html in html_map.items():
        out += parse_single(html, url)
    uniq = {(r["Proveedor"], r["Comercio"], r["Beneficio"]): r for r in out}
    return list(uniq.values())
