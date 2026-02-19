# scrapers/movistar.py
from bs4 import BeautifulSoup
from datetime import datetime

URLS = [
    "https://ww2.movistar.cl/app/club/",            # landing del club
    "https://www.movistar.cl/?club-movistar/beneficios/todos"  # listado "todos"
]

def parse_movistar(html: str):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Buscar elementos con descuentos/texto típico
    for b in soup.find_all(["div","section","article","li","a","span"]):
        text = b.get_text(" ", strip=True)
        if not text:
            continue
        low = text.lower()

        if any(kw in low for kw in [
            "dcto", "descuento", "canjea", "entradas", "cine", "uber",
            "mercado libre", "cinépolis", "melt", "accesorios movistar",
            "wetransport", "beneficios", "club movistar", "freepik", "perplexity"
        ]):
            if 20 <= len(text) <= 600:
                # Comercio aproximado
                title_tag = b.find(["h3","h2","strong","b"])
                comercio = title_tag.get_text(strip=True) if title_tag else text.split(" ")[0][:60]

                href = b.get("href", "")
                link = href if href.startswith("http") else ""

                data.append({
                    "Proveedor": "Movistar - Club Movistar",
                    "Categoría": "Promos/Descuentos",
                    "Comercio": comercio,
                    "Beneficio": text,
                    "Vigencia": "",
                    "Link": link,
                    "Fuente": "",
                    "Extraido_En": datetime.now().isoformat()
                })

    # Dedup por Beneficio
    uniq = {d["Beneficio"]: d for d in data}
    return list(uniq.values())
