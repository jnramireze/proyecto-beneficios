from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://ww2.movistar.cl/app/club/"  # página pública Club Movistar

def parse_movistar(html:str):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    # Captura bloques con descuentos/palabras clave
    for b in soup.find_all(["div","section","article","li"]):
        text = b.get_text(" ", strip=True)
        if not text:
            continue
        text_low = text.lower()
        if any(kw in text_low for kw in ["dcto", "descuento", "canjea", "entradas", "uber", "mercado libre", "cinépolis", "melt", "accesorios movistar", "wetransport", "freepik", "perplexity"]):
            if 20 <= len(text) <= 400:
                comercio = text.split()[0][:60]
                data.append({
                    "Proveedor": "Movistar - Club Movistar",
                    "Categoría": "Promos/Descuentos",
                    "Comercio": comercio,
                    "Beneficio": text,
                    "Vigencia": "",
                    "Link": URL,
                    "Fuente": URL,
                    "Extraido_En": datetime.now().isoformat()
                })

    uniq = {d["Beneficio"]: d for d in data}
    return list(uniq.values())

